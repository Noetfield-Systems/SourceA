#!/usr/bin/env python3
"""Append-only live event feed for hub SSE (Track 2 L1)."""
from __future__ import annotations

import fcntl
import json
import time
from pathlib import Path
from typing import Any

EVENTS = Path.home() / ".sina" / "hub-live-events-v1.jsonl"


def append_live_event(event_type: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    """Append one JSON line event. Returns the written event dict."""
    EVENTS.parent.mkdir(parents=True, exist_ok=True)
    evt = {
        "type": event_type,
        "ts": time.time(),
        **(payload or {}),
    }
    line = json.dumps(evt, ensure_ascii=False, separators=(",", ":")) + "\n"
    with open(EVENTS, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(line)
        fcntl.flock(f, fcntl.LOCK_UN)
    return evt


def tail_events(*, since_offset: int = 0, max_lines: int = 50) -> tuple[list[dict[str, Any]], int]:
    """Read events from byte offset; return (events, new_offset)."""
    if not EVENTS.is_file():
        return [], 0
    size = EVENTS.stat().st_size
    if since_offset > size:
        since_offset = 0
    events: list[dict[str, Any]] = []
    with open(EVENTS, encoding="utf-8") as f:
        f.seek(since_offset)
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError:
                continue
            if len(events) >= max_lines:
                break
        new_offset = f.tell()
    return events, new_offset
