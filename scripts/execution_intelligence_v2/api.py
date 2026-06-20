"""Hub API — execution intelligence v2 (read-only)."""
from __future__ import annotations

from execution_intelligence_v2.causal_linker import build_causal_links, causal_graph_summary
from execution_intelligence_v2.prediction_engine import predict_all
from execution_intelligence_v2.risk_scoring import score_all
from execution_intelligence_v2.strategy_optimizer import optimize_strategy, planner_v2_signals
from execution_intelligence_v2.task_recommender import recommend_tasks
from execution_intelligence_v2.types import DEFAULT_CANDIDATE_ACTIONS


def intelligence_v2_payload(action_ids: list[str] | None = None) -> dict:
    candidates = action_ids or list(DEFAULT_CANDIDATE_ACTIONS)
    strategy = optimize_strategy(candidates)
    return {
        "ok": True,
        "version": 2,
        "predictions": predict_all(candidates),
        "risk_scores": score_all(candidates),
        "recommendations": recommend_tasks(candidates),
        "causal_links": build_causal_links()[:20],
        "causal_graph_summary": causal_graph_summary(),
        "strategy": {
            "optimal_execution_plan": strategy.get("optimal_execution_plan"),
            "summary": strategy.get("summary"),
        },
        "planner_signals": planner_v2_signals(candidates).get("execution_intelligence_v2"),
    }
