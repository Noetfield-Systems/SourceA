"""D6 SSOT — ~/.sina/memory_git_bridge_v1.json"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
BRIDGE_SSOT_PATH = STATE_DIR / "memory_git_bridge_v1.json"
SCHEMA = "memory-git-bridge-v1"


def load_snapshot() -> dict:
    if not BRIDGE_SSOT_PATH.is_file():
        return {}
    try:
        data = json.loads(BRIDGE_SSOT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def load_canonical() -> dict:
    snap = load_snapshot()
    latest = snap.get("latest") or {}
    if latest.get("schema") == SCHEMA:
        return latest
    return {}


def write_canonical(*, canonical: dict, task_id: str = "default") -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    envelope = load_snapshot() if BRIDGE_SSOT_PATH.is_file() else {"schema": SCHEMA, "builds": {}}
    envelope["schema"] = SCHEMA
    envelope["generated_at"] = canonical.get("generated_at")
    envelope["path"] = str(BRIDGE_SSOT_PATH)
    envelope["latest"] = canonical
    envelope.setdefault("builds", {})[task_id] = canonical

    fd, tmp = tempfile.mkstemp(dir=str(STATE_DIR), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(envelope, fh, indent=2)
        os.replace(tmp, BRIDGE_SSOT_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
