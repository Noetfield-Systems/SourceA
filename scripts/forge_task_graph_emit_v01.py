#!/usr/bin/env python3
"""Emit forge-task-graph-v0.1 from competitor pick (all stacks)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from forge_mvp_lib_v1 import DEFAULT_BAY, build_task_graph, new_run_id, task_graph_path  # noqa: E402
from portfolio_competitor_pick_lib import enrich_pick, load_registry, phase_order, pick_backlog_plans, resolve_stack  # noqa: E402


def emit_for_pick(pick: dict, *, run_id: str = "", bay: str = DEFAULT_BAY) -> dict:
    graph = build_task_graph(pick=pick, run_id=run_id or new_run_id(str(pick.get("id") or "")))
    out = task_graph_path(graph["run_id"], bay)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(graph, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "path": str(out), "run_id": graph["run_id"], "graph": graph}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--stack", default="")
    ap.add_argument("--pick-json", default="", help="Path to pick JSON array from pick-portfolio-competitor-plan")
    ap.add_argument("--plan-id", default="")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--bay", default=DEFAULT_BAY)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.pick_json:
        picks = json.loads(Path(args.pick_json).read_text(encoding="utf-8"))
        pick = picks[0] if isinstance(picks, list) else picks
    elif args.stack:
        stack_key = resolve_stack(args.stack)
        registry = load_registry(stack_key)
        if args.plan_id:
            raw = next((p for p in registry.get("plans") or [] if p.get("id") == args.plan_id), None)
            if not raw:
                print(f"plan not found: {args.plan_id}", file=sys.stderr)
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
                print("no backlog", file=sys.stderr)
                return 1
            pick = enrich_pick(stack_key, backlog[0], registry)
    else:
        print("Provide --stack or --pick-json", file=sys.stderr)
        return 1

    row = emit_for_pick(pick, run_id=args.run_id, bay=args.bay)
    if args.json:
        print(json.dumps({k: v for k, v in row.items() if k != "graph"}, indent=2))
    else:
        print(f"{row['run_id']}\t{row['path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
