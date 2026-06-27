#!/usr/bin/env python3
"""Dispatch picked competitor-1000 plan to FORGE on cloud (Railway FBE) — not Mac body."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from forge_cloud_env_load_v1 import load_cloud_env  # noqa: E402
from forge_mvp_lib_v1 import persist_work_order  # noqa: E402
from forge_task_graph_emit_v01 import emit_for_pick  # noqa: E402
from portfolio_competitor_pick_lib import enrich_pick, load_registry, phase_order, pick_backlog_plans, resolve_stack  # noqa: E402

DRAIN_SSOT = ROOT / "data" / "secondary-cloud-forge-run-next-100-v1.json"


def _cloud_sec_id_for_registry_plan(registry_plan_id: str) -> str | None:
    """Map sa-mkt-0001 → CLOUD-SEC-001 via secondary Cloud Forge Run SSOT."""
    if not DRAIN_SSOT.is_file():
        return None
    try:
        doc = json.loads(DRAIN_SSOT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    rid = str(registry_plan_id or "").strip()
    for row in doc.get("plans") or []:
        if str(row.get("maps_registry") or "") == rid:
            return str(row.get("id") or "") or None
    return None


def _use_evidence_slice(pick: dict[str, Any]) -> bool:
    """T0 competitor evidence plans use cloud_worker_dispatch — not W5 motor_verify chain."""
    tier = str(pick.get("tier") or pick.get("sa_tier") or "").upper()
    plan_id = str(pick.get("id") or "")
    if tier == "T0" and plan_id.startswith("sa-mkt-"):
        return _cloud_sec_id_for_registry_plan(plan_id) is not None
    return False


def _dispatch_evidence_slice(pick: dict[str, Any], *, dry_run: bool) -> dict[str, Any]:
    from cloud_worker_dispatch_v1 import dispatch  # noqa: WPS433

    cloud_id = _cloud_sec_id_for_registry_plan(str(pick.get("id") or ""))
    if not cloud_id:
        return {"ok": False, "error": "cloud_sec_mapping_missing", "plan_id": pick.get("id")}
    row = dispatch(plan_id=cloud_id, dry_run=dry_run)
    return {
        "schema": "portfolio-competitor-forge-dispatch-v1",
        "ok": bool(row.get("ok")) or dry_run,
        "dispatch_lane": "cloud_worker_evidence_slice",
        "registry_plan_id": pick.get("id"),
        "cloud_sec_plan_id": cloud_id,
        "dry_run": dry_run,
        "reason": "T0 sa-mkt uses cloud_worker_dispatch — W5 motor_verify requires Mac ~/.sina receipts absent on Railway",
        "cloud_dispatch": row,
        "competitor_plan": {
            "plan_id": pick.get("id"),
            "competitor": pick.get("competitor"),
            "workstream": pick.get("workstream"),
            "execution_mode": "CLOUD_ONLY",
        },
        "mac_build_forbidden": True,
    }


def dispatch_pick(
    pick: dict[str, Any],
    *,
    dry_run: bool = False,
    mode: str = "railway_fbe",
    full_motor: bool = False,
) -> dict[str, Any]:
    if not full_motor and _use_evidence_slice(pick):
        return _dispatch_evidence_slice(pick, dry_run=dry_run)
    if not dry_run:
        load_cloud_env(apply=True)
    graph_row = emit_for_pick(pick)
    forge = pick["forge"]
    forge_context = {
        "plan_id": pick.get("id"),
        "run_id": graph_row["run_id"],
        "task_graph_path": graph_row["path"],
        "stack": pick.get("stack"),
        "stack_key": pick.get("stack_key"),
        "competitor": pick.get("competitor"),
        "workstream": pick.get("workstream"),
        "phase": pick.get("phase"),
        "prompt_abs": pick.get("prompt_abs"),
        "execution_mode": "CLOUD_ONLY",
        "preview_url": None,
    }
    try:
        forge_context["task_graph"] = json.loads(Path(graph_row["path"]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    persist_work_order(forge_context)
    sys.path.insert(0, str(ROOT / "scripts" / "fbe" / "lib"))
    from cloud_adapter_v1 import submit_job  # noqa: WPS433

    receipt = submit_job(
        template_id=forge["template_id"],
        work_order_id=str(forge["work_order_id"]),
        tenant=str(forge["tenant"]),
        bay_slug=str(forge["bay_slug"]),
        dry_run=dry_run,
        mode=mode,
        run_mode=str(forge["run_mode"]),
        forge_context=forge_context,
    )
    receipt["competitor_plan"] = forge_context
    receipt["task_graph_path"] = graph_row["path"]
    receipt["run_id"] = graph_row["run_id"]
    receipt["forge_loop"] = forge.get("stack_loop")
    receipt["mac_build_forbidden"] = True
    if not dry_run and mode == "railway_fbe" and receipt.get("submit_mode") != "in_process":
        env = load_cloud_env(apply=False)
        if not env.get("cloud_ready"):
            receipt["ok"] = False
            receipt["error"] = "cloud_worker_url_missing"
            receipt["for_founder"] = {
                "show_this": "FORGE cloud worker URL is not configured. Mac cannot build — set FBE_CLOUD_WORKER_URL in ~/.sourcea-secrets.",
            }
    return receipt


def main() -> int:
    p = argparse.ArgumentParser(description="FORGE cloud dispatch for competitor plan pick")
    p.add_argument("--stack", required=True)
    p.add_argument("--plan-id", default="", help="Specific plan id; default = next pick")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument(
        "--full-motor",
        action="store_true",
        help="Use W5 FORGE motor on Railway (revenue lane) — not evidence-slice stub",
    )
    p.add_argument("--mode", default="railway_fbe", choices=("railway_fbe", "local_docker", "mono_mirror"))
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    stack_key = resolve_stack(args.stack)
    registry = load_registry(stack_key)

    if args.plan_id:
        raw = next((pl for pl in registry.get("plans") or [] if pl.get("id") == args.plan_id), None)
        if not raw:
            print(f"Plan not found: {args.plan_id}", file=sys.stderr)
            return 1
        pick = enrich_pick(stack_key, raw, registry)
    else:
        backlog = pick_backlog_plans(
            registry.get("plans") or [],
            phases=phase_order(registry),
            tiers=("T0", "T1", "T2", "T3"),
            limit=1,
        )
        if not backlog:
            print("No backlog", file=sys.stderr)
            return 1
        pick = enrich_pick(stack_key, backlog[0], registry)

    receipt = dispatch_pick(pick, dry_run=args.dry_run, mode=args.mode, full_motor=args.full_motor)

    if args.json:
        print(json.dumps(receipt, indent=2))
    else:
        ok = receipt.get("ok")
        print(f"FORGE dispatch {'DRY-RUN' if args.dry_run else 'LIVE'} — ok={ok}")
        print(f"plan={pick.get('id')} stack={pick.get('stack')} competitor={pick.get('competitor')}")
        print(f"mode={receipt.get('submit_mode')} run_mode={receipt.get('run_mode')}")
        if not ok:
            rr = receipt.get("run_result") or {}
            print(f"error={rr.get('error') or receipt.get('error')}")

    return 0 if receipt.get("ok") or args.dry_run else 1


if __name__ == "__main__":
    raise SystemExit(main())
