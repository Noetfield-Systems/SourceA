"""Shared helpers for pattern dict consumers (read-only)."""
from __future__ import annotations


def action_from_pattern(pattern: dict) -> str:
    inp = pattern.get("input_pattern") or ""
    if inp.startswith("action:"):
        return inp.split("|", 1)[0].replace("action:", "").strip()
    if inp.startswith("actions:"):
        return inp.replace("actions:", "").split(",")[0].strip()
    return ""


def pattern_matches_action(pattern: dict, action_id: str) -> bool:
    act = action_from_pattern(pattern)
    if act and act == action_id:
        return True
    inp = pattern.get("input_pattern") or ""
    return action_id in inp
