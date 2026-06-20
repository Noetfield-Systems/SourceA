"""Merge safety, planner, and verification policy (read-only)."""
from __future__ import annotations

CONTEXT_ALIGNMENT_MIN = 0.0
SAFETY_SCORE_MIN = 0.7


def policy_context(*, verified: dict, planner: dict, context: dict) -> dict:
    avoid = set((planner.get("recommendation") or {}).get("avoid_actions") or [])
    recommended = set((planner.get("recommendation") or {}).get("recommended_actions") or [])
    ranked = (planner.get("recommendation") or {}).get("ranked_actions") or []
    planner_scores = {r.get("action_id"): float(r.get("score") or 0) for r in ranked if r.get("action_id")}

    return {
        "avoid_actions": sorted(avoid),
        "recommended_actions": sorted(recommended),
        "planner_scores": planner_scores,
        "verification_recommendation": verified.get("recommendation"),
        "is_valid": verified.get("is_valid"),
        "cycle_detected": verified.get("cycle_detected"),
        "safety_score": float(verified.get("safety_score") or 0),
        "context_alignment_score": float(verified.get("context_alignment_score") or 0),
        "plan_score": float(verified.get("plan_score") or 0),
        "system_health": float((context.get("system_state") or {}).get("system_health") or 1.0),
    }


def evaluate_step(
    *,
    tool_id: str,
    policy: dict,
    dependencies_satisfied: bool,
) -> dict:
    reasons: list[str] = []
    blocked = False

    if policy.get("verification_recommendation") != "approve":
        blocked = True
        reasons.append(f"verification_not_approved:{policy.get('verification_recommendation')}")
    if not policy.get("is_valid"):
        blocked = True
        reasons.append("graph_not_valid")
    if policy.get("cycle_detected"):
        blocked = True
        reasons.append("cycle_risk")
    if tool_id in policy.get("avoid_actions", []):
        blocked = True
        reasons.append("planner_avoid")
    if float(policy.get("safety_score") or 0) < SAFETY_SCORE_MIN:
        blocked = True
        reasons.append("safety_below_threshold")
    if not dependencies_satisfied:
        blocked = True
        reasons.append("dependency_unsatisfied")
    if float(policy.get("context_alignment_score") or 0) < CONTEXT_ALIGNMENT_MIN:
        pass  # threshold 0.0 — informational only at v1

    return {
        "allowed": not blocked,
        "blocked": blocked,
        "reasons": reasons,
    }
