"""Read-only access to execution spine memory."""
from __future__ import annotations

import json
from pathlib import Path

from execution_intelligence.types import MEMORY_FILENAME, STATE_DIR_NAME

MEMORY_PATH = Path.home() / STATE_DIR_NAME / MEMORY_FILENAME


def read_execution_memory() -> list[dict]:
    if not MEMORY_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in MEMORY_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def memory_line_count() -> int:
    if not MEMORY_PATH.is_file():
        return 0
    return sum(1 for ln in MEMORY_PATH.read_text(encoding="utf-8").splitlines() if ln.strip())
