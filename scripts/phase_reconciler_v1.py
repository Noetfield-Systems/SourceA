#!/usr/bin/env python3
"""Phase reconciler — orchestrator only. READ desired · PROBE · PROJECT observed.

Law: data/execution-state-desired-observed-v1.json
NEVER writes assignment (desired). Founder/ASF alone authors desired state.

Separate modules (no shared write path with desired):
  phase_desired_read_v1.py      — read-only desired
  phase_transition_probe_v1.py  — live preconditions
  phase_observed_project_v1.py  — observed writes only
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
from phase_desired_read_v1 import desired_cloud_drain_head, read_desired_active  # noqa: E402
from phase_observed_project_v1 import (  # noqa: E402
    already_reconciled_phase_market,
    append_event,
    derive_era_from_event_log,
    has_probe_backed_ratify,
    project_cycle2_to_market,
    read_observed_era,
)
from phase_transition_probe_v1 import probe_cycle2_to_market_preconditions, probe_hub  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _write_receipt(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def ratify_phase_market(*, dry_run: bool = False) -> dict:
    """Append probe-backed ratify event without re-projecting observed surfaces (law v1.2.0)."""
    desired = read_desired_active()
    cloud_head = desired_cloud_drain_head()
    probe = probe_cycle2_to_market_preconditions()
    ff = (probe.get("probes") or {}).get("ff_cycle2") or {}

    if not probe.get("ok"):
        return {
            "schema": "phase-ratify-receipt-v1",
            "ok": False,
            "error": "probe_failed",
            "issues": probe.get("issues") or [],
            "probe": probe,
            "at": _now(),
            "law": "ratify requires 10/10 probe — no silent waiver",
        }

    if has_probe_backed_ratify():
        return {
            "schema": "phase-ratify-receipt-v1",
            "ok": True,
            "noop": True,
            "reason": "already_ratified",
            "observed_era": read_observed_era(),
            "derived_era_from_log": derive_era_from_event_log(),
            "cloud_drain_head": cloud_head,
            "at": _now(),
        }

    if dry_run:
        return {
            "schema": "phase-ratify-receipt-v1",
            "ok": True,
            "dry_run": True,
            "would_append": {
                "event": "forge_factory_cycle2_closed",
                "ratify": True,
                "probe_gate_pass": True,
                "to_era": "phase_market",
                "probe_ff_ok_count": ff.get("ok_count"),
            },
            "observed_unchanged": True,
            "at": _now(),
        }

    append_event(
        {
            "schema": "phase-event-v1",
            "event": "forge_factory_cycle2_closed",
            "ratify": True,
            "probe_gate_pass": True,
            "from_era": "forge_factory_cycle2",
            "to_era": "phase_market",
            "cloud_drain_head": cloud_head,
            "desired_ref": desired.get("source"),
            "probe_ff_ok_count": ff.get("ok_count"),
            "probe_snapshot_at": probe.get("at"),
            "observed_unchanged": True,
            "reconciler": "phase_reconciler_v1.py:ratify",
        }
    )
    receipt = {
        "schema": "phase-ratify-receipt-v1",
        "ok": True,
        "ratified": True,
        "noop": False,
        "observed_unchanged": True,
        "probe": {"ok": True, "ff_ok_count": ff.get("ok_count")},
        "derived_era_from_log": derive_era_from_event_log(),
        "event_log": str(SINA / "phase-event-log-v1.jsonl"),
        "line": "phase_market ratified · probe-backed · observed projection unchanged",
        "at": _now(),
    }
    _write_receipt(SINA / "phase-ratify-receipt-v1.json", receipt)
    return receipt


def reconcile_cycle2_to_market(*, dry_run: bool = False, force: bool = False) -> dict:
    desired = read_desired_active()
    cloud_head = desired_cloud_drain_head()
    phase_id = str(desired.get("phase_id") or "")

    if not force and already_reconciled_phase_market(desired_phase_id=phase_id, cloud_head=cloud_head):
        return {
            "schema": "phase-reconciler-receipt-v1",
            "ok": True,
            "noop": True,
            "reason": "already_reconciled",
            "observed_era": read_observed_era() or "phase_market",
            "cloud_drain_head": cloud_head,
            "desired_source": desired.get("source"),
            "at": _now(),
        }

    probe = probe_cycle2_to_market_preconditions()
    if not probe.get("ok") and not dry_run:
        return {
            "schema": "phase-reconciler-receipt-v1",
            "ok": False,
            "error": "preconditions_failed",
            "issues": probe.get("issues") or [],
            "probe": probe,
            "at": _now(),
            "law": "probe_beats_closeout — closeout file never used as gate",
        }

    if dry_run:
        return {
            "schema": "phase-reconciler-receipt-v1",
            "ok": True,
            "dry_run": True,
            "event": "forge_factory_cycle2_closed",
            "from_era": read_observed_era(),
            "to_era": "phase_market",
            "cloud_drain_head": cloud_head,
            "desired_active": desired,
            "probe_ok": probe.get("ok"),
            "at": _now(),
        }

    projected = project_cycle2_to_market(cloud_head=cloud_head, caller="phase_reconciler_v1")
    if not projected.get("ok"):
        return {
            "schema": "phase-reconciler-receipt-v1",
            "ok": False,
            "error": "observed_projection_failed",
            "steps": projected.get("steps") or [],
            "at": _now(),
        }

    append_event(
        {
            "schema": "phase-event-v1",
            "event": "forge_factory_cycle2_closed",
            "from_era": "forge_factory_cycle2",
            "to_era": "phase_market",
            "cloud_drain_head": cloud_head,
            "desired_ref": desired.get("source"),
            "probe_ff_ok_count": (probe.get("probes") or {}).get("ff_cycle2", {}).get("ok_count"),
            "reconciler": "phase_reconciler_v1.py",
        }
    )

    receipt = {
        "schema": "phase-reconciler-receipt-v1",
        "ok": True,
        "event": "forge_factory_cycle2_closed",
        "from_era": "forge_factory_cycle2",
        "to_era": "phase_market",
        "cloud_drain_head": cloud_head,
        "desired_active": desired,
        "noop": False,
        "steps": projected.get("steps") or [],
        "probe": {"ok": probe.get("ok"), "issues": probe.get("issues") or []},
        "event_log": str(SINA / "phase-event-log-v1.jsonl"),
        "line": f"phase_market · {cloud_head} · observed reconciled · desired read-only",
        "at": _now(),
    }
    _write_receipt(SINA / "phase-reconciler-receipt-v1.json", receipt)
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Phase reconciler — desired read · probe · observed project")
    ap.add_argument("--transition", default="cycle2-to-market", choices=["cycle2-to-market", "ratify-phase-market"])
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--force", action="store_true", help="Skip idempotency noop only — probe still required unless dry-run")
    ap.add_argument("--probe-hub", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.probe_hub:
        row = probe_hub()
    elif args.transition == "ratify-phase-market":
        row = ratify_phase_market(dry_run=args.dry_run)
    elif args.transition == "cycle2-to-market":
        row = reconcile_cycle2_to_market(dry_run=args.dry_run, force=args.force)
    else:
        row = {"ok": False, "error": "unknown_transition"}

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or row.get("reason") or json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
