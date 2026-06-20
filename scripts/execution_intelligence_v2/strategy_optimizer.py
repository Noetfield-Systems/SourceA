"""Combine prediction, risk, causal signals into execution strategy."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from execution_intelligence_v2.causal_linker import build_causal_links, causal_graph_summary
from execution_intelligence_v2.prediction_engine import predict_all
from execution_intelligence_v2.risk_scoring import score_all
from execution_intelligence_v2.task_recommender import recommend_tasks
from execution_intelligence_v2.types import DEFAULT_CANDIDATE_ACTIONS

STATE_PATH = Path.home() / ".sina" / "execution-strategy-v2.json"


def _load_system_state() -> dict:
    prog = Path.home() / "Desktop" / "SourceA" / "PROGRAM_PROGRESS.json"
    if not prog.is_file():
        return {}
    try:
        data = json.loads(prog.read_text(encoding="utf-8"))
        plans = data.get("parallel_plans") or []
        p0 = plans[0].get("id") if plans else None
        drift_path = Path.home() / "Desktop" / "SourceA" / "sina-bowl" / "DRIFT.json"
        drift_n = 0
        if drift_path.is_file():
            try:
                drift_data = json.loads(drift_path.read_text(encoding="utf-8"))
                drift_n = len(drift_data if isinstance(drift_data, list) else drift_data.get("items", []))
            except json.JSONDecodeError:
                drift_n = 0
        return {"p0_id": p0, "drift_count": drift_n, "updated_at": data.get("updated_at")}
    except (json.JSONDecodeError, OSError):
        return {}


def optimize_strategy(action_ids: list[str] | None = None) -> dict:
    candidates = action_ids or list(DEFAULT_CANDIDATE_ACTIONS)
    state = _load_system_state()
    predictions = predict_all(candidates)
    risks = score_all(candidates)
    recommendations = recommend_tasks(candidates, system_state=state)
    causal = build_causal_links()
    graph = causal_graph_summary()

    # Group: prompt-os engines vs other
    engine_group = [a for a in candidates if a.startswith("pos-")]
    plan_steps = []
    for item in recommendations["recommended_tasks"]:
        if item["action_id"] in engine_group:
            plan_steps.append(
                {
                    "step": len(plan_steps) + 1,
                    "action_id": item["action_id"],
                    "priority_score": item["priority_score"],
                    "strategy": "execute_when_risk_low" if item["risk_type"] != "high" else "defer_until_risk_mitigated",
                }
            )

    strategy = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "optimal_execution_plan": plan_steps,
        "task_groups": {
            "prompt_os_engines": {
                "actions": engine_group,
                "recommended_order": [x["action_id"] for x in recommendations["recommended_tasks"] if x["action_id"] in engine_group],
            }
        },
        "signals_combined": {
            "predictions": predictions,
            "risks": risks,
            "causal_top": causal[:8],
        },
        "summary": {
            "best_next_action": (recommendations["recommended_tasks"][0]["action_id"] if recommendations["recommended_tasks"] else None),
            "highest_risk_action": max(risks, key=lambda r: r["risk_score"])["action_id"] if risks else None,
            "highest_confidence_success": max(predictions, key=lambda p: p["predicted_success_rate"])["action_id"] if predictions else None,
        },
    }

    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(strategy, indent=2) + "\n", encoding="utf-8")
    return strategy


def planner_v2_signals(action_ids: list[str] | None = None) -> dict:
    candidates = action_ids or list(DEFAULT_CANDIDATE_ACTIONS)
    strategy = optimize_strategy(candidates)
    recs = recommend_tasks(candidates)
    return {
        "execution_intelligence_v2": {
            "predictions": strategy["signals_combined"]["predictions"],
            "risk_scores": strategy["signals_combined"]["risks"],
            "recommendations": recs["recommended_tasks"][:6],
            "causal_summary": causal_graph_summary(),
            "optimal_plan": strategy["optimal_execution_plan"][:6],
            "best_next_action": strategy["summary"]["best_next_action"],
            "planner_rules_v2": [
                "Use best_next_action when founder has not fixed blocking failure patterns.",
                "Skip actions with risk_type=high unless explicitly required.",
                "Weight predicted_success_rate over novelty.",
            ],
        }
    }
