#!/usr/bin/env python3
"""Factory mode — re-exports factory_control_v1."""
from factory_control_v1 import DRAIN_MODES, VALID_MODES, allow_single_sa, current_mode, freeze

load_mode = lambda: {"mode": current_mode(), "schema": "factory-mode-v1"}


def set_mode(mode: str, *, set_by: str, reason: str = "") -> dict:
    from factory_control_v1 import freeze as _freeze

    if mode == "FREEZE":
        return _freeze(set_by=set_by, reason=reason)
    if mode == "SINGLE_SA":
        return allow_single_sa(set_by=set_by, reason=reason)
    return {"ok": False, "error": f"invalid_mode:{mode}"}
