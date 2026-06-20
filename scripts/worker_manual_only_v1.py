#!/usr/bin/env python3
"""INBOX is default. Manual-only only when worker-manual-only-v1.flag is set."""
from __future__ import annotations

from pathlib import Path

MANUAL_FLAG = Path.home() / ".sina" / "worker-manual-only-v1.flag"


def is_manual_only() -> bool:
    return MANUAL_FLAG.is_file()


def manual_hint(*, sa_id: str = "", role: str = "", pos: str = "") -> str:
    bind = f"{sa_id} {role} pos={pos}".strip()
    return (
        "Manual mode — no INBOX inject. "
        f"Paste from Hub{(' (' + bind + ')') if bind else ''}."
    )
