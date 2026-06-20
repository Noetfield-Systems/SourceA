#!/usr/bin/env python3
"""Detect Worker Hub (H1) mode — legacy Sina Command app.js retired."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKER_HUB_BOOT = ROOT / "agent-control-panel" / "worker-hub" / "boot.json"


def worker_hub_mode() -> bool:
    if not WORKER_HUB_BOOT.is_file():
        return False
    try:
        row = json.loads(WORKER_HUB_BOOT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return bool(row.get("command_retired_forever") or row.get("hub_mode") == "worker-only")
