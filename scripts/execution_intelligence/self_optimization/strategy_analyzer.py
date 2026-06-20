"""Analyze strategy performance trends per action (read-only)."""
from __future__ import annotations

from collections import defaultdict


def _half_trend(values: list[float]) -> tuple[str, float]:
    if len(values) < 2:
        return "flat", 0.0
    mid = len(values) // 2
    first = values[:mid] or [0]
    second = values[mid:] or first
    avg_first = sum(first) / len(first)
    avg_second = sum(second) / len(second)
    delta = avg_second - avg_first
    if abs(delta) < 0.05:
        return "flat", round(abs(delta), 3)
    return ("improving" if delta > 0 else "degrading"), round(min(1.0, abs(delta)), 3)


def analyze_strategies(*, memory: list[dict], performance: list[dict]) -> list[dict]:
    runs_by_action: dict[str, list[dict]] = defaultdict(list)
    for rec in memory:
        act = rec.get("action_id") or "unknown"
        runs_by_action[act].append(rec)

    strategies: list[dict] = []
    for row in performance:
        action_id = row["action_id"]
        action_runs = runs_by_action.get(action_id, [])
        success_series = [1.0 if r.get("status") == "success" else 0.0 for r in action_runs]
        trend, strength = _half_trend(success_series)

        if row["success_rate"] >= 0.7 and row["stability_score"] >= 0.6:
            label = "successful"
        elif row["failure_rate"] >= 0.5:
            label = "failing"
        elif trend == "improving":
            label = "improving"
        elif trend == "degrading":
            label = "degrading"
        else:
            label = "neutral"

        confidence = round(
            min(
                1.0,
                (row["success_rate"] * 0.35)
                + (row["stability_score"] * 0.25)
                + (row["decision_quality"] * 0.2)
                + (row["planner_quality"] * 0.2),
            ),
            3,
        )

        strategies.append(
            {
                "strategy_id": f"action:{action_id}",
                "action_id": action_id,
                "trend": trend,
                "label": label,
                "confidence": confidence,
            }
        )

    strategies.sort(key=lambda s: (-s["confidence"], s["action_id"]))
    return strategies
