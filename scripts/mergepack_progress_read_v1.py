#!/usr/bin/env python3
"""Mergepack PROGRAM_PROGRESS.json — non-blocking read for SourceA build paths (sa-0523)."""
from __future__ import annotations

import json
from pathlib import Path

MERGEPACK_PROGRESS_PATH = Path.home() / "Desktop/mergepack/PROGRAM_PROGRESS.json"


def read_mergepack_progress_safe(path: Path | None = None) -> dict:
    """Read mergepack progress JSON; never raise — empty data when absent or invalid."""
    target = path or MERGEPACK_PROGRESS_PATH
    if not target.is_file():
        return {"ok": False, "missing": True, "path": str(target), "data": {}}
    try:
        raw = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "missing": False, "error": str(exc), "path": str(target), "data": {}}
    if not isinstance(raw, dict):
        return {"ok": False, "missing": False, "error": "not a dict", "path": str(target), "data": {}}
    return {"ok": True, "missing": False, "path": str(target), "data": raw}
