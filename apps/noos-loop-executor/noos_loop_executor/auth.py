"""Auth for POST /loop — X-NOOS-Loop-Secret header only."""
from __future__ import annotations

import os


def auth_ok(headers: dict[str, str]) -> tuple[bool, str | None]:
    secret = (os.environ.get("NOOS_LOOP_SECRET") or "").strip()
    if not secret:
        return False, "NOOS_LOOP_SECRET not configured"
    got = (headers.get("X-NOOS-Loop-Secret") or headers.get("x-noos-loop-secret") or "").strip()
    if not got:
        return False, "missing_X-NOOS-Loop-Secret"
    if got != secret:
        return False, "invalid_X-NOOS-Loop-Secret"
    return True, None
