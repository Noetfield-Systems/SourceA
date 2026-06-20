"""Evaluate per-action historical outcomes for planner decisions."""
from __future__ import annotations

from execution_intelligence.planner_upgrade.history_ranker import _history_component
from execution_intelligence.planner_upgrade.signal_consumer import consume_signals


def evaluate_outcomes(
    action_ids: list[str],
    *,
    patterns: list[dict],
    decisions: list[dict],
    signals: list[dict],
) -> list[dict]:
    signal_weights = consume_signals(signals)
    evaluations: list[dict] = []

    for action_id in action_ids:
        hist = _history_component(action_id, patterns, decisions)
        sig = signal_weights.get(action_id) or {}

        success = hist["success_score"]
        failure = hist["failure_score"]
        total = success + failure
        historical_score = success / total if total > 0 else 0.5

        avoid_w = float(sig.get("avoid_weight") or 0)
        deprioritize_w = float(sig.get("deprioritize_weight") or 0)
        risk_score = min(1.0, (failure / max(total, 1)) * 0.6 + avoid_w * 0.3 + deprioritize_w * 0.1)

        conf_parts = [hist["pattern_confidence"], hist["decision_confidence"]]
        if sig.get("reinforce_weight"):
            conf_parts.append(float(sig["reinforce_weight"]))
        if sig.get("prefer_weight"):
            conf_parts.append(float(sig["prefer_weight"]) * 0.8)
        non_zero = [c for c in conf_parts if c > 0]
        confidence = sum(non_zero) / len(non_zero) if non_zero else 0.35

        evaluations.append(
            {
                "action_id": action_id,
                "historical_score": round(historical_score, 3),
                "risk_score": round(risk_score, 3),
                "confidence": round(min(1.0, confidence), 3),
            }
        )

    evaluations.sort(key=lambda e: (-e["confidence"], -e["historical_score"], e["action_id"]))
    return evaluations
