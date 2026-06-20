"""Convert optimization candidates into persistent recommendations."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


TYPE_MAP = {
    "increase_preference_weight": "prefer_weight_up",
    "decrease_preference_weight": "prefer_weight_down",
    "raise_confidence_threshold": "confidence_threshold_up",
    "lower_confidence_threshold": "confidence_threshold_down",
    "prioritize_action": "prioritize",
    "deprioritize_action": "deprioritize",
}


def generate_recommendations(candidates: list[dict]) -> list[dict]:
    recommendations: list[dict] = []
    for cand in candidates:
        opt_type = cand.get("optimization_type") or ""
        recommendations.append(
            {
                "recommendation_id": str(uuid.uuid4()),
                "recommendation_type": TYPE_MAP.get(opt_type, opt_type),
                "target": cand.get("target") or "",
                "reason": cand.get("reason") or "",
                "confidence": round(min(1.0, float(cand.get("confidence") or 0)), 3),
                "created_at": _now(),
                "executed": False,
            }
        )
    recommendations.sort(key=lambda r: (-r["confidence"], r["target"]))
    return recommendations
