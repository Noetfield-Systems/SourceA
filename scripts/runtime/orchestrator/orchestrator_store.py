"""Orchestrator SSOT."""
from __future__ import annotations

import json
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
ORCHESTRATOR_SSOT_PATH = STATE_DIR / "runtime_orchestrator_v1.json"


def load_snapshot() -> dict:
    if not ORCHESTRATOR_SSOT_PATH.is_file():
        return {}
    try:
        data = json.loads(ORCHESTRATOR_SSOT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def write_snapshot(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ORCHESTRATOR_SSOT_PATH.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")
