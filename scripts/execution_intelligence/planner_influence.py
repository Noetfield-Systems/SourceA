"""Planner influence — delegates to planner_upgrade v1 (read-only SSOT inputs)."""
from __future__ import annotations

from execution_intelligence.planner_upgrade import build_recommendation, run_planner_upgrade


def avoid_actions() -> list[str]:
    rec = build_recommendation()
    return rec["avoid_actions"]


def prefer_actions() -> list[str]:
    rec = build_recommendation()
    return rec["recommended_actions"]


def influence_task_priority(action_ids: list[str]) -> list[dict]:
    """Rank candidate actions — higher score = run first."""
    rec = build_recommendation(candidate_actions=action_ids)
    ranked = []
    for row in rec["ranked_actions"]:
        if row["action_id"] not in action_ids:
            continue
        ranked.append(
            {
                "action_id": row["action_id"],
                "score": row["score"],
                "avoid": row.get("avoid", False),
                "prefer": row.get("prefer", False) or row.get("recommended", False),
                "historical_score": row.get("historical_score", 0),
                "risk_score": row.get("risk_score", 0),
                "confidence": row.get("confidence", 0),
            }
        )
    seen = {r["action_id"] for r in ranked}
    for aid in action_ids:
        if aid not in seen:
            ranked.append({"action_id": aid, "score": 50.0, "avoid": False, "prefer": False})
    ranked.sort(key=lambda x: -x["score"])
    return ranked


def planner_context_block() -> dict:
    """Inject into agent_loop / prompt_direction planners."""
    upgrade = run_planner_upgrade()
    rec = upgrade.get("recommendation") or {}
    contexts = upgrade.get("action_contexts") or []
    patterns_top = []
    for ctx in contexts:
        patterns_top.extend(ctx.get("patterns") or [])
    patterns_top = patterns_top[:12]

    block = {
        "execution_intelligence": {
            "planner_upgrade_v1": {
                "recommended_actions": rec.get("recommended_actions") or [],
                "avoid_actions": rec.get("avoid_actions") or [],
                "ranked_actions": rec.get("ranked_actions") or [],
                "outcome_evaluations": upgrade.get("outcome_evaluations") or [],
                "planner_context_summary": upgrade.get("planner_context_summary") or {},
            },
            "patterns_top": patterns_top,
            "avoid_actions": rec.get("avoid_actions") or [],
            "prefer_actions": rec.get("recommended_actions") or [],
            "recent_decisions": _recent_decisions_from_contexts(contexts),
            "planner_rules": [
                "Deprioritize actions in avoid_actions until failure signatures are resolved.",
                "Prefer recommended_actions backed by historical success and reinforce signals.",
                "Use ranked_actions scores — not task text alone — when choosing next dispatch.",
                "Reference outcome_evaluations for historical_score, risk_score, and confidence.",
            ],
        }
    }
    try:
        from execution_intelligence_v2.strategy_optimizer import planner_v2_signals  # noqa: WPS433

        v2 = planner_v2_signals()
        ei2 = v2.get("execution_intelligence_v2") or {}
        block["execution_intelligence"]["predictions"] = ei2.get("predictions", [])[:6]
        block["execution_intelligence"]["risk_scores"] = ei2.get("risk_scores", [])[:6]
        block["execution_intelligence_v2"] = ei2
    except Exception as exc:  # noqa: BLE001
        block["execution_intelligence_v2"] = {"ok": False, "error": str(exc)}
    return block


def _recent_decisions_from_contexts(contexts: list[dict]) -> list[dict]:
    decisions: list[dict] = []
    for ctx in contexts:
        decisions.extend(ctx.get("decisions") or [])
    return decisions[-8:]


def planner_context_text() -> str:
    import json

    return json.dumps(planner_context_block(), indent=2, ensure_ascii=False)[:8000]
