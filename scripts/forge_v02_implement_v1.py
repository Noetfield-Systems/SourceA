#!/usr/bin/env python3
"""Forge v0.2 cloud implement — task graph + router + critic → receipt on cloud volume."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
IMPLEMENT_SIG = "cloud_implement_receipt_pass"
RUN_DETAIL_WORKSTREAMS = frozenset({"ws-run"})
EVIDENCE_WORKSTREAMS = frozenset({"ws-onboard", "ws-ux", "ws-pricing", "ws-integrate"})
SCORING_OVERLAY_REL = "receipts/forge_v0.2/scoring_overlay.json"


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
                    "maps_registry": p.get("maps_registry"),
                },
                "inputs": {
                    "action": p.get("cloud_action") or p.get("title"),
                    "workstream": p.get("workstream"),
                    "": p.get(""),
                    "plane": p.get("plane"),
                    "maps_registry": p.get("maps_registry"),
                },
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
        "": str(meta.get("") or inputs.get("") or "Trigger.dev"),
        "workstream": str(meta.get("workstream") or inputs.get("workstream") or "ws-run"),
        "title": action or f"Implement {plan_id}",
        "tier": meta.get("tier"),
        "forge": {"tenant": "forge"},
    }


def implement_receipt_path(plan_id: str, *, root: Path | None = None) -> Path:
    base = root or ROOT
    return base / "receipts" / "cloud-implement" / f"{plan_id}.json"


def is_mac_control_blueprint(row: dict[str, Any]) -> bool:
    """Mac observe-only lane — never cloud real-ship (INCIDENT-038)."""
    pid = str(row.get("id") or "")
    if pid.startswith("MAC-CTL-"):
        return True
    inputs = row.get("inputs") if isinstance(row.get("inputs"), dict) else {}
    plane = str(inputs.get("plane") or row.get("plane") or "")
    ws = str(inputs.get("workstream") or "")
    return plane == "mac_control" or ws == "mac_control"


def is_real_shippable_blueprint(row: dict[str, Any]) -> bool:
    """True when ranked blueprint can produce a real cloud artifact."""
    if is_mac_control_blueprint(row):
        return False
    inputs = row.get("inputs") if isinstance(row.get("inputs"), dict) else {}
    ws = str(inputs.get("workstream") or "")
    return ws in RUN_DETAIL_WORKSTREAMS or ws in EVIDENCE_WORKSTREAMS


def is_real_shippable_plan(plan_id: str, *, root: Path | None = None) -> bool:
    """True when plan can produce a real cloud artifact (not mac_control / unknown ws)."""
    if plan_id.startswith("MAC-CTL-"):
        return False
    row = load_plan_row(plan_id, root=root)
    if not row:
        return False
    meta = row.get("metadata") if isinstance(row.get("metadata"), dict) else {}
    inputs = row.get("inputs") if isinstance(row.get("inputs"), dict) else {}
    bp = {
        "id": plan_id,
        "inputs": inputs,
        "plane": inputs.get("plane") or row.get("plane"),
        "workstream": meta.get("workstream") or inputs.get("workstream"),
    }
    return is_real_shippable_blueprint(bp)


def already_implemented_ids(*, root: Path | None = None) -> set[str]:
    base = root or ROOT
    seen: set[str] = set()
    overlay = _read_json(base / SCORING_OVERLAY_REL)
    for pid in overlay.get("already_implemented_plan_ids") or []:
        if pid:
            seen.add(str(pid))
    impl_dir = base / "receipts" / "cloud-implement"
    if impl_dir.is_dir():
        for path in impl_dir.glob("*.json"):
            try:
                row = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if row.get("status") == "PASS" and row.get("implement_mode") == "real":
                seen.add(str(row.get("plan_id") or path.stem))
    return seen


def _router_has_stub(router_result: dict[str, Any]) -> bool:
    for r in router_result.get("results") or []:
        if r.get("stub"):
            return True
    return False


def _ship_real_artifact(
    pid: str,
    pick: dict[str, Any],
    plan_row: dict[str, Any],
    *,
    root: Path,
    worker_base: str,
) -> dict[str, Any] | None:
    """Ship real cloud artifact for supported workstreams."""
    ws = str(pick.get("workstream") or "")
    if ws in RUN_DETAIL_WORKSTREAMS:
        from implement_run_detail_slice_v1 import ship_run_detail_for_plan  # noqa: WPS433

        return ship_run_detail_for_plan(
            pid,
            root=root,
            =str(pick.get("") or "Trigger.dev"),
            workstream=ws,
            worker_base=worker_base,
        )
    if ws in EVIDENCE_WORKSTREAMS:
        from implement__evidence_slice_v1 import ship_evidence_for_plan  # noqa: WPS433

        return ship_evidence_for_plan(pid, plan_row, root=root, worker_base=worker_base)
    return None


def run_forge_v02_implement(
    plan_id: str,
    *,
    root: Path | None = None,
    write_output: bool = True,
    bay: str = "forge-bay",
) -> dict[str, Any]:
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
    if not pid or not plan_row:
        raise ValueError(f"plan_not_found:{pid}")

    pick = plan_to_pick(pid, plan_row)
    worker_base = os.environ.get("FBE_CLOUD_WORKER_URL", "").strip().rstrip("/")
    if not worker_base:
        worker_base = "https://sourcea-fbe-runner-production.up.railway.app"

    run_id = new_run_id(pid)
    graph = build_task_graph(pick=pick, run_id=run_id)
    router_result = execute_graph(graph=graph, bay=bay)
    critic = run_critic_loop(graph=graph, router_result=router_result, pick=pick, bay=bay)

    artifact = _ship_real_artifact(pid, pick, plan_row, root=base, worker_base=worker_base)
    has_stub = _router_has_stub(router_result)
    if artifact and artifact.get("ok"):
        implement_mode = "real"
        preview_url = str(artifact.get("preview_url") or "")
        artifact_paths = [str(artifact.get("artifact_path") or "")]
    else:
        implement_mode = "structural_stub"
        preview_url = f"{worker_base}/receipts/cloud-implement/{pid}.json"
        artifact_paths = []

    if implement_mode == "real":
        status = "PASS"
        verdict = "PASS"
    else:
        status = "FAIL"
        verdict = "FAIL"

    telemetry_impl = f"Implement: {pid} {implement_mode} {status}"
    if implement_mode == "structural_stub" and has_stub:
        telemetry_impl += " (stub router — no artifact)"

    receipt = {
        "schema": "forge-v0.2-implement-receipt",
        "at": _now(),
        "architecture": "A",
        "plan_id": pid,
        "status": status,
        "verdict": verdict,
        "implement_mode": implement_mode,
        "telemetry_line": telemetry_impl,
        "preview_url": preview_url,
        "artifact_paths": artifact_paths,
        "run_id": run_id,
        "intent": (graph.get("prompt") or {}).get("intent"),
        "action": pick.get("title"),
        "workstream": pick.get("workstream"),
        "": pick.get(""),
        "artifact": artifact,
        "router": {
            "ok": router_result.get("ok"),
            "tasks_run": router_result.get("tasks_run"),
            "cost_usd_total": router_result.get("cost_usd_total"),
            "has_stub": has_stub,
            "results": router_result.get("results"),
        },
        "critic": {
            "ok": critic.get("ok"),
            "final_verdict": critic.get("final_verdict"),
            "replans": critic.get("replans"),
        },
        "implementation_signature": IMPLEMENT_SIG if status == "PASS" else None,
        "receipt_url": f"/receipts/cloud-implement/{pid}.json",
        "ok": status == "PASS",
    }

    if write_output:
        _write_json(implement_receipt_path(pid, root=base), receipt)
        if status == "PASS" and implement_mode == "real":
            from forge_v02_github_v1 import append_scoring_overlay  # noqa: WPS433
            from forge_v02_status_v1 import write_implement_index  # noqa: WPS433

            append_scoring_overlay(pid, root=base)
            write_implement_index(root=base)

    return receipt


def _pick_implement_plan_ids(top: list[dict[str, Any]], *, implement_top_n: int, root: Path) -> list[str]:
    """Pick plan ids by rank order; skip already real-implemented."""
    want = max(1, implement_top_n)
    done = already_implemented_ids(root=root)
    picked: list[str] = []
    for row in top:
        pid = str(row.get("id") or "")
        if not pid or pid in done or not is_real_shippable_plan(pid, root=root):
            continue
        picked.append(pid)
        if len(picked) >= want:
            break
    return picked


def run_forge_v02_run_and_implement(
    *,
    root: Path | None = None,
    write_output: bool = True,
    implement_top_n: int = 1,
    **github_kwargs: Any,
) -> dict[str, Any]:
    import sys

    sys.path.insert(0, str(ROOT / "scripts"))
    from forge_v02_github_v1 import run_forge_v02_from_github  # noqa: WPS433

    base = root or ROOT
    forge_result = run_forge_v02_from_github(write_output=write_output, root=base, **github_kwargs)
    top = forge_result.get("top_20") or []
    implement_results: list[dict[str, Any]] = []
    for pid in _pick_implement_plan_ids(top, implement_top_n=implement_top_n, root=base):
        try:
            impl = run_forge_v02_implement(pid, root=base, write_output=write_output)
            implement_results.append(impl)
        except Exception as exc:
            implement_results.append({"plan_id": pid, "ok": False, "error": str(exc), "status": "FAIL"})

    impl_lines = [str(r.get("telemetry_line") or f"{r.get('plan_id')} FAIL") for r in implement_results]
    return {
        "schema": "forge-v0.2-run-and-implement",
        "at": _now(),
        "architecture": "A",
        "ok": all(r.get("status") == "PASS" for r in implement_results if r.get("plan_id")),
        "forge": forge_result,
        "telemetry_line": forge_result.get("telemetry_line"),
        "implement_telemetry": impl_lines,
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
        print(row.get("implement_mode"), row.get("status"), row.get("plan_id"))
    return 0 if row.get("status") == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
