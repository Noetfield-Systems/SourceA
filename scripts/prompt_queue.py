#!/usr/bin/env python3
"""Prompt queue REMOVED — ASF 2026-06-15. Stub keeps imports stable."""
from __future__ import annotations

REMOVED = "Prompt queue removed — use INBOX + live-ongoing-prompts SSOT."


def _load() -> dict:
    return {"session_id": "removed", "auto_feed": False, "items": [], "updated_at": None}


def _save(data: dict) -> None:
    pass


def set_auto_feed(enabled: bool) -> dict:
    return {"ok": True, "auto_feed": False, "removed": True, "message": REMOVED}


def queue_payload() -> dict:
    return {"ok": True, "removed": True, "items": [], "auto_feed": False, "message": REMOVED}


def handle_action(body: dict) -> dict:
    return {"ok": False, "error": REMOVED, "removed": True}
