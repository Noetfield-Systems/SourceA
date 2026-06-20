#!/usr/bin/env python3
"""Stop/resume receipts — re-exports factory_control_v1."""
from factory_control_v1 import (
    load_resume_token,
    load_stop_receipt,
    stop_receipt_open,
    write_resume_token,
    write_stop_receipt,
)


def clear_stop_receipt(*, set_by: str = "founder_resume") -> dict:
    from factory_control_v1 import STOP_RECEIPT, _atomic_write, _now, load_stop_receipt

    row = load_stop_receipt() or {"schema": "founder-stop-receipt-v1"}
    row.update({"cleared_by_asf": True, "cleared_at": _now(), "cleared_by": set_by})
    _atomic_write(STOP_RECEIPT, row)
    return {"ok": True, **row}


def consume_resume_turn(*, caller: str) -> dict:
    from factory_control_v1 import KILL_FLAG, RESUME_TOKEN, _atomic_write, _invalidate_caches, _now, freeze

    token = load_resume_token()
    if not token:
        return {"ok": False, "error": "no_resume_token"}
    turns_left = int(token.get("turns_left", token.get("max_turns") or 0)) - 1
    if turns_left <= 0:
        RESUME_TOKEN.unlink(missing_ok=True)
        freeze(set_by=caller, reason="resume_token_exhausted")
        KILL_FLAG.touch()
        _invalidate_caches()
        return {"ok": True, "turns_left": 0}
    token.update({"turns_left": turns_left, "last_caller": caller, "last_at": _now()})
    _atomic_write(RESUME_TOKEN, token)
    return {"ok": True, "turns_left": turns_left}
