#!/usr/bin/env python3
"""NewMatch free-tier readiness check — Phase 0 $0 gate before paid escalation.

Law: data/newmatch-factory-v1.json · data/tool-pick-two-phase-v1.json
Receipt: ~/.sina/newmatch-free-tier-check-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "newmatch-factory-v1.json"
PLAN = ROOT / "data" / "newmatch-factory-999-plan-v1.json"
TOOL_PICK = ROOT / "data" / "tool-pick-two-phase-v1.json"
GRAPH = ROOT / "data" / "newmatch-graph-schema-v1.json"
RECEIPT = Path.home() / ".sina" / "newmatch-free-tier-check-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def assess() -> dict:
    checks: list[dict] = []
    ok = True

    def add(name: str, passed: bool, detail: str) -> None:
        nonlocal ok
        if not passed:
            ok = False
        checks.append({"name": name, "ok": passed, "detail": detail})

    ssot = json.loads(SSOT.read_text(encoding="utf-8"))
    ft = ssot.get("free_tier_policy") or {}
    add(
        "phase_0_ceiling",
        ft.get("phase_0_cost_ceiling_usd") == 0,
        f"phase_0_cost_ceiling_usd={ft.get('phase_0_cost_ceiling_usd')}",
    )
    add("graph_schema", GRAPH.is_file(), str(GRAPH))
    scaffold_graph = ROOT / "apps" / "newmatch" / "data" / "graph-v1.json"
    scaffold_schema = ROOT / "apps" / "newmatch" / "schema" / "graph-v1.json"
    add("apps_scaffold_graph", scaffold_graph.is_file(), str(scaffold_graph))
    add("apps_scaffold_schema", scaffold_schema.is_file(), str(scaffold_schema))
    add("tool_pick", TOOL_PICK.is_file(), "phase_1_free exhaust wired")

    if PLAN.is_file():
        plan_doc = json.loads(PLAN.read_text(encoding="utf-8"))
        plans = plan_doc.get("plans") or []
        free_n = sum(1 for p in plans if p.get("marginal_cost_usd", 0) == 0)
        all_free_first = all(p.get("free_tier_first") for p in plans)
        add("999_free_plans", free_n >= 700, f"free={free_n}/999")
        add("999_free_tier_first", all_free_first, f"rows={len(plans)}")
    else:
        add("999_plan", False, "missing — run gen_newmatch_factory_999_plan_v1.py")

    stack = ssot.get("free_stack_newmatch") or {}
    add(
        "free_llm_chain",
        len(stack.get("router_logic") or []) >= 4,
        ",".join(stack.get("router_logic") or [])[:120],
    )
    add(
        "paid_blocked",
        "paid_blocked_until" in stack,
        stack.get("paid_blocked_until", "missing"),
    )

    line = (
        f"newmatch-free-tier · {'PASS' if ok else 'FAIL'} · "
        f"phase0=$0 · free_plans={free_n if PLAN.is_file() else '?'}"
    )
    doc = {
        "ok": ok,
        "saved_at": _now(),
        "schema": "newmatch-free-tier-check-v1",
        "line": line,
        "checks": checks,
        "ssot_version": ssot.get("version"),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return doc


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    doc = assess()
    if args.json:
        print(json.dumps(doc, indent=2))
    else:
        print(doc["line"])
    return 0 if doc["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
