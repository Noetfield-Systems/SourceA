"""Detect system-wide performance, behavior, decision, and planner trends."""
from __future__ import annotations

from collections import Counter


def _direction(delta: float, *, threshold: float = 0.05) -> str:
    if delta > threshold:
        return "up"
    if delta < -threshold:
        return "down"
    return "flat"


def _half_delta(series: list[float]) -> float:
    if len(series) < 2:
        return 0.0
    mid = len(series) // 2
    first = series[:mid] or [0]
    second = series[mid:] or first
    return (sum(second) / len(second)) - (sum(first) / len(first))


def detect_trends(
    *,
    memory: list[dict],
    patterns: list[dict],
    decisions: list[dict],
    planner: dict,
    context: dict,
) -> list[dict]:
    trends: list[dict] = []

    success_series = [1.0 if r.get("status") == "success" else 0.0 for r in memory]
    perf_delta = _half_delta(success_series)
    trends.append(
        {
            "trend_type": "performance",
            "direction": _direction(perf_delta),
            "strength": round(min(1.0, abs(perf_delta)), 3),
            "detail": f"success_rate_delta={perf_delta:.3f}",
        }
    )

    type_counts = Counter(p.get("type") or "unknown" for p in patterns)
    dominant = type_counts.most_common(1)[0][0] if type_counts else "none"
    fail_weight = (type_counts.get("failure", 0) + type_counts.get("repetition", 0)) / max(len(patterns), 1)
    trends.append(
        {
            "trend_type": "behavior",
            "direction": "down" if fail_weight > 0.4 else "up" if dominant == "success" else "flat",
            "strength": round(min(1.0, fail_weight if fail_weight > 0.4 else type_counts.get("success", 0) / max(len(patterns), 1)), 3),
            "detail": f"dominant_pattern_type={dominant}",
        }
    )

    cause_counts = Counter(d.get("cause_type") or "unknown" for d in decisions)
    success_causes = cause_counts.get("success_cause", 0)
    failure_causes = cause_counts.get("failure_cause", 0)
    decision_delta = (success_causes - failure_causes) / max(len(decisions), 1)
    trends.append(
        {
            "trend_type": "decision",
            "direction": _direction(decision_delta, threshold=0.1),
            "strength": round(min(1.0, abs(decision_delta)), 3),
            "detail": f"success_causes={success_causes}, failure_causes={failure_causes}",
        }
    )

    planner_summary = planner.get("planner_context_summary") or {}
    context_planner = (context.get("planner_state") or {}).get("planner_context_summary") or {}
    top_action = planner_summary.get("top_action") or context_planner.get("top_action")
    top_score = planner_summary.get("top_score") or context_planner.get("top_score") or 0
    trends.append(
        {
            "trend_type": "planner",
            "direction": "up" if top_score and float(top_score) >= 80 else "flat",
            "strength": round(min(1.0, float(top_score) / 120 if top_score else 0), 3),
            "detail": f"top_action={top_action}, top_score={top_score}",
        }
    )

    system_health = (context.get("system_state") or {}).get("system_health")
    if system_health is not None:
        trends.append(
            {
                "trend_type": "operational_health",
                "direction": "up" if float(system_health) >= 0.7 else "down" if float(system_health) < 0.5 else "flat",
                "strength": round(abs(float(system_health) - 0.5) * 2, 3),
                "detail": f"system_health={system_health}",
            }
        )

    return trends
