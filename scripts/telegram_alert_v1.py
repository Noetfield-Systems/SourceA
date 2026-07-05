#!/usr/bin/env python3
"""Shared Telegram alert helper for Railway / Kaizen / triage."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any


def telegram_configured() -> bool:
    return bool(
        os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
        and (
            os.environ.get("TELEGRAM_ALERT_CHAT_ID", "").strip()
            or os.environ.get("TELEGRAM_ALLOWED_CHAT_ID", "").strip()
        )
    )


def send_telegram_alert(text: str, *, parse_mode: str = "HTML") -> dict[str, Any]:
    token = os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    chat_id = (
        os.environ.get("TELEGRAM_ALERT_CHAT_ID", "").strip()
        or os.environ.get("TELEGRAM_ALLOWED_CHAT_ID", "").strip()
    )
    if not token or not chat_id:
        return {"ok": False, "skipped": True, "reason": "telegram_not_configured"}
    payload = {
        "chat_id": chat_id,
        "text": str(text)[:3900],
        "disable_web_page_preview": True,
    }
    if parse_mode:
        payload["parse_mode"] = parse_mode
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace") or "{}")
            return {
                "ok": bool(body.get("ok")),
                "message_id": (body.get("result") or {}).get("message_id"),
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "error": exc.read().decode("utf-8", errors="replace")[:300],
        }
