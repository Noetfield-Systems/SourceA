"""Clipboard / Cursor automation — permanently disabled unless SINA_ALLOW_CURSOR_PASTE=1 in env."""
from __future__ import annotations

import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

_ATTEMPT_LOG = Path.home() / ".sina" / "cursor-inject-blocked.log"


def _log_block(caller: str, preview: str) -> None:
    try:
        _ATTEMPT_LOG.parent.mkdir(parents=True, exist_ok=True)
        line = f"{datetime.now(timezone.utc).isoformat()} BLOCKED {caller} {preview[:80]!r}\n"
        with _ATTEMPT_LOG.open("a", encoding="utf-8") as f:
            f.write(line)
    except OSError:
        pass


def _read_clipboard() -> bytes:
    proc = subprocess.run(["pbpaste"], capture_output=True, check=False)
    return proc.stdout if proc.returncode == 0 else b""


def _write_clipboard(data: bytes) -> None:
    subprocess.run(["pbcopy"], input=data, check=False)


def _paste_allowed() -> bool:
    return os.environ.get("SINA_ALLOW_CURSOR_PASTE", "").strip() in ("1", "true", "yes")


def clipboard_paste_into_cursor(
    text: str,
    *,
    activate_delay: float = 0.6,
    allow_automation: bool = False,
    target: str = "focused",
) -> dict:
    """Blocked by default — prevents background hub from spamming Cursor when app is closed.

    target=worker | goal1 → disk INBOX only (never paste into whichever chat is focused).
    target=focused → legacy Cmd+V into active Cursor chat (Brain hijack risk).
    """
    preview = (text or "").strip()[:120]
    tgt = (target or "focused").strip().lower()
    worker_lane = tgt in ("worker", "goal1", "sourcea_worker")
    if not worker_lane:
        try:
            from brain_lane_guard import is_worker_prompt  # noqa: WPS433

            worker_lane = is_worker_prompt(text or "")
        except Exception:
            worker_lane = False
    if worker_lane or "[GOAL1_HEALTHY_DRAIN]" in (text or ""):
        from worker_inject_lib import inject_worker_prompt  # noqa: WPS433

        mode = "worker_chat" if os.environ.get("SINA_WORKER_CHAT_RESUME_INJECT", "").strip().lower() in (
            "1",
            "true",
            "yes",
        ) else "inbox"
        return inject_worker_prompt(
            text,
            source="clipboard_safe_redirect",
            meta={"target": tgt},
            delivery_mode=mode,
        )
    if "[SINA_LIVE_MAINTAINER]" in (text or "") or "[SINA_ADVISOR]" in (text or ""):
        _log_block("live_or_advisor_tag", preview)
        return {
            "ok": False,
            "skipped": True,
            "blocked": True,
            "reason": "forbidden_inject_tag",
            "message": "Blocked — Live agents / advisor must not auto-paste into Cursor.",
        }
    if not _paste_allowed() and not allow_automation:
        _log_block("kill_switch", preview)
        return {
            "ok": False,
            "skipped": True,
            "blocked": True,
            "reason": "cursor_paste_disabled",
            "message": "Auto-paste into Cursor is disabled (hub may still run; nothing copied).",
        }

    from cursor_window_preflight_v1 import run_cursor_window_preflight  # noqa: WPS433

    preflight = run_cursor_window_preflight(caller="clipboard_safe_paste")
    if not preflight.get("ok"):
        return {"ok": False, "blocked": True, "reason": "cursor_preflight_failed", "preflight": preflight}
    if preflight.get("focus_steal_skipped"):
        return {
            "ok": True,
            "skipped": True,
            "blocked": False,
            "reason": "cursor_focus_steal_disabled",
            "message": "Research mode ON — Cursor not activated; copy from hub preview if needed.",
            "preflight": preflight,
        }

    backup = _read_clipboard()
    try:
        subprocess.run(["pbcopy"], input=(text or "").encode("utf-8"), check=False)
        delay = max(0.2, min(activate_delay, 2.0))
        script = f"""
        tell application "Cursor" to activate
        delay {delay}
        tell application "System Events"
          keystroke "v" using command down
          delay 0.2
          keystroke return
        end tell
        """
        proc = subprocess.run(["osascript", "-e", script], capture_output=True, text=True)
        if proc.returncode != 0:
            err = (proc.stderr or proc.stdout or "inject failed").strip()
            return {"ok": False, "error": err, "clipboard_only": True}
        return {"ok": True, "injected": True, "clipboard_restored": True}
    finally:
        _write_clipboard(backup)
