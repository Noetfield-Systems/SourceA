#!/usr/bin/env python3
"""Shared n8n glue config — quarantine-aware URLs and webhooks."""
from __future__ import annotations

import json
import urllib.request
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
CONFIG_PATH = SINA / "n8n-glue-config-v1.json"
QUARANTINE_PATH = SINA / "sina-command-quarantine-v1.json"
RECEIPTS_ROOT = SINA / "n8n-receipts"

DEFAULT_CONFIG: dict[str, Any] = {
    "schema": "n8n-glue-config-v1",
    "hub_mode": "live",
    "urls": {
        "mac_health": "http://127.0.0.1:13024",
        "n8n": "http://127.0.0.1:5678",
        "n8n_integration": "http://127.0.0.1:13026",
        "chat_unify": "http://127.0.0.1:13023",
        "portfolio_mail": "http://127.0.0.1:13020/mail-hub/",
        "portfolio_mail_api": "http://127.0.0.1:13020/api/portfolio-mail/v1",
        "hub": "http://127.0.0.1:13020",
        "worker_hub": "http://127.0.0.1:13020/",
        "mac_law": "http://127.0.0.1:8781/",
        "runtime": "http://127.0.0.1:8000",
    },
    "webhooks": {
        "mac_health_cooldown": "http://127.0.0.1:5678/webhook/mac-health-cooldown",
        "product_signal": "http://127.0.0.1:5678/webhook/sinaai-product-signal",
        "chat_unify_merge": "http://127.0.0.1:5678/webhook/chat-unify-merge",
        "portfolio_mail_send": "http://127.0.0.1:5678/webhook/portfolio-mail-send",
    },
    "telegram_listener": "runtime",
    "cpu_pause_dry_run": True,
}


def _tcp_open(port: int, host: str = "127.0.0.1") -> bool:
    import socket

    try:
        with socket.create_connection((host, port), timeout=1.5):
            return True
    except OSError:
        return False


def detect_hub_mode() -> str:
    if QUARANTINE_PATH.is_file():
        return "quarantined"
    if not _tcp_open(13020):
        return "quarantined"
    try:
        req = urllib.request.Request("http://127.0.0.1:13020/health", method="GET")
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            if resp.status in (200, 201, 204):
                return "live"
    except OSError:
        pass
    return "quarantined"


def load_config(*, refresh_hub_mode: bool = True) -> dict[str, Any]:
    cfg: dict[str, Any]
    if CONFIG_PATH.is_file():
        try:
            cfg = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            cfg = dict(DEFAULT_CONFIG)
    else:
        cfg = dict(DEFAULT_CONFIG)
    cfg.setdefault("schema", "n8n-glue-config-v1")
    cfg.setdefault("urls", dict(DEFAULT_CONFIG["urls"]))
    cfg.setdefault("webhooks", dict(DEFAULT_CONFIG["webhooks"]))
    if refresh_hub_mode:
        cfg["hub_mode"] = detect_hub_mode()
    return cfg


def save_config(cfg: dict[str, Any]) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(cfg, indent=2), encoding="utf-8")


def receipt_path(track: str, workflow_id: str) -> Path:
    safe = workflow_id.replace("/", "-")
    return RECEIPTS_ROOT / track / f"{safe}.jsonl"
