"""Rough token estimates — char/4 heuristic (no tokenizer dep)."""
from __future__ import annotations


def estimate_tokens(text: str) -> int:
    raw = (text or "").strip()
    if not raw:
        return 0
    return max(1, len(raw) // 4)


def trim_to_token_budget(text: str, limit: int) -> str:
    if limit <= 0:
        return ""
    raw = (text or "").strip()
    if estimate_tokens(raw) <= limit:
        return raw
    # Shrink by chars proportional to token overshoot
    target_chars = max(40, limit * 4)
    clipped = raw[:target_chars].rsplit("\n", 1)[0].strip()
    if not clipped:
        clipped = raw[:target_chars].strip()
    suffix = " …[budget-trimmed]"
    if len(clipped) + len(suffix) > target_chars:
        clipped = clipped[: max(0, target_chars - len(suffix))]
    return clipped + suffix
