"""Token budget policy for D14 — rule-based caps per goal class."""
from __future__ import annotations

import os

DEFAULT_TOKEN_LIMIT = 4096

_GOAL_LIMITS: dict[str, int] = {
    "build": 5120,
    "fix": 3584,
    "refactor": 4608,
    "explore": 3072,
    "other": DEFAULT_TOKEN_LIMIT,
}


def resolve_token_limit(*, goal_class: str | None, explicit: int | None = None) -> int:
    if explicit and explicit > 0:
        return int(explicit)
    env = os.environ.get("SINA_COMPRESSION_TOKEN_LIMIT", "").strip()
    if env.isdigit() and int(env) > 0:
        return int(env)
    gc = (goal_class or "other").strip().lower()
    return _GOAL_LIMITS.get(gc, DEFAULT_TOKEN_LIMIT)
