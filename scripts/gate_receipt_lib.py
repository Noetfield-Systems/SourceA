"""Gate receipt verification — Layer 3 mechanical enforcement for hub loop."""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

GATE_RECEIPT = Path.home() / ".sina" / "cursor_entry_gate_receipt_v1.json"
BRAIN_RECEIPT = Path.home() / ".sina" / "brain_session_receipt_v1.json"


def _parse_iso(ts: str) -> datetime | None:
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except ValueError:
        return None


def gate_receipt_ok(*, role: str = "worker", max_age_hours: float = 24.0) -> tuple[bool, str, dict | None]:
    if not GATE_RECEIPT.is_file():
        return False, "missing ~/.sina/cursor_entry_gate_receipt_v1.json — run cursor_entry_gate.py", None
    try:
        data = json.loads(GATE_RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return False, f"invalid gate receipt: {exc}", None
    if data.get("role") != role:
        return (
            False,
            f"gate role {data.get('role')!r} != required {role!r} — rerun cursor_entry_gate.py --role {role}",
            data,
        )
    at = _parse_iso(str(data.get("at") or ""))
    if not at:
        return False, "gate receipt missing valid timestamp", data
    age = datetime.now(timezone.utc) - at
    if age > timedelta(hours=max_age_hours):
        return False, f"gate receipt stale ({int(age.total_seconds() // 3600)}h) — rerun cursor_entry_gate.py", data
    if not data.get("gate_hash8"):
        return False, "gate receipt missing gate_hash8", data
    return True, "", data


def loop_gate_block(*, max_age_hours: float = 8.0) -> dict | None:
    """Return error payload if agent loop must not advance; None if ok."""
    ok, err, receipt = gate_receipt_ok(role="worker", max_age_hours=max_age_hours)
    if ok:
        return None
    return {
        "ok": False,
        "error": err,
        "gate_blocked": True,
        "hint": (
            "cd ~/Desktop/SourceA && python3 scripts/cursor_entry_gate.py --role worker "
            "&& python3 scripts/cursor_agent_self_audit.py session-start"
        ),
        "gate_receipt": str(GATE_RECEIPT),
        "gate_hash8": (receipt or {}).get("gate_hash8"),
    }
