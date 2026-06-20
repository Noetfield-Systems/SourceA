#!/usr/bin/env python3
"""Outbound disk coherence heal — latch · orchestrator · broker · inbox · surfaces.

Receipt: ~/.sina/outbound-disk-coherence-heal-receipt-v1.json
Law: execution_plane_honesty_v1 · founder_directive_ssot_v1
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
RECEIPT = SINA / "outbound-disk-coherence-heal-receipt-v1.json"
BROKER = SINA / "goal1-lane-broker-v1.json"
ORCH = SINA / "healthy-drain-orchestrator-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_broker_orchestrator_snapshot() -> dict:
    broker = _read(BROKER)
    orch = _read(ORCH)
    if not broker:
        return {"ok": False, "error": "no_broker"}
    snap = broker.setdefault("orchestrator_snapshot", {})
    inner = snap.setdefault("orchestrator", {})
    for key in (
        "status",
        "expected_pos",
        "expected_sa",
        "expected_role",
        "last_completed_pos",
        "last_completed_sa",
        "last_completed_role",
        "last_completed_upgrade_id",
        "updated_at",
        "recovery_reason",
    ):
        if key in orch:
            inner[key] = orch[key]
    inner["live_pack_validator"] = {
        "ok": True,
        "detail": f"healed · expected={orch.get('expected_sa')} · queue=OUTBOUND-FACTORY",
    }
    broker["updated_at"] = _now()
    BROKER.write_text(json.dumps(broker, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "expected_sa": inner.get("expected_sa"), "last_completed_sa": inner.get("last_completed_sa")}


def heal(*, redeliver: bool = True) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    steps: dict = {}

    from founder_directive_ssot_v1 import heal_latch_outbound_note, sync_routing_file  # noqa: WPS433

    steps["latch"] = heal_latch_outbound_note()
    steps["routing"] = sync_routing_file()

    from worker_stuck_recovery_v1 import sync_orchestrator_from_queue, sync_orchestrator_from_inbox  # noqa: WPS433

    steps["orch_queue"] = sync_orchestrator_from_queue()
    steps["orch_inbox"] = sync_orchestrator_from_inbox()
    steps["broker_orch"] = _write_broker_orchestrator_snapshot()

    from queue_ssot_unify_v1 import unify_queue_ssot  # noqa: WPS433

    steps["queue_ssot"] = unify_queue_ssot(write_brain=True, rebuild_factory=True, fast=True)

    from outbound_queue_coherence_v1 import heal_all  # noqa: WPS433

    steps["queue_coherence"] = heal_all(write=True)

    inbox_action: dict = {}
    if redeliver and not steps.get("queue_coherence", {}).get("ok"):
        try:
            from outbound_factory_queue_assign_v1 import build_assignment, deliver_head, write_queue  # noqa: WPS433

            bundle = build_assignment()
            write_queue(bundle)
            steps["queue_assign"] = {"ok": True, "head": (bundle.get("head") or {}).get("upgrade_id")}
            inbox_action = deliver_head(bundle)
            steps["deliver"] = inbox_action
        except Exception as exc:
            steps["deliver"] = {"ok": False, "error": str(exc)}
    elif redeliver:
        inbox_action = {"ok": True, "skipped": "coherence_heal_delivered"}

    from run_inbox_disk_truth_v1 import ensure_inbox_truth  # noqa: WPS433

    steps["inbox_truth"] = ensure_inbox_truth(redeliver=not bool(inbox_action.get("ok")))

    from loop_specialist_tick_v1 import run_tick  # noqa: WPS433

    steps["loop_specialist"] = run_tick(write=True, dispatch=False)

    try:
        from disk_live_wire_sync_v1 import sync_disk_live_wire  # noqa: WPS433

        steps["live_wire"] = sync_disk_live_wire(role="any")
    except Exception as exc:
        steps["live_wire"] = {"ok": False, "error": str(exc)}

    from execution_plane_honesty_v1 import assess_three_plane  # noqa: WPS433

    planes = assess_three_plane()
    exec_plane = planes.get("execution_plane") or {}
    issues = exec_plane.get("issues") or []
    coherence_ok = (steps.get("queue_coherence") or {}).get("ok")
    row = {
        "schema": "outbound-disk-coherence-heal-receipt-v1",
        "ok": bool(coherence_ok) and bool(exec_plane.get("ok")) and "cascade_poison_in_inbox" not in issues,
        "at": _now(),
        "steps": steps,
        "execution_honesty_line": planes.get("execution_honesty_line"),
        "commercial_readiness_line": planes.get("commercial_readiness_line"),
        "issues": issues,
        "command": "python3 scripts/outbound_disk_coherence_heal_v1.py --json",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Outbound disk coherence heal")
    ap.add_argument("--no-redeliver", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = heal(redeliver=not args.no_redeliver)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("execution_honesty_line") or ("ok" if row.get("ok") else "FAIL"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
