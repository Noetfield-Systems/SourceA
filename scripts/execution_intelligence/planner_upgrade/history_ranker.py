"""Rank actions using historical patterns, decisions, and signal weights."""
from __future__ import annotations

from execution_intelligence.pattern_engine.helpers import action_from_pattern


def _action_from_decision(decision: dict) -> str:
    if decision.get("action_id"):
        return str(decision["action_id"])
    why = decision.get("why_summary") or ""
    if why.startswith("'") and "'" in why[1:]:
        return why[1 : why.index("'", 1)]
    return ""


def _history_component(action_id: str, patterns: list[dict], decisions: list[dict]) -> dict:
    success_score = 0.0
    failure_score = 0.0
    pattern_conf_sum = 0.0
    pattern_conf_n = 0
    decision_conf_sum = 0.0
    decision_conf_n = 0

    for pattern in patterns:
        act = action_from_pattern(pattern)
        if act != action_id:
            continue
        freq = float(pattern.get("frequency") or 0)
        conf = float(pattern.get("confidence") or 0)
        ptype = pattern.get("type") or ""
        pattern_conf_sum += conf
        pattern_conf_n += 1
        if ptype == "success":
            success_score += freq * conf * 15
        elif ptype == "failure":
            failure_score += freq * conf * 15
        elif ptype == "repetition":
            failure_score += freq * conf * 5

    for decision in decisions:
        if _action_from_decision(decision) != action_id:
            continue
        conf = float(decision.get("confidence") or 0)
        decision_conf_sum += conf
        decision_conf_n += 1
        cause = decision.get("cause_type") or ""
        if cause == "success_cause":
            success_score += conf * 20
        elif cause == "failure_cause":
            failure_score += conf * 25
        elif cause == "fix_cause":
            success_score += conf * 10
        elif cause == "constraint":
            failure_score += conf * 8

    avg_pattern_conf = pattern_conf_sum / max(pattern_conf_n, 1)
    avg_decision_conf = decision_conf_sum / max(decision_conf_n, 1)

    return {
        "success_score": round(success_score, 2),
        "failure_score": round(failure_score, 2),
        "history_delta": round(success_score - failure_score, 2),
        "pattern_confidence": round(avg_pattern_conf, 3),
        "decision_confidence": round(avg_decision_conf, 3),
    }


def rank_actions(
    action_ids: list[str],
    *,
    patterns: list[dict],
    decisions: list[dict],
    signal_weights: dict[str, dict],
    base_score: float = 50.0,
) -> list[dict]:
    ranked: list[dict] = []
    for action_id in action_ids:
        hist = _history_component(action_id, patterns, decisions)
        sig = signal_weights.get(action_id) or {}
        signal_score = float(sig.get("signal_score") or 0)
        total = base_score + hist["history_delta"] + signal_score

        ranked.append(
            {
                "action_id": action_id,
                "score": round(total, 2),
                "base_score": base_score,
                "history_delta": hist["history_delta"],
                "signal_score": signal_score,
                "success_score": hist["success_score"],
                "failure_score": hist["failure_score"],
                "pattern_confidence": hist["pattern_confidence"],
                "decision_confidence": hist["decision_confidence"],
                "prefer": bool(sig.get("prefer_weight")),
                "avoid": bool(sig.get("avoid_weight")),
                "reinforce": bool(sig.get("reinforce_weight")),
                "deprioritize": bool(sig.get("deprioritize_weight")),
            }
        )

    ranked.sort(key=lambda r: (-r["score"], r["action_id"]))
    return ranked
