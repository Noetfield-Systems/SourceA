"""Fallback paths from repair loop recovery suggestions."""
from __future__ import annotations

from runtime.multi_step_planner.planner_store import load_json, INPUT_PATHS


def build_fallback_paths(*, task_id: str) -> list[dict]:
    repair_store = load_json(INPUT_PATHS["repair"])
    repairs = repair_store.get("repairs") or {}
    repair = repairs.get(task_id) or repair_store.get("latest") or {}
    suggestions = repair.get("recovery_suggestions") or []

    fallbacks: list[dict] = []
    for sug in suggestions:
        steps = sug.get("steps") or []
        fallbacks.append(
            {
                "path_id": sug.get("path_id") or "fallback",
                "title": sug.get("title") or "",
                "trigger": repair.get("failure_class") or "runtime_failure",
                "steps": steps,
                "confidence": sug.get("confidence", 0),
                "rationale": sug.get("rationale") or "",
            }
        )
    return fallbacks[:5]
