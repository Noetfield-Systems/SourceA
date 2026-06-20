#!/usr/bin/env python3
"""Agentic layer pipeline v2 — upgraded L0–L3 stack sync · health · self-heal · unified SSOT.

Law: SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md
Receipt: ~/.sina/agentic-layer-pipeline-v2.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"

sys.path.insert(0, str(SCRIPTS))
from agentic_pipeline_lib_v1 import (  # noqa: E402
    L1_AGENTS,
    L2_AGENTS,
    L3_ROLES,
    PATHS,
    cross_ref_check,
    read_json,
    stack_health,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _factory_mode() -> str:
    try:
        from factory_control_v1 import load_factory_now  # noqa: WPS433

        return str(load_factory_now().get("mode") or "FREEZE")
    except Exception:
        return "UNKNOWN"


def run_agentic_pipeline_v2(
    *,
    sync_brain: bool = True,
    self_heal: bool = False,
    tier: str = "full",
) -> dict:
    t0 = datetime.now(timezone.utc)
    steps: list[dict] = []
    issues: list[str] = []

    if tier == "fast":
        sync_brain = False
        self_heal = False

    sys.path.insert(0, str(SCRIPTS))
    from l1_agent_pipeline_wire_v1 import wire_l1_pipeline  # noqa: WPS433

    l1 = wire_l1_pipeline(sync_brain=sync_brain)
    steps.append({"step": "l1_agent_pipeline_wire", "ok": bool(l1.get("ok")), "ms": l1.get("ms")})

    brain = read_json(PATHS["brain_wire"])
    l1 = read_json(PATHS["l1_pipeline"])
    cross_ok, cross_issues = cross_ref_check(l1, brain)
    issues.extend(cross_issues)

    health = stack_health(l1, brain)
    if not cross_ok:
        health["status"] = "degraded"
    if health["L1"].get("wire_staleness") in ("stale", "critical"):
        issues.append(f"L1 wire {health['L1']['wire_staleness']}")
        health["status"] = "degraded"
    if health["L2"].get("wire_staleness") in ("stale", "critical"):
        issues.append(f"L2 wire {health['L2']['wire_staleness']}")
        health["status"] = "degraded"
    if not health["dual_pick"].get("aligned") and health["dual_pick"].get("queue_sa"):
        issues.append("dual_pick misaligned")
        health["status"] = "degraded"

    wire_ok = bool(l1.get("ok")) and bool(brain.get("ok")) and cross_ok
    l1_count = len((l1.get("l1_to_brain") or {}).get("subordinates") or [])
    l2_count = len((brain.get("l2_wired") or {}).get("agents") or [])
    if l1_count < 3:
        issues.append(f"L1 subordinates {l1_count}<3")
        wire_ok = False
    if l2_count < 4:
        issues.append(f"L2 agents {l2_count}<4")
        wire_ok = False
    operational_ok = wire_ok and len(issues) == 0

    if self_heal and issues:
        steps.append({"step": "self_heal_trigger", "ok": True, "issues": issues[:5]})
        try:
            from hub_dual_heal_v1 import heal_two_hubs  # noqa: WPS433

            hub = heal_two_hubs(reason="agentic_pipeline_v2", full=False)
            steps.append({"step": "two_hub_heal", "ok": bool(hub.get("ok"))})
        except Exception as exc:
            steps.append({"step": "two_hub_heal", "ok": False, "error": str(exc)})
        l1 = wire_l1_pipeline(sync_brain=True)
        steps.append({"step": "self_heal_l1_resync", "ok": bool(l1.get("ok"))})
        brain = read_json(PATHS["brain_wire"])
        l1 = read_json(PATHS["l1_pipeline"])
        cross_ok, cross_issues = cross_ref_check(l1, brain)
        issues = cross_issues
        health = stack_health(l1, brain)
        if cross_ok and wire_ok:
            health["status"] = "healed" if issues else health.get("status", "ok")

    chat_ctx = read_json(PATHS["chat_context"])
    l3 = (chat_ctx.get("layer_stack") or {}).get("L3_portfolio_repos") or []

    ok = wire_ok
    ms = int((datetime.now(timezone.utc) - t0).total_seconds() * 1000)

    row = {
        "ok": ok,
        "operational_ok": operational_ok,
        "schema": "agentic-layer-pipeline-v2",
        "version": 2,
        "tier": tier,
        "at": _now(),
        "ms": ms,
        "factory_mode": _factory_mode(),
        "stack": {
            "L0": "ASF + Hub",
            "L0_5": "machine_pipeline_python",
            "L1": {"hub": "brain", "chat": "58148ac9", "agents": list(L1_AGENTS)},
            "L2": {"agents": list(L2_AGENTS), "wired_to": "brain"},
            "L3": {"roles": list(L3_ROLES), "repos": l3},
        },
        "health": health,
        "issues": issues,
        "cross_ref_ok": cross_ok,
        "ssot_paths": {k: str(v) for k, v in PATHS.items()},
        "commands": {
            "sync_full": "python3 scripts/agentic_layer_pipeline_v2.py --json",
            "sync_fast": "python3 scripts/agentic_layer_pipeline_v2.py --json --tier fast",
            "validate": "bash scripts/validate-agentic-layer-pipeline-v2.sh",
        },
        "l1_summary": {
            "at": l1.get("at"),
            "l1_to_brain": len((l1.get("l1_to_brain") or {}).get("subordinates") or []),
            "queue_head": ((l1.get("l1_wired") or {}).get("shared") or {}).get("queue_head", {}).get("sa_id"),
        },
        "brain_summary": {
            "at": brain.get("at"),
            "l2_wired": len((brain.get("l2_wired") or {}).get("agents") or []),
            "queue_head": (brain.get("queue_head") or {}).get("sa_id"),
            "reconciled_stale": (brain.get("reconciled_decision") or {}).get("stale"),
        },
        "steps": steps,
        "law": "SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md",
    }

    SINA.mkdir(parents=True, exist_ok=True)
    PATHS["pipeline_v2"].write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    sync_v1 = {
        "ok": ok,
        "schema": "agentic-layer-wire-sync-v1",
        "at": row["at"],
        "ms": ms,
        "pipeline_v2": str(PATHS["pipeline_v2"]),
        "queue_head": row["brain_summary"].get("queue_head"),
        "health_status": health.get("status"),
        "issues_count": len(issues),
    }
    PATHS["wire_sync_v1"].write_text(json.dumps(sync_v1, indent=2) + "\n", encoding="utf-8")

    if brain:
        brain["agentic_pipeline_v2"] = {
            "ssot": str(PATHS["pipeline_v2"]),
            "at": row["at"],
            "ok": ok,
            "health_status": health.get("status"),
            "tier": tier,
        }
        payload = json.dumps(brain, indent=2) + "\n"
        PATHS["brain_wire"].write_text(payload, encoding="utf-8")
        PATHS["brain_wire_alias"].write_text(payload, encoding="utf-8")

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Agentic layer pipeline v2 — upgraded stack sync")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--tier", choices=["fast", "full"], default="full")
    ap.add_argument("--no-sync", action="store_true", help="Skip brain snapshot sync")
    ap.add_argument("--self-heal", action="store_true", help="Re-sync on drift/staleness")
    args = ap.parse_args()
    sync = not args.no_sync and args.tier == "full"
    row = run_agentic_pipeline_v2(sync_brain=sync, self_heal=args.self_heal, tier=args.tier)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
