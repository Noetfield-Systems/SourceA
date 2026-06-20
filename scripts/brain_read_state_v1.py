#!/usr/bin/env python3
"""Brain maintainer — read Mac SSOT before every answer. One JSON, no memory."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
INBOX = ROOT / ".sina-loop" / "INBOX.md"
sys.path.insert(0, str(SCRIPTS))


def _inbox_meta() -> dict:
    if not INBOX.is_file():
        return {"pending": False, "error": "INBOX_MISSING"}
    text = INBOX.read_text(encoding="utf-8", errors="replace")
    m = re.search(
        r"pending=(\d+).*?queue=(\d+)/(\d+).*?role=(\w+).*?sa=(sa-\d+)",
        text,
        re.S,
    )
    if not m:
        return {"pending": "?", "raw_header": text.splitlines()[0] if text else ""}
    return {
        "pending": m.group(1) == "1",
        "queue_pos": int(m.group(2)),
        "queue_total": int(m.group(3)),
        "role": m.group(4),
        "sa_id": m.group(5),
    }


def read_state(*, caller: str = "brain") -> dict:
    from active_now_v1 import heartbeat, load_active_now  # noqa: WPS433

    hb = heartbeat(caller=caller, enforce=False)
    active = load_active_now()
    qst = Path.home() / ".sina" / "healthy-queue-state-v1.json"
    orch = Path.home() / ".sina" / "healthy-drain-orchestrator-v1.json"
    report = Path.home() / ".sina" / "worker_round_report_v1.json"

    queue = {}
    if qst.is_file():
        try:
            queue = json.loads(qst.read_text())
        except json.JSONDecodeError:
            queue = {"error": "invalid_json"}

    orchestrator = {}
    if orch.is_file():
        try:
            orchestrator = json.loads(orch.read_text())
        except json.JSONDecodeError:
            orchestrator = {"error": "invalid_json"}

    round_report = None
    if report.is_file():
        try:
            round_report = json.loads(report.read_text())
        except json.JSONDecodeError:
            round_report = {"error": "invalid_json"}

    inbox = _inbox_meta()
    orch_status = orchestrator.get("status") or "idle"
    orch_sa = orchestrator.get("expected_sa")
    if orch_status == "idle" and not inbox.get("pending"):
        orch_aligned = orch_sa is None or orch_sa == active.get("current_sa_id")
    else:
        orch_aligned = orch_sa == active.get("current_sa_id")
    aligned = (
        inbox.get("sa_id") == active.get("current_sa_id")
        and inbox.get("queue_pos") == active.get("queue_pos")
        and queue.get("next_pos") == active.get("queue_pos")
        and orch_aligned
    )
    report_ok = True
    if round_report and orchestrator.get("status") == "awaiting_worker":
        exp = orchestrator.get("expected_sa")
        got = round_report.get("sa_focus")
        if got and exp and got != exp:
            report_ok = False

    return {
        "ok": hb.get("ok") and aligned,
        "aligned": aligned,
        "report_blocks_advance": not report_ok,
        "registry_note": active.get("current_blocker"),
        "heartbeat": {
            "sa_id": active.get("current_sa_id"),
            "queue_pos": active.get("queue_pos"),
            "queue_total": active.get("queue_total"),
            "founder_mode": active.get("founder_mode"),
        },
        "queue_state": queue,
        "inbox": inbox,
        "orchestrator": {
            "status": orchestrator.get("status"),
            "expected_sa": orchestrator.get("expected_sa"),
            "expected_pos": orchestrator.get("expected_pos"),
            "expected_role": orchestrator.get("expected_role"),
        },
        "round_report": round_report,
        "gatekeeper_hint": "python3 scripts/gatekeeper_v1.py",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Brain read Mac SSOT before answer")
    p.add_argument("--caller", default="brain_maintainer")
    p.add_argument("--json", action="store_true", default=True)
    args = p.parse_args()
    row = read_state(caller=args.caller)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
