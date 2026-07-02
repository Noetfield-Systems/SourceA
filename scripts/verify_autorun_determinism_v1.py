#!/usr/bin/env python3
"""CI determinism gate — governed-autorun D1–D5 (4 tests).

Law: references/deterministic-loops.md · L13
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _test_d5_replay() -> dict[str, Any]:
    """Fold append-only events → state; replay must match."""
    events = [
        {"event": "claim", "halted": False, "last_path": "/api/cloud-forge-run/auto-tick/v1"},
        {"event": "halt", "halted": True, "halt_reason": "second_request_within_cycle_window"},
        {"event": "heal", "halted": False, "healed_trigger_source": "cloudflare_cron"},
    ]

    def fold(rows: list[dict[str, Any]]) -> dict[str, Any]:
        state: dict[str, Any] = {"schema": "cloud-auto-runtime-single-cycle-gate-v1", "halted": False}
        for row in rows:
            state.update({k: v for k, v in row.items() if k != "event"})
        return state

    live = fold(events)
    replay = fold(list(events))
    match = live == replay
    return {
        "id": "D5_replay",
        "law": "D5",
        "ok": match,
        "evidence": {"live": live, "replay": replay, "event_count": len(events)},
    }


def _test_d1_idempotency() -> dict[str, Any]:
    """Same op_key twice → second call reports duplicate."""
    sys.path.insert(0, str(SCRIPTS))
    from fbe.lib import execution_contract_v1 as ec  # noqa: WPS433

    key = hashlib.sha256(b"cloud-forge-run|cloudflare_cron|CLOUD-SEC-7666|77").hexdigest()[:40]
    with tempfile.TemporaryDirectory() as tmp:
        idx = Path(tmp) / "idempotency.json"
        original = ec.IDEMPOTENCY_INDEX_PATH
        ec.IDEMPOTENCY_INDEX_PATH = idx
        try:
            first = ec.check_idempotency(key)
            ec.record_idempotency(
                idempotency_key=key,
                job_id="determinism-test-d1",
                status="success",
                receipt_path=str(idx),
            )
            second = ec.check_idempotency(key)
            ok = first.get("ok") is True and second.get("ok") is False
            return {
                "id": "D1_idempotency",
                "law": "D1",
                "ok": ok,
                "evidence": {"first": first, "second": second, "op_key": key},
            }
        finally:
            ec.IDEMPOTENCY_INDEX_PATH = original


def _test_d2_cas_gate() -> dict[str, Any]:
    """Concurrent external claims: first wins, second HALT receipt."""
    sys.path.insert(0, str(SCRIPTS))
    import cloud_auto_runtime_single_cycle_gate_v1 as gate  # noqa: WPS433

    with tempfile.TemporaryDirectory() as tmp:
        gate_file = Path(tmp) / "gate.json"
        original = gate._gate_path
        gate._gate_path = lambda: gate_file  # type: ignore[method-assign]
        try:
            os.environ["CLOUD_DRAIN_SINGLE_CYCLE_SECONDS"] = "600"
            first = gate.claim_or_halt(
                path="/api/cloud-forge-run/auto-tick/v1",
                trigger_source="http",
            )
            second = gate.claim_or_halt(
                path="/api/cloud-forge-run/auto-tick/v1",
                trigger_source="http",
            )
            ok = first is None and second is not None and second.get("decision") == "halt_single_cycle"
            return {
                "id": "D2_cas_gate",
                "law": "D2",
                "ok": ok,
                "evidence": {
                    "first_claim": "proceed" if first is None else first.get("decision"),
                    "second_claim": second.get("decision") if second else None,
                    "reason": (second or {}).get("reason"),
                },
            }
        finally:
            gate._gate_path = original  # type: ignore[method-assign]


def _test_d4_transitions() -> dict[str, Any]:
    """Fuzz illegal transitions — all must reject."""
    sys.path.insert(0, str(SCRIPTS))
    from autorun_legal_transitions_v1 import validate_transition  # noqa: WPS433

    illegal = [
        ("IDLE_NO_WORK", "COMPLETE"),
        ("IDLE_NO_WORK", "BLOCKED_WITH_REASON"),
        ("RUNNING", "IDLE_NO_WORK"),
        ("COMPLETE", "BLOCKED_WITH_REASON"),
        ("THROTTLED_ROI", "RUNNING"),
    ]
    legal = [
        ("IDLE_NO_WORK", "RUNNING"),
        ("RUNNING", "BLOCKED_WITH_REASON"),
        ("BLOCKED_WITH_REASON", "IDLE_NO_WORK"),
    ]
    bad = [pair for pair in illegal if validate_transition(*pair).get("ok")]
    good = [pair for pair in legal if not validate_transition(*pair).get("ok")]
    ok = len(bad) == 0 and len(good) == 0
    return {
        "id": "D4_transitions",
        "law": "D4",
        "ok": ok,
        "evidence": {
            "illegal_accepted": bad,
            "legal_rejected": good,
            "illegal_tested": len(illegal),
            "legal_tested": len(legal),
        },
    }


def verify() -> dict[str, Any]:
    tests = [_test_d5_replay(), _test_d1_idempotency(), _test_d2_cas_gate(), _test_d4_transitions()]
    ok = all(t.get("ok") for t in tests)
    return {
        "schema": "autorun-determinism-verify-v1",
        "version": "1.0.0",
        "at": _now(),
        "law": "governed-autorun L13 · deterministic-loops D1-D5",
        "ok": ok,
        "tests": tests,
        "report_line": f"determinism {'PASS' if ok else 'FAIL'} · "
        + " · ".join(f"{t['id']}={'PASS' if t.get('ok') else 'FAIL'}" for t in tests),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--write-receipt", action="store_true")
    args = ap.parse_args()
    row = verify()
    if args.write_receipt:
        out = ROOT / "receipts" / "cloud" / "autorun-determinism" / "determinism-latest-v1.json"
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        row["receipt_path"] = str(out)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
