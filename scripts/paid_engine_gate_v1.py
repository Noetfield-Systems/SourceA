#!/usr/bin/env python3
"""Block ALL paid Anthropic/CLI calls when kill flag or api-disabled flag is set."""
from __future__ import annotations

from pathlib import Path

KILL = Path.home() / ".sina" / "auto-run-disabled-v1.flag"
FOUNDER_WORK = Path.home() / ".sina" / "founder-work-mode-v1.flag"
API_OFF = Path.home() / ".sina" / "api-disabled-v1.flag"
CLI_OFF = Path.home() / ".sina" / "cli-disabled-v1.flag"


def block_paid(*, engine: str = "any", caller: str = "") -> dict | None:
    """Return block dict if paid call forbidden; None if allowed."""
    # auto-run-disabled pauses factory only — must NOT block founder Cursor work
    if KILL.is_file() and not FOUNDER_WORK.is_file():
        return {
            "ok": False,
            "blocked": True,
            "reason": "autorun_kill_flag",
            "cost_usd": 0,
            "caller": caller,
            "engine": engine,
        }
    if engine in ("api", "any") and API_OFF.is_file():
        return {
            "ok": False,
            "blocked": True,
            "reason": "api_disabled_flag",
            "cost_usd": 0,
            "caller": caller,
            "engine": "api",
        }
    if engine in ("cli", "any") and CLI_OFF.is_file():
        return {
            "ok": False,
            "blocked": True,
            "reason": "cli_disabled_flag",
            "cost_usd": 0,
            "caller": caller,
            "engine": "cli",
        }
    return None
