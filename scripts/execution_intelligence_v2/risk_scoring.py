"""Failure likelihood, repetition risk, unstable action detection."""
from __future__ import annotations

from execution_intelligence.pattern_engine.api import load_patterns_v1 as load_patterns
from execution_intelligence.reader import read_execution_memory
from execution_intelligence_v2.prediction_engine import predict_task


def _unstable(action_id: str, records: list[dict]) -> bool:
    hist = [r.get("status") for r in records if r.get("action_id") == action_id][-6:]
    if len(hist) < 3:
        return False
    flips = sum(1 for i in range(1, len(hist)) if hist[i] != hist[i - 1])
    return flips >= 2


def score_risk(action_id: str, *, task_id: str | None = None) -> dict:
    records = read_execution_memory()
    patterns = load_patterns()
    pred = predict_task(action_id, task_id=task_id)

    failure_likelihood = 1.0 - pred["predicted_success_rate"]
    blocking: list[str] = []

    fail_pats = [p for p in patterns if p.get("type") == "failure" and p.get("action_id") in (action_id, "*")]
    repetition = 0.0
    for p in fail_pats:
        freq = p.get("frequency", 0)
        if freq >= 2:
            repetition = max(repetition, min(1.0, freq / 10))
            blocking.append(p.get("pattern_id", ""))

    unstable = _unstable(action_id, records)
    unstable_penalty = 0.15 if unstable else 0.0

    risk_score = min(1.0, failure_likelihood * 0.55 + repetition * 0.35 + unstable_penalty)
    if risk_score < 0.35:
        risk_type = "low"
    elif risk_score < 0.65:
        risk_type = "medium"
    else:
        risk_type = "high"

    factors = []
    if repetition > 0.2:
        factors.append("repetition_risk")
    if unstable:
        factors.append("unstable_action")
    if failure_likelihood > 0.5:
        factors.append("high_failure_likelihood")

    return {
        "task_id": task_id or f"risk:{action_id}",
        "action_id": action_id,
        "risk_score": round(risk_score, 3),
        "risk_type": risk_type,
        "blocking_patterns": [b for b in blocking if b][:6],
        "risk_factors": factors,
        "failure_likelihood": round(failure_likelihood, 3),
        "repetition_risk": round(repetition, 3),
        "unstable": unstable,
    }


def score_all(action_ids: list[str]) -> list[dict]:
    return [score_risk(aid) for aid in action_ids]
