#!/usr/bin/env python3
"""Resolve active cloud drain queue SSOT path (batch pointer · locked)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ACTIVE_POINTER = ROOT / "data/cloud-drain-queue-active-v1.json"
LEGACY = ROOT / "data/secondary-cloud-drain-next-100-v1.json"


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def active_drain_path() -> Path:
    ptr = _read(ACTIVE_POINTER)
    rel = str(ptr.get("queue_path") or "").strip()
    if rel:
        return ROOT / rel
    return LEGACY


def active_batch_meta() -> dict:
    ptr = _read(ACTIVE_POINTER)
    if ptr:
        return ptr
    leg = _read(LEGACY)
    return {"batch_id": 1, "queue_path": str(LEGACY.relative_to(ROOT)), "locked": False, "legacy": True, **leg}
