"""Ranked next-task suggestions from predictions + history + system state."""
from __future__ import annotations

from execution_intelligence.planner_influence import avoid_actions, prefer_actions
from execution_intelligence_v2.prediction_engine import predict_task
from execution_intelligence_v2.risk_scoring import score_risk
from execution_intelligence_v2.types import DEFAULT_CANDIDATE_ACTIONS


def recommend_tasks(
    action_ids: list[str] | None = None,
    *,
    system_state: dict | None = None,
) -> dict:
    candidates = action_ids or list(DEFAULT_CANDIDATE_ACTIONS)
    avoid = set(avoid_actions())
    prefer = set(prefer_actions())
    state = system_state or {}

    recs: list[dict] = []
    for aid in candidates:
        pred = predict_task(aid)
        risk = score_risk(aid)
        score = pred["predicted_success_rate"] * 100
        score -= risk["risk_score"] * 45
        if aid in prefer:
            score += 15
        if aid in avoid:
            score -= 25

        reasons = []
        if aid in prefer:
            reasons.append("historical success pattern")
        if aid in avoid:
            reasons.append("in avoid list — elevated failure history")
        if risk["risk_type"] == "high":
            reasons.append(f"high risk ({risk['risk_score']})")
        elif pred["predicted_success_rate"] >= 0.7:
            reasons.append(f"predicted success {pred['predicted_success_rate']:.0%}")
        if not reasons:
            reasons.append("neutral — limited history")

        recs.append(
            {
                "action_id": aid,
                "priority_score": round(max(0, min(100, score)), 1),
                "reason": "; ".join(reasons),
                "predicted_success_rate": pred["predicted_success_rate"],
                "risk_type": risk["risk_type"],
            }
        )

    recs.sort(key=lambda x: -x["priority_score"])
    return {
        "recommended_tasks": recs,
        "system_state_hint": {
            "p0": state.get("p0_id"),
            "drift_count": state.get("drift_count"),
        },
    }
