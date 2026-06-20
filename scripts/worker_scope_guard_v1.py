#!/usr/bin/env python3
"""Block fat multi-hour Worker tasks — one INBOX turn only."""
from __future__ import annotations

FAT_MARKERS = (
    "validate-sourcea-e2e-full",
    "check and fix everything",
    "check e2e",
    "e2e check",
    "fix everything above",
    "full e2e",
    "e2e-full",
    "find_critical_bugs",
    "build-sina-command-panel",
    "validate-registry-1000",
    "finish-worker-1",
)


def check_fat_request(text: str) -> dict | None:
    """Return block dict if user message would hang Worker on full E2E."""
    low = (text or "").lower()
    if not low.strip():
        return None
    for marker in FAT_MARKERS:
        if marker in low:
            return {
                "ok": False,
                "blocked": True,
                "reason": "WORKER_FAT_TASK_FORBIDDEN",
                "marker": marker,
                "hint": (
                    "Worker does ONE queue turn only. Say **run inbox** — "
                    "never full E2E / fix-everything in Worker chat."
                ),
                "law": "HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md",
            }
    return None
