"""Mac focus freeze — respect auto-run-disabled during Cursor work sessions.

Law: factory motors + burst governance belong on cloud; Mac runs Cursor + Mac Health only.
Flag: ~/.sina/auto-run-disabled-v1.flag (written by Mac Health auto-stop / founder pause)
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
FREEZE_FLAG = SINA / "auto-run-disabled-v1.flag"
FOUNDER_WORK_FLAG = SINA / "founder-work-mode-v1.flag"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def is_focus_freeze() -> bool:
    if FOUNDER_WORK_FLAG.is_file():
        return True
    if FREEZE_FLAG.is_file():
        return True
    emergency = SINA / "mac-health-emergency-active-v1.flag"
    return emergency.is_file()


def freeze_line() -> str:
    if not FREEZE_FLAG.is_file():
        return ""
    try:
        return FREEZE_FLAG.read_text(encoding="utf-8").splitlines()[0][:200]
    except OSError:
        return "auto-run-disabled-v1.flag"


def skip_receipt(*, schema: str, script: str, note: str = "") -> dict[str, Any]:
    return {
        "schema": schema,
        "ok": True,
        "at": _now(),
        "mode": "mac_focus_freeze",
        "skipped": True,
        "freeze_flag": str(FREEZE_FLAG),
        "freeze_line": freeze_line(),
        "script": script,
        "note": note or "Mac focus freeze — factory deferred to cloud",
        "execution_plane": "cloud_deferred",
    }


def read_cached_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
