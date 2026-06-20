"""Failure → fix relationship builder (patterns + timeline)."""
from __future__ import annotations

from execution_intelligence.pattern_engine.helpers import action_from_pattern


def link_fixes(patterns: list[dict], records: list[dict]) -> list[dict]:
    fix_patterns = [p for p in patterns if p.get("type") == "fix"]
    links: list[dict] = []

    for p in fix_patterns:
        action = action_from_pattern(p)
        links.append(
            {
                "action_id": action,
                "failure_signal": (p.get("input_pattern") or "").split("failed_with:")[-1][:120],
                "recovery_signal": p.get("output_pattern") or p.get("signature") or "",
                "pattern_id": p.get("pattern_id"),
                "confidence": p.get("confidence", 0),
                "related_task_ids": p.get("related_task_ids") or [],
            }
        )

    by_action: dict[str, list[dict]] = {}
    for rec in sorted(records, key=lambda r: r.get("timestamp") or ""):
        act = rec.get("action_id") or "unknown"
        by_action.setdefault(act, []).append(rec)

    for action, recs in by_action.items():
        prior_fail = None
        for rec in recs:
            if rec.get("status") != "success":
                prior_fail = rec
            elif prior_fail is not None:
                links.append(
                    {
                        "action_id": action,
                        "failure_signal": (prior_fail.get("error_signature") or "failure")[:120],
                        "recovery_signal": f"success:{rec.get('task_id', '')}",
                        "pattern_id": "",
                        "confidence": 0.65,
                        "related_task_ids": [prior_fail.get("task_id"), rec.get("task_id")],
                    }
                )
                prior_fail = None

    return links
