"""Predict task success probability before execution (read-only v1 inputs)."""
from __future__ import annotations

from execution_intelligence.decision_memory import read_decisions
from execution_intelligence.pattern_engine.api import load_patterns_v1 as load_patterns
from execution_intelligence.reader import read_execution_memory


def _action_history(action_id: str, records: list[dict]) -> list[dict]:
    return [r for r in records if (r.get("action_id") or "") == action_id]


def predict_task(action_id: str, *, task_id: str | None = None) -> dict:
    records = read_execution_memory()
    patterns = load_patterns()
    decisions = read_decisions(limit=200)
    hist = _action_history(action_id, records)

    success_n = sum(1 for r in hist if r.get("status") == "success")
    fail_n = len(hist) - success_n
    total = len(hist)

    if total == 0:
        rate = 0.5
        risk_factors = ["no_history — neutral prior"]
    else:
        rate = success_n / total
        risk_factors = []
        if fail_n >= 2:
            risk_factors.append(f"{fail_n} prior failure(s) on this action")
        last = hist[-1] if hist else {}
        if last.get("status") != "success":
            risk_factors.append(f"last run failed: {last.get('error_signature') or 'exit non-zero'}")

    from execution_intelligence.pattern_engine.helpers import pattern_matches_action

    fail_patterns = [p for p in patterns if p.get("type") == "failure" and pattern_matches_action(p, action_id)]
    for p in fail_patterns[:3]:
        risk_factors.append(f"failure pattern freq={p.get('frequency')}: {(p.get('signature') or '')[:60]}")

    similar = []
    for r in hist[-8:]:
        similar.append(
            {
                "task_id": r.get("task_id"),
                "status": r.get("status"),
                "timestamp": r.get("timestamp"),
                "execution_time_ms": r.get("execution_time_ms"),
            }
        )
    for d in decisions:
        if d.get("action_id") == action_id:
            similar.append({"decision_id": d.get("decision_id"), "why": d.get("why"), "outcome": d.get("outcome")})
            if len(similar) >= 12:
                break

    return {
        "task_id": task_id or f"predict:{action_id}",
        "action_id": action_id,
        "predicted_success_rate": round(rate, 3),
        "sample_size": total,
        "risk_factors": risk_factors[:8],
        "similar_past_cases": similar[:10],
    }


def predict_all(action_ids: list[str]) -> list[dict]:
    return [predict_task(aid) for aid in action_ids]
