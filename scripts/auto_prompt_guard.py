#!/usr/bin/env python3
"""Permanent kill-switch — no Cursor paste/inject/auto-feed from Sina Command by default."""
from __future__ import annotations

import json
from pathlib import Path

KILL_PATH = Path.home() / ".sina" / "auto-prompt-kill.json"


def auto_prompt_blocked() -> bool:
    """Always blocked unless founder creates ~/.sina/auto-prompt-opt-in.json with enabled:true."""
    opt = Path.home() / ".sina" / "auto-prompt-opt-in.json"
    if opt.is_file():
        try:
            return not bool(json.loads(opt.read_text(encoding="utf-8")).get("enabled"))
        except json.JSONDecodeError:
            pass
    return True


def founder_opted_in() -> bool:
    """True only when founder explicitly created ~/.sina/auto-prompt-opt-in.json."""
    opt = Path.home() / ".sina" / "auto-prompt-opt-in.json"
    if not opt.is_file():
        return False
    try:
        return bool(json.loads(opt.read_text(encoding="utf-8")).get("enabled"))
    except json.JSONDecodeError:
        return False


def block_inject(reason: str = "auto_prompt_off") -> dict:
    return {"ok": False, "skipped": True, "blocked": True, "reason": reason}


def ensure_kill_on() -> None:
    KILL_PATH.parent.mkdir(parents=True, exist_ok=True)
    KILL_PATH.write_text(
        json.dumps({"disabled": True, "reason": "permanent_default"}, indent=2),
        encoding="utf-8",
    )


def disable_auto_feed_everywhere() -> None:
    from prompt_queue import _load, _save, set_auto_feed  # noqa: WPS433

    set_auto_feed(False)
    data = _load()
    data["auto_feed"] = False
    _save(data)
    st_path = Path.home() / ".sina" / "prompt-direction.json"
    if st_path.is_file():
        try:
            st = json.loads(st_path.read_text(encoding="utf-8"))
            if st.get("status") == "feeding":
                st["status"] = "queued"
            st_path.write_text(json.dumps(st, indent=2), encoding="utf-8")
        except (json.JSONDecodeError, OSError):
            pass
