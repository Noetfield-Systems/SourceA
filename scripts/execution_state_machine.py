#!/usr/bin/env python3
"""Deterministic task state machine — single spine contract for SourceA + FORGE port."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# Runtime states (REGISTRY uses backlog/done; runtime SM governs in-flight work)
STATES = frozenset({"queued", "scheduled", "running", "verifying", "done", "failed"})

TRANSITIONS: dict[str, frozenset[str]] = {
    "queued": frozenset({"scheduled", "failed"}),
    "scheduled": frozenset({"running", "queued", "failed"}),
    "running": frozenset({"verifying", "done", "failed", "queued"}),
    "verifying": frozenset({"done", "failed", "running"}),
    "done": frozenset(),
    "failed": frozenset({"queued", "scheduled"}),
}

TERMINAL = frozenset({"done"})


@dataclass
class TransitionResult:
    ok: bool
    from_state: str
    to_state: str
    error: str = ""
    idempotent: bool = False


def normalize_state(raw: str | None) -> str:
    s = (raw or "queued").strip().lower()
    return s if s in STATES else "queued"


def can_transition(from_state: str, to_state: str) -> bool:
    f = normalize_state(from_state)
    t = normalize_state(to_state)
    if f == t:
        return True
    return t in TRANSITIONS.get(f, frozenset())


def apply_transition(
    *,
    from_state: str,
    to_state: str,
    task_id: str = "",
    idempotency_key: str = "",
) -> TransitionResult:
    f = normalize_state(from_state)
    t = normalize_state(to_state)
    if f == t:
        return TransitionResult(ok=True, from_state=f, to_state=t, idempotent=True)
    if t not in TRANSITIONS.get(f, frozenset()):
        return TransitionResult(
            ok=False,
            from_state=f,
            to_state=t,
            error=f"invalid transition {f!r} -> {t!r} for task {task_id or '?'}",
        )
    return TransitionResult(ok=True, from_state=f, to_state=t)


def contract_export() -> dict[str, Any]:
    return {
        "schema": "execution-state-machine-v1",
        "states": sorted(STATES),
        "terminal": sorted(TERMINAL),
        "transitions": {k: sorted(v) for k, v in TRANSITIONS.items()},
        "invariant_loop": [
            "event",
            "context",
            "plan",
            "schedule",
            "execute",
            "diff",
            "verify",
            "persist",
            "next",
        ],
    }
