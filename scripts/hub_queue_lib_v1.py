#!/usr/bin/env python3
"""Shared fcntl-safe queue append. Used by server AND lib — one writer pattern."""
from __future__ import annotations

import fcntl
import json
import time
from pathlib import Path

QUEUE = Path.home() / ".sina" / "hub-rebuild-queue-v1.jsonl"


def enqueue_rebuild(source: str = "", run_refresh: bool = False) -> None:
    QUEUE.parent.mkdir(parents=True, exist_ok=True)
    evt = {"ts": time.time(), "source": source, "run_refresh": run_refresh}
    with open(QUEUE, "a", encoding="utf-8") as f:
        fcntl.flock(f, fcntl.LOCK_EX)
        f.write(json.dumps(evt) + "\n")
        fcntl.flock(f, fcntl.LOCK_UN)
