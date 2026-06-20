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


def dispatch_pick(
    pick: dict[str, Any],
    *,
    dry_run: bool = False,
    mode: str = "railway_fbe",
) -> dict[str, Any]:
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
    if not dry_run and mode == "railway_fbe":
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

    receipt = dispatch_pick(pick, dry_run=args.dry_run, mode=args.mode)

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
