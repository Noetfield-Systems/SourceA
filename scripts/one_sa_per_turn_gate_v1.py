#!/usr/bin/env python3
"""Mechanical one-sa-per-turn enforcement — law logged, not honor system.

Blocks: open turn without close · multiple sa_focus in report · broker submit mismatch.
Law: GOAL_EXECUTION_ACTIVE_LOCKED_v1.md · REGISTRY_DRAIN_RAIL_LOCKED_v1.md
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
VIOLATION_LOG = Path.home() / ".sina" / "one-sa-violations-v1.jsonl"

SA_RE = re.compile(r"\bsa-(?:\d{4}|B\d{4})\b", re.I)
SA_FOCUS_RE = re.compile(r"sa_focus:\s*(sa-(?:\d{4}|B\d{4}))", re.I)
REPORT_STATUS_RE = re.compile(r"^\s*status:\s*WORKER_ROUND_REPORT\s*$", re.I | re.M)
REGISTRY_UPDATED_RE = re.compile(r"registry_updated:\s*\[(.*?)\]", re.S | re.I)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log_violation(row: dict) -> None:
    VIOLATION_LOG.parent.mkdir(parents=True, exist_ok=True)
    with VIOLATION_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def extract_sa_focus_ids(text: str) -> list[str]:
    return [m.group(1).lower() for m in SA_FOCUS_RE.finditer(text or "")]


def count_round_reports(text: str) -> int:
    return len(REPORT_STATUS_RE.findall(text or ""))


def registry_updated_sa_ids(text: str) -> list[str]:
    out: list[str] = []
    for block in REGISTRY_UPDATED_RE.findall(text or ""):
        out.extend(m.group(0).lower() for m in SA_RE.finditer(block))
    return out


def validate_agent_output(*, text: str, expected_sa: str) -> dict:
    """Reject batching in agent/Worker reply before broker accepts."""
    expected = (expected_sa or "").lower()
    if not expected.startswith("sa-"):
        return {"ok": False, "error": "expected_sa_required"}

    focuses = extract_sa_focus_ids(text)
    unique_focus = sorted(set(focuses))
    report_count = count_round_reports(text)
    registry_ids = registry_updated_sa_ids(text)
    unique_registry = sorted(set(registry_ids))

    violations: list[str] = []
    if report_count > 1:
        violations.append(f"multiple_WORKER_ROUND_REPORT count={report_count}")
    if len(unique_focus) > 1:
        violations.append(f"multiple_sa_focus {unique_focus}")
    if unique_focus and expected not in unique_focus:
        violations.append(f"sa_focus_mismatch expected={expected} got={unique_focus}")
    if len(unique_registry) > 1:
        violations.append(f"registry_updated_multiple {unique_registry}")
    if len(unique_registry) == 1 and unique_registry[0] != expected:
        violations.append(f"registry_updated_wrong_sa {unique_registry[0]} != {expected}")

    # Heuristic: many distinct sa- mentions in implement section (batch narrative)
    all_sa = sorted(set(m.group(0).lower() for m in SA_RE.finditer(text or "")))
    if len(all_sa) > 3 and len(unique_focus) == 0:
        violations.append(f"suspected_batch_narrative sa_mentions={all_sa[:8]}")

    ok = not violations
    row = {
        "ok": ok,
        "status": "ONE_SA_GATE_PASS" if ok else "ONE_SA_BATCH_VIOLATION",
        "expected_sa": expected,
        "sa_focus_ids": unique_focus,
        "report_count": report_count,
        "registry_updated": unique_registry,
        "violations": violations,
    }
    if not ok:
        _log_violation(row)
    return row


def open_turn_for_inbox(*, force_close_stale: bool = False) -> dict:
    """Open mechanical turn from INBOX meta — blocks second concurrent turn."""
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import inbox_status  # noqa: WPS433
    from worker_turn_lib import close_turn, open_turn, turn_open_block, turn_state  # noqa: WPS433

    inbox = inbox_status()
    if not inbox.get("pending"):
        return {"ok": False, "error": "INBOX_NOT_PENDING", "step": "open_turn"}

    sa = str((inbox.get("meta") or {}).get("sa_id") or "")
    if not sa.startswith("sa-"):
        return {"ok": False, "error": "INBOX_MISSING_SA_ID"}

    st0 = turn_state() or {}
    if st0.get("status") == "open" and str(st0.get("sa_id") or "").startswith("sa-TEST"):
        close_turn(sa_id=st0.get("sa_id"), force=True)

    block = turn_open_block()
    if block:
        open_sa = block.get("open_sa") or (turn_state() or {}).get("sa_id")
        if force_close_stale and open_sa == sa:
            close_turn(sa_id=sa, force=True)
        elif open_sa == sa:
            return {"ok": True, "already_open": sa, "sa_id": sa}
        elif str(open_sa or "").startswith("sa-TEST"):
            close_turn(sa_id=open_sa, force=True)
        else:
            # Headless AUTO-RUN: close mismatched open turn so INBOX sa can proceed.
            close_turn(sa_id=open_sa, force=True)

    opened = open_turn(sa_id=sa, path=str(ROOT / ".sina-loop/INBOX.md"))
    if not opened.get("ok"):
        return opened
    return {"ok": True, "sa_id": sa, "opened": True}


def guard_before_agent_turn(*, expected_sa: str | None = None) -> dict:
    """Call at start_goal1_worker_turn — must pass before agent -p -f."""
    opened = open_turn_for_inbox()
    if not opened.get("ok"):
        return opened
    sa = expected_sa or opened.get("sa_id")
    return {"ok": True, "sa_id": sa, "turn": opened}


def guard_broker_submit(*, text: str, expected_sa: str) -> dict:
    """Call from goal1_lane_broker.worker_submit before accept."""
    sys.path.insert(0, str(SCRIPTS))
    from worker_turn_lib import turn_open_block, turn_state  # noqa: WPS433

    block = turn_open_block()
    st = turn_state()
    open_sa = (st or {}).get("sa_id")
    expected = (expected_sa or "").lower()

    if block and open_sa and open_sa.lower() != expected:
        row = {
            "ok": False,
            "status": "ONE_SA_TURN_BLOCKED",
            "error": f"turn open for {open_sa} not {expected}",
            "open_sa": open_sa,
        }
        _log_violation(row)
        return row

    out = validate_agent_output(text=text, expected_sa=expected)
    if not out.get("ok"):
        return out

    if st.get("status") == "open" and open_sa and open_sa.lower() != expected:
        return {
            "ok": False,
            "status": "ONE_SA_TURN_MISMATCH",
            "error": f"open_turn {open_sa} != report {expected}",
        }
    return out


def gate_status() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from worker_turn_lib import turn_open_block, turn_state  # noqa: WPS433
    from worker_inject_lib import inbox_status  # noqa: WPS433

    block = turn_open_block()
    inbox = inbox_status()
    st = turn_state() or {}
    inbox_sa = (inbox.get("meta") or {}).get("sa_id")
    open_sa = st.get("sa_id") if block else None
    # In-flight AUTO-RUN: open turn bound to current INBOX sa is OK (not a stale block).
    bound_ok = bool(block and open_sa and inbox_sa and str(open_sa) == str(inbox_sa))
    return {
        "ok": block is None or bound_ok,
        "turn_open": block is not None,
        "open_sa": open_sa,
        "inbox_sa": inbox_sa,
        "inbox_pending": inbox.get("pending"),
        "bound_to_inbox": bound_ok,
        "block": None if bound_ok else block,
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="One-sa-per-turn mechanical gate")
    p.add_argument("--status", action="store_true")
    p.add_argument("--open-inbox", action="store_true")
    p.add_argument("--validate-text", metavar="FILE", help="Validate agent output file")
    p.add_argument("--expected-sa", metavar="SA_ID")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.status:
        row = gate_status()
    elif args.open_inbox:
        row = open_turn_for_inbox()
    elif args.validate_text:
        text = Path(args.validate_text).read_text(encoding="utf-8", errors="replace")
        row = validate_agent_output(text=text, expected_sa=args.expected_sa or "")
    else:
        p.print_help()
        return 1

    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
