#!/usr/bin/env python3
"""Forge critic loop — T6 evaluate + meta replan (max 2)."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from forge_mvp_lib_v1 import DEFAULT_BAY, append_trace, build_task_graph, load_router_rules, now_utc, task_graph_path  # noqa: E402


def evaluate_run(*, graph: dict[str, Any], router_result: dict[str, Any], bay: str = DEFAULT_BAY) -> dict[str, Any]:
    rules = load_router_rules()
    caps = rules.get("cost_caps_usd") or {}
    intent = str((graph.get("prompt") or {}).get("intent") or "")
    total_cost = float(router_result.get("cost_usd_total") or 0)
    hard_cap = float(caps.get("hard_abort", 5.0))
    run_cap = float(caps.get("per_run_default", 2.0))
    tasks_ok = all(r.get("ok") for r in (router_result.get("results") or []))
    intent_ok = bool(intent) and tasks_ok
    cost_ok = total_cost <= run_cap
    verdict = "PASS" if intent_ok and cost_ok and total_cost <= hard_cap else "FAIL"
    reasons = []
    if not intent_ok:
        reasons.append("task_execution_or_intent")
    if not cost_ok:
        reasons.append("cost_over_run_cap")
    row = {
        "schema": "forge-critic-eval-v0.1",
        "at": now_utc(),
        "run_id": graph.get("run_id"),
        "verdict": verdict,
        "intent": intent[:200],
        "cost_usd_total": total_cost,
        "reasons": reasons,
    }
    append_trace(bay, "eval", row)
    return row


def run_critic_loop(
    *,
    graph: dict[str, Any],
    router_result: dict[str, Any],
    pick: dict[str, Any] | None = None,
    bay: str = DEFAULT_BAY,
    force_fail: bool = False,
) -> dict[str, Any]:
    meta = graph.get("meta_loop") or {}
    max_replan = int(meta.get("max_replan") or 2)
    replans = 0
    current_graph = graph
    current_router = router_result
    history: list[dict[str, Any]] = []

    while True:
        ev = evaluate_run(graph=current_graph, router_result=current_router, bay=bay)
        if force_fail and replans == 0:
            ev["verdict"] = "FAIL"
            ev["reasons"] = ["forced_fail_test"]
            force_fail = False
        history.append({"replan": replans, "eval": ev, "run_id": current_graph.get("run_id")})
        if ev.get("verdict") == "PASS":
            return {
                "ok": True,
                "schema": "forge-critic-loop-v0.1",
                "at": now_utc(),
                "replans": replans,
                "final_verdict": "PASS",
                "history": history,
            }
        if replans >= max_replan:
            return {
                "ok": False,
                "schema": "forge-critic-loop-v0.1",
                "at": now_utc(),
                "replans": replans,
                "final_verdict": "FAIL",
                "abort": True,
                "history": history,
            }
        replans += 1
        if not pick:
            pick = {"id": (graph.get("work_order") or {}).get("plan_id"), "workstream": "ws-ux", "competitor": "replan"}
        current_graph = build_task_graph(pick=pick, run_id=f"{graph.get('run_id')}-replan{replans}")
        path = task_graph_path(current_graph["run_id"], bay)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(current_graph, indent=2) + "\n", encoding="utf-8")
        from forge_router_execute_v01 import execute_graph  # noqa: WPS433

        current_router = execute_graph(graph=current_graph, bay=bay)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", required=True)
    ap.add_argument("--router-json", required=True)
    ap.add_argument("--bay", default=DEFAULT_BAY)
    ap.add_argument("--force-fail", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    graph = json.loads(Path(args.graph).read_text(encoding="utf-8"))
    router_result = json.loads(Path(args.router_json).read_text(encoding="utf-8"))
    row = run_critic_loop(graph=graph, router_result=router_result, bay=args.bay, force_fail=args.force_fail)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
