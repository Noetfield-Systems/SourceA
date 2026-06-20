"""Resolve competing next-step candidates by weighted score."""
from __future__ import annotations

from collections import Counter


def historical_success_rate(tool_id: str, memory: list[dict]) -> float:
    runs = [r for r in memory if r.get("action_id") == tool_id]
    if not runs:
        return 0.5
    ok = sum(1 for r in runs if r.get("status") == "success")
    return round(ok / len(runs), 3)


def score_candidate(
    *,
    tool_id: str,
    policy: dict,
    memory: list[dict],
) -> dict:
    context = float(policy.get("context_alignment_score") or 0)
    safety = float(policy.get("safety_score") or 0)
    history = historical_success_rate(tool_id, memory)
    planner_raw = float(policy.get("planner_scores", {}).get(tool_id, 0))
    planner = min(1.0, planner_raw / 120) if planner_raw else (0.6 if tool_id in policy.get("recommended_actions", []) else 0.35)

    total = round(context * 0.30 + safety * 0.25 + history * 0.25 + planner * 0.20, 3)
    return {
        "tool_id": tool_id,
        "score": total,
        "breakdown": {
            "context": round(context * 0.30, 3),
            "safety": round(safety * 0.25, 3),
            "history": round(history * 0.25, 3),
            "planner": round(planner * 0.20, 3),
        },
    }


def resolve_priority(
    *,
    candidates: list[str],
    policy: dict,
    memory: list[dict],
) -> dict | None:
    if not candidates:
        return None
    scored = [score_candidate(tool_id=c, policy=policy, memory=memory) for c in candidates]
    scored.sort(key=lambda x: (-x["score"], x["tool_id"]))
    return scored[0]
