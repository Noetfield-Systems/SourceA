#!/usr/bin/env python3
"""Legal autorun state transitions (controlled-autorun D4 · L13)."""
from __future__ import annotations

from typing import FrozenSet

LEGAL_TRANSITIONS: dict[str, FrozenSet[str]] = {
    "IDLE_NO_WORK": frozenset({"RUNNING"}),
    "RUNNING": frozenset(
        {"COMPLETE", "FAILED_WITH_RECEIPT", "BLOCKED_WITH_REASON", "TRIAGE_REQUIRED", "THROTTLED_ROI"}
    ),
    "BLOCKED_WITH_REASON": frozenset({"IDLE_NO_WORK"}),
    "THROTTLED_ROI": frozenset({"IDLE_NO_WORK"}),
    "TRIAGE_REQUIRED": frozenset({"IDLE_NO_WORK"}),
    "FAILED_WITH_RECEIPT": frozenset({"IDLE_NO_WORK"}),
    "COMPLETE": frozenset({"IDLE_NO_WORK", "RUNNING"}),
}

BLOCKED_LIKE = frozenset({"BLOCKED_WITH_REASON", "THROTTLED_ROI", "TRIAGE_REQUIRED"})


def validate_transition(from_state: str, to_state: str) -> dict:
    """Return {ok, from_state, to_state, reason}."""
    src = str(from_state or "").strip().upper()
    dst = str(to_state or "").strip().upper()
    if not src or not dst:
        return {"ok": False, "from_state": src, "to_state": dst, "reason": "missing_state"}
    if src == dst:
        return {"ok": True, "from_state": src, "to_state": dst, "reason": "noop"}
    allowed = LEGAL_TRANSITIONS.get(src)
    if allowed is None:
        return {"ok": False, "from_state": src, "to_state": dst, "reason": "unknown_from_state"}
    if dst in allowed:
        return {"ok": True, "from_state": src, "to_state": dst, "reason": "legal"}
    if src in BLOCKED_LIKE and dst == "IDLE_NO_WORK":
        return {"ok": True, "from_state": src, "to_state": dst, "reason": "blocker_cleared"}
    return {"ok": False, "from_state": src, "to_state": dst, "reason": "illegal_transition"}
