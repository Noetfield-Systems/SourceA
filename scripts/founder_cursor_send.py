#!/usr/bin/env python3
"""Founder one-tap hub → Cursor (explicit click only; no background inject)."""
from __future__ import annotations

from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
MAC_SNAPSHOT_PROMPT = SOURCE_A / "MAC_SNAPSHOT_PROMPT.txt"


def load_mac_snapshot_prompt() -> str:
    if MAC_SNAPSHOT_PROMPT.is_file():
        return MAC_SNAPSHOT_PROMPT.read_text(encoding="utf-8").strip()
    return """MAC SNAPSHOT — run now

Read this as a standing order. Do not guess. Do not use old numbers from chat history.

1. Run: python3 ~/Desktop/SourceA/scripts/mac_performance_snapshot.py
2. If that fails, gather the same metrics manually (RAM, CPU load, top processes, grouped app RAM, GPU/display, thermal, disk, swap).
3. Reply with the full snapshot report only — real numbers from this exact moment.
4. End with 3 bullets: biggest RAM user, biggest lag risk, one action I can take without Terminal.

Format: plain English, MB and GB, timestamp at top."""


def send_mac_snapshot_to_cursor() -> dict:
    """Founder clicked Mac log in hub topbar — paste prompt into Cursor, one-way."""
    from clipboard_safe import clipboard_paste_into_cursor  # noqa: WPS433

    text = load_mac_snapshot_prompt()
    if not text.strip():
        return {"ok": False, "error": "mac_snapshot_prompt_missing"}
    # Explicit founder button — allow_automation bypasses hub kill-switch (not background inject).
    result = clipboard_paste_into_cursor(text, allow_automation=True, activate_delay=0.5)
    if result.get("ok"):
        return {
            "ok": True,
            "sent": True,
            "injected": bool(result.get("injected")),
            "message": "Mac snapshot prompt sent to Cursor — check your chat.",
            "chars": len(text),
        }
    if result.get("clipboard_only") or result.get("blocked"):
        try:
            import subprocess

            subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=False)
            return {
                "ok": True,
                "sent": True,
                "injected": False,
                "clipboard_only": True,
                "message": "Copied Mac snapshot prompt — paste into Cursor (Cmd+V).",
                "reason": result.get("reason") or result.get("message"),
                "chars": len(text),
            }
        except OSError as e:
            return {"ok": False, "error": str(e), "detail": result}
    return {"ok": False, "error": result.get("error") or result.get("message") or "send_failed", "detail": result}


def handle_founder_cursor_send(body: dict) -> dict:
    action = (body.get("action") or "mac_snapshot").strip()
    if action == "mac_snapshot":
        return send_mac_snapshot_to_cursor()
    return {"ok": False, "error": f"unknown_action:{action}"}
