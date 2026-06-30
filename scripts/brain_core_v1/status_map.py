"""Deterministic live-status helpers for Brain Core v1."""
from __future__ import annotations

from typing import Any, Mapping

UNKNOWN = "unknown"
OK = "ok"
DEGRADED = "degraded"
UNAVAILABLE = "unavailable"

OK_VALUES = {"ok", "pass", "passed", "green", "healthy", "available", "live", "up", "true", True}
DEGRADED_VALUES = {"degraded", "amber", "slow", "partial", "warning", "warn"}
UNAVAILABLE_VALUES = {"unavailable", "down", "offline", "fail", "failed", "block", "blocked", "false", False}

ROUTE_STATUS_KEYS = ("route_or_tool_status", "tool_status", "route_status", "path_status")


def normalize_status(value: Any) -> str:
    """Return the canonical status string used by Decision Core."""
    if isinstance(value, Mapping):
        return normalize_status(value.get("status", value.get("value", value.get("ok"))))
    if value in OK_VALUES:
        return OK
    if value in UNAVAILABLE_VALUES:
        return UNAVAILABLE
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered in OK_VALUES:
            return OK
        if lowered in DEGRADED_VALUES:
            return DEGRADED
        if lowered in UNAVAILABLE_VALUES:
            return UNAVAILABLE
    return UNKNOWN


def resolve_status_key(raw_key: str | None, live_status_map: Mapping[str, Any]) -> str | None:
    """Resolve placeholder route/tool status keys to the concrete provided key."""
    if raw_key != "relevant_route_or_tool_status":
        return raw_key
    for key in ROUTE_STATUS_KEYS:
        if key in live_status_map:
            return key
    return ROUTE_STATUS_KEYS[0]


def get_status(live_status_map: Mapping[str, Any] | None, status_key: str | None) -> str:
    """Return canonical status for a key, defaulting to unknown."""
    if not live_status_map or not status_key:
        return UNKNOWN
    return normalize_status(live_status_map.get(status_key, UNKNOWN))


def ladder_for_status(status: str, *, requires_status_signal: bool) -> str:
    """Map a canonical status to a public response gear."""
    if not requires_status_signal:
        return "confident"
    if status == OK:
        return "confident"
    if status in {DEGRADED, UNAVAILABLE}:
        return "degraded"
    return "unsure"
