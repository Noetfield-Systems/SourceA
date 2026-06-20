"""Group execution records by outcome (read-only)."""
from __future__ import annotations


def classify_records(records: list[dict]) -> dict[str, list[dict]]:
    buckets: dict[str, list[dict]] = {"success": [], "failure": []}
    for rec in records:
        status = rec.get("status") or ""
        if status == "success":
            buckets["success"].append(rec)
        else:
            buckets["failure"].append(rec)
    return buckets


def group_by_action(records: list[dict]) -> dict[str, list[dict]]:
    out: dict[str, list[dict]] = {}
    for rec in records:
        action = (rec.get("action_id") or rec.get("producer") or "unknown").strip()
        out.setdefault(action, []).append(rec)
    return out
