#!/usr/bin/env python3
"""Fail-closed guard: Worker prompts and disk snapshots must not steer Prompt feed / Sina Command.

Law: AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md · INCIDENT-034 (positive disk, not ban tables).
"""
from __future__ import annotations

import re
from typing import Any

STALE_STEER = re.compile(
    r"Prompt\s+feed|prompt-feed|prompt_feed|Sina\s+Command\s*→\s*Prompt|Confirm\s+auto-send",
    re.I,
)

STALE_ADVISORY = frozenset({"prompt_feed", "prompt_feed_live_mirror"})

POSITIVE_CLOSE = (
    "Worker chat: RUN INBOX one sa/turn. Optional: Worker Hub http://127.0.0.1:13020/ "
    "→ Form · Safety · H2 machines. Quote factory_now_line from truth bundle."
)


class WorkerSteerViolation(Exception):
    def __init__(self, detail: str, *, match: str | None = None) -> None:
        self.match = match
        super().__init__(detail)


def find_stale_steer(text: str) -> re.Match[str] | None:
    if not text:
        return None
    return STALE_STEER.search(text)


def assert_worker_prompt_clean(text: str, *, context: str = "worker_prompt") -> None:
    m = find_stale_steer(text)
    if m:
        raise WorkerSteerViolation(
            f"{context}: stale daily steer ({m.group()!r}) — rebuild via build_turn_prompt + live disk",
            match=m.group(),
        )


def guard_worker_prompt(text: str, *, context: str = "worker_prompt") -> str:
    """Return text if clean; raise WorkerSteerViolation if stale steer detected."""
    assert_worker_prompt_clean(text, context=context)
    return text


def broker_inbox_snapshot(inbox: dict[str, Any]) -> dict[str, Any]:
    """Broker/cache writes must not persist full prompt bodies (re-infection vector)."""
    if not isinstance(inbox, dict):
        return {}
    return {
        k: inbox.get(k)
        for k in (
            "ok",
            "pending",
            "delivered_at",
            "source",
            "meta",
            "sa_id",
            "queue_role",
            "queue",
            "chars",
        )
        if k in inbox
    }


def heal_execution_lane_row(row: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    changed = False
    if not isinstance(row, dict):
        return row, False
    adv = row.get("advisory")
    if adv in STALE_ADVISORY:
        row = dict(row)
        row["advisory"] = "live_next10_mirror"
        changed = True
    if row.pop("prompt_feed_lane", None):
        row["next_steps_lane"] = row.get("next_steps_lane") or "advisory_only"
        changed = True
    return row, changed


def heal_truth_row(row: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    if not isinstance(row, dict):
        return row, False
    changed = False
    if row.pop("prompt_feed_lane", None):
        row = dict(row)
        row["next_steps_lane"] = row.get("next_steps_lane") or "advisory_only"
        changed = True
    row, adv_changed = heal_execution_lane_row(row)
    return row, changed or adv_changed
