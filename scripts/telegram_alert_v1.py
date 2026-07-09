#!/usr/bin/env python3
"""Shared Telegram alert helper — SourceA ops lane only (TrustFieldBot → TELEGRAM_OPS_CHAT_ID).

NEVER @Gateway_A · NEVER Sina Gateway lane · see data/sourcea-telegram-lane-v1.json
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Any

FORBIDDEN_USERNAMES = ("gateway_a", "@gateway_a")


def _ops_token() -> str:
    return (
        os.environ.get("TELEGRAM_PRIMARY_BOT_TOKEN", "").strip()
        or os.environ.get("TELEGRAM_BOT_TOKEN", "").strip()
    )


def _ops_chat_id() -> str:
    return os.environ.get("TELEGRAM_OPS_CHAT_ID", "").strip()


def telegram_configured() -> bool:
    return bool(_ops_token() and _ops_chat_id())


def _assert_outbound_lane(text: str) -> dict[str, Any] | None:
    lower = str(text or "").lower()
    for name in FORBIDDEN_USERNAMES:
        if name in lower:
            return {"ok": False, "skipped": True, "reason": "forbidden_telegram_target", "target": name}
    return None


def send_telegram_alert(text: str, *, parse_mode: str = "HTML") -> dict[str, Any]:
    token = _ops_token()
    chat_id = _ops_chat_id()
    if not token or not chat_id:
        return {
            "ok": False,
            "skipped": True,
            "reason": "telegram_ops_not_configured",
            "hint": "Set TELEGRAM_OPS_CHAT_ID + TELEGRAM_PRIMARY_BOT_TOKEN only",
        }
    blocked = _assert_outbound_lane(text)
    if blocked:
        return blocked

    payload: dict[str, Any] = {
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
                "lane": "sourcea_ops_trustfield",
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "error": exc.read().decode("utf-8", errors="replace")[:300],
        }
