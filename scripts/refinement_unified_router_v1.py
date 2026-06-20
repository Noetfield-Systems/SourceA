#!/usr/bin/env python3
"""Unified refinement router — agent pipelines + machine pipelines together.

Law: REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md

Usage:
  python3 scripts/refinement_unified_router_v1.py agent orientation --json
  python3 scripts/refinement_unified_router_v1.py machine tune --json
  python3 scripts/refinement_unified_router_v1.py both hospital tune --role worker --json
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "refinement-unified-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load(name: str):
    path = SCRIPTS / name
    spec = importlib.util.spec_from_file_location(name.replace(".py", ""), path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def run_unified(*, domain: str, agent_trigger: str = "", machine_trigger: str = "", **kwargs) -> dict:
    results: dict = {"agent": None, "machine": None}
    if domain in ("agent", "both") and agent_trigger:
        results["agent"] = _load("agent_three_pipelines_router_v1.py").route(agent_trigger, role=kwargs.get("role", "any"))
    if domain in ("machine", "both") and machine_trigger:
        results["machine"] = _load("machine_three_pipelines_router_v1.py").route(
            machine_trigger,
            ladder_tier=kwargs.get("ladder_tier", "daily"),
            upgrade_id=kwargs.get("upgrade_id", ""),
            role=kwargs.get("role", "worker"),
        )
    ok = all(r.get("ok") for r in results.values() if r)
    row = {
        "schema": "refinement-unified-receipt-v1",
        "ok": ok,
        "at": _now(),
        "domain": domain,
        "agent_trigger": agent_trigger or None,
        "machine_trigger": machine_trigger or None,
        "results": results,
        "law": "brain-os/law/REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Unified refinement router")
    ap.add_argument("domain", choices=["agent", "machine", "both"])
    ap.add_argument("trigger", nargs="+", help="agent trigger and/or machine trigger when both")
    ap.add_argument("--role", default="worker")
    ap.add_argument("--ladder-tier", default="daily")
    ap.add_argument("--upgrade-id", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    agent_t = machine_t = ""
    if args.domain == "agent":
        agent_t = args.trigger[0]
    elif args.domain == "machine":
        machine_t = args.trigger[0]
    else:
        if len(args.trigger) >= 2:
            agent_t, machine_t = args.trigger[0], args.trigger[1]
        elif args.trigger[0] in ("orientation", "hospital", "maze"):
            agent_t = args.trigger[0]
        else:
            machine_t = args.trigger[0]

    row = run_unified(
        domain=args.domain,
        agent_trigger=agent_t,
        machine_trigger=machine_t,
        role=args.role,
        ladder_tier=args.ladder_tier,
        upgrade_id=args.upgrade_id,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"REFINE unified ok={row['ok']} domain={args.domain}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
