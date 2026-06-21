#!/usr/bin/env python3
"""Forge v0.2 cloud implement — task graph + router + critic → receipt on cloud volume."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DRAIN_PATH = ROOT / "data" / "secondary-cloud-drain-next-100-v1.json"
PLANS_DIR = ROOT / "plans"
IMPLEMENT_SIG = "cloud_implement_receipt_pass"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def load_plan_row(plan_id: str, *, root: Path | None = None) -> dict[str, Any]:
    """Load plan from GitHub-shaped plans/ JSON or secondary-cloud-drain SSOT."""
    base = root or ROOT
    plan_path = base / "plans" / f"{plan_id}.json"
    if plan_path.is_file():
        row = _read_json(plan_path)
        if row:
            return row
    drain = _read_json(base / "data" / "secondary-cloud-drain-next-100-v1.json")
    for p in drain.get("plans") or []:
        if str(p.get("id") or "") == plan_id:
            return {
                "plan_id": plan_id,
                "metadata": {
                    "workstream": p.get("workstream"),
                    "": p.get(""),
                    "tier": p.get("tier"),
                },
                "inputs": {"action": p.get("cloud_action") or p.get("title")},
            }
    return {}


def plan_to_pick(plan_id: str, plan_row: dict[str, Any]) -> dict[str, Any]:
    meta = plan_row.get("metadata") if isinstance(plan_row.get("metadata"), dict) else {}
    inputs = plan_row.get("inputs") if isinstance(plan_row.get("inputs"), dict) else {}
    action = str(inputs.get("action") or "")
    return {
        "id": plan_id,
        "stack": "sourcea",
        "stack_key": "sourcea",
        "": str(meta.get("") or "Trigger.dev"),
        "workstream": str(meta.get("workstream") or inputs.get("workstream") or "ws-run"),
        "title": action or f"Implement {plan_id}",
        "tier": meta.get("tier"),
        "forge": {"tenant": "forge"},
    }


def implement_receipt_path(plan_id: str, *, root: Path | None = None) -> Path:
    base = root or ROOT
    return base / "receipts" / "cloud-implement" / f"{plan_id}.json"


def run_forge_v02_implement(
    plan_id: str,
    *,
    root: Path | None = None,
    write_output: bool = True,
    bay: str = "forge-bay",
) -> dict[str, Any]:
    """Execute implement slice for one CLOUD-SEC / MAC-CTL plan on cloud."""
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from forge_critic_loop_v01 import run_critic_loop  # noqa: WPS433
    from forge_mvp_lib_v1 import build_task_graph, new_run_id  # noqa: WPS433
    from forge_router_execute_v01 import execute_graph  # noqa: WPS433

    base = root or ROOT
    pid = str(plan_id or "").strip()
    if not pid:
        raise ValueError("plan_id_required")

    plan_row = load_plan_row(pid, root=base)
    if not plan_row:
        raise ValueError(f"plan_not_found:{pid}")

    pick = plan_to_pick(pid, plan_row)
    run_id = new_run_id(pid)
    graph = build_task_graph(pick=pick, run_id=run_id)
    router_result = execute_graph(graph=graph, bay=bay)
    critic = run_critic_loop(graph=graph, router_result=router_result, pick=pick, bay=bay)

    verdict = "PASS" if critic.get("ok") else "FAIL"
    worker_base = os.environ.get("FBE_CLOUD_WORKER_URL", "").strip().rstrip("/")
    if not worker_base:
        worker_base = "https://sourcea-fbe-runner-production.up.railway.app"
    preview_url = f"{worker_base}/receipts/cloud-implement/{pid}.json"

    receipt = {
        "schema": "forge-v0.2-implement-receipt",
        "at": _now(),
        "architecture": "A",
        "plan_id": pid,
        "status": verdict,
        "verdict": verdict,
        "preview_url": preview_url,
        "run_id": run_id,
        "intent": (graph.get("prompt") or {}).get("intent"),
        "action": pick.get("title"),
        "workstream": pick.get("workstream"),
        "": pick.get(""),
        "router": {
            "ok": router_result.get("ok"),
            "tasks_run": router_result.get("tasks_run"),
            "cost_usd_total": router_result.get("cost_usd_total"),
        },
        "critic": {
            "ok": critic.get("ok"),
            "final_verdict": critic.get("final_verdict"),
            "replans": critic.get("replans"),
        },
        "implementation_signature": IMPLEMENT_SIG if verdict == "PASS" else None,
        "receipt_url": f"/receipts/cloud-implement/{pid}.json",
    }

    if write_output:
        _write_json(implement_receipt_path(pid, root=base), receipt)
        _append_implement_to_scoring_ssot(pid, root=base)

    return receipt


def _append_implement_to_scoring_ssot(plan_id: str, *, root: Path) -> None:
    """Mark PASS implement plans as already-have for next Forge run."""
    ssot_path = root / "data" / "forge-scoring-ssot-v01.json"
    ssot = _read_json(ssot_path)
    if not ssot:
        return
    ids = list(ssot.get("already_implemented_plan_ids") or [])
    sigs = list(ssot.get("already_implemented_signatures") or [])
    if plan_id not in ids:
        ids.append(plan_id)
    if IMPLEMENT_SIG not in sigs:
        sigs.append(IMPLEMENT_SIG)
    ssot["already_implemented_plan_ids"] = ids
    ssot["already_implemented_signatures"] = sigs
    _write_json(ssot_path, ssot)


def run_forge_v02_run_and_implement(
    *,
    root: Path | None = None,
    write_output: bool = True,
    implement_top_n: int = 1,
    **github_kwargs: Any,
) -> dict[str, Any]:
    """Chain: Forge v0.2 rank → implement top[0..n-1]."""
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from forge_v02_github_v1 import run_forge_v02_from_github  # noqa: WPS433

    forge_result = run_forge_v02_from_github(write_output=write_output, root=root, **github_kwargs)
    top = forge_result.get("top_20") or []
    implement_results: list[dict[str, Any]] = []
    for row in top[: max(1, implement_top_n)]:
        pid = str(row.get("id") or "")
        if not pid:
            continue
        try:
            impl = run_forge_v02_implement(pid, root=root, write_output=write_output)
            implement_results.append(impl)
        except Exception as exc:
            implement_results.append({"plan_id": pid, "ok": False, "error": str(exc)})

    return {
        "schema": "forge-v0.2-run-and-implement",
        "at": _now(),
        "architecture": "A",
        "forge": forge_result,
        "telemetry_line": forge_result.get("telemetry_line"),
        "implement_results": implement_results,
        "implement_count": len(implement_results),
    }


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--plan-id", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_forge_v02_implement(args.plan_id)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("status"), row.get("plan_id"))
    return 0 if row.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
