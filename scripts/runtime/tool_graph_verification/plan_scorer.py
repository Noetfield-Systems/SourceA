"""Weighted plan score from validation components + historical consistency."""
from __future__ import annotations

from collections import Counter


def historical_consistency_score(*, execution_path: list[dict], memory: list[dict]) -> float:
    path_tools = [step.get("tool_id") for step in execution_path if step.get("tool_id")]
    if not path_tools or not memory:
        return 0.5

    memory_actions = [r.get("action_id") for r in memory if r.get("action_id")]
    if not memory_actions:
        return 0.5

    pair_counts: Counter[tuple[str, str]] = Counter()
    for i in range(1, len(memory_actions)):
        pair_counts[(memory_actions[i - 1], memory_actions[i])] += 1

    hits = 0
    checks = 0
    for i in range(1, len(path_tools)):
        checks += 1
        if pair_counts.get((path_tools[i - 1], path_tools[i]), 0) > 0:
            hits += 1

    action_hits = sum(1 for t in path_tools if t in memory_actions)
    action_ratio = action_hits / len(path_tools)
    pair_ratio = hits / max(checks, 1)
    return round(min(1.0, action_ratio * 0.55 + pair_ratio * 0.45), 3)


def structural_integrity_score(
    *,
    cycle_detected: bool,
    topologically_valid: bool,
    goal_last: bool,
    estimated_steps: int,
) -> float:
    score = 1.0
    if cycle_detected:
        score -= 0.5
    if not topologically_valid:
        score -= 0.35
    if not goal_last:
        score -= 0.25
    if estimated_steps < 1:
        score -= 0.4
    return round(max(0.0, score), 3)


def compute_plan_score(
    *,
    dependency_validity_score: float,
    context_alignment_score: float,
    historical_consistency: float,
    structural_integrity: float,
) -> dict:
    plan_score = round(
        dependency_validity_score * 0.30
        + context_alignment_score * 0.25
        + historical_consistency * 0.20
        + structural_integrity * 0.25,
        3,
    )
    return {
        "plan_score": plan_score,
        "score_breakdown": {
            "dependency_validity": dependency_validity_score,
            "context_alignment": context_alignment_score,
            "historical_consistency": historical_consistency,
            "structural_integrity": structural_integrity,
            "weights": {
                "dependency_validity": 0.30,
                "context_alignment": 0.25,
                "historical_consistency": 0.20,
                "structural_integrity": 0.25,
            },
        },
    }
