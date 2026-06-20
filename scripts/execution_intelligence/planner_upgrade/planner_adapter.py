"""Planner-facing recommendations from ranked history + signals."""
from __future__ import annotations

from execution_intelligence.planner_upgrade.history_ranker import rank_actions
from execution_intelligence.planner_upgrade.outcome_evaluator import evaluate_outcomes
from execution_intelligence.planner_upgrade.planner_context import (
    build_planner_context_package,
    load_decisions_readonly,
    load_patterns_readonly,
    load_signals_readonly,
)
from execution_intelligence.planner_upgrade.signal_consumer import consume_signals

AVOID_RISK_THRESHOLD = 0.55
RECOMMEND_CONFIDENCE_MIN = 0.45
RECOMMEND_HISTORICAL_MIN = 0.5


def build_recommendation(*, candidate_actions: list[str] | None = None) -> dict:
    patterns = load_patterns_readonly()
    decisions = load_decisions_readonly()
    signals = load_signals_readonly()
    context_pkg = build_planner_context_package(candidate_actions=candidate_actions)

    action_ids = context_pkg["candidate_actions"]
    if candidate_actions:
        action_ids = sorted(set(candidate_actions) | set(action_ids))

    signal_weights = consume_signals(signals)
    ranked = rank_actions(action_ids, patterns=patterns, decisions=decisions, signal_weights=signal_weights)
    outcomes = evaluate_outcomes(action_ids, patterns=patterns, decisions=decisions, signals=signals)
    outcome_by_action = {o["action_id"]: o for o in outcomes}

    avoid_actions: list[str] = []
    for row in ranked:
        aid = row["action_id"]
        outcome = outcome_by_action.get(aid) or {}
        if row.get("avoid") or outcome.get("risk_score", 0) >= AVOID_RISK_THRESHOLD:
            avoid_actions.append(aid)

    recommended_actions: list[str] = []
    for row in ranked:
        aid = row["action_id"]
        if aid in avoid_actions:
            continue
        outcome = outcome_by_action.get(aid) or {}
        if (
            row.get("prefer")
            or row.get("reinforce")
            or outcome.get("historical_score", 0) >= RECOMMEND_HISTORICAL_MIN
            and outcome.get("confidence", 0) >= RECOMMEND_CONFIDENCE_MIN
        ):
            recommended_actions.append(aid)

    ranked_actions = []
    for row in ranked:
        aid = row["action_id"]
        outcome = outcome_by_action.get(aid) or {}
        ranked_actions.append(
            {
                **row,
                "historical_score": outcome.get("historical_score", 0),
                "risk_score": outcome.get("risk_score", 0),
                "confidence": outcome.get("confidence", 0),
                "recommended": aid in recommended_actions,
                "avoid": aid in avoid_actions,
            }
        )

    return {
        "recommended_actions": recommended_actions,
        "avoid_actions": sorted(set(avoid_actions)),
        "ranked_actions": ranked_actions,
        "outcome_evaluations": outcomes,
        "context_package": context_pkg,
        "signals_consumed": len(signals),
    }
