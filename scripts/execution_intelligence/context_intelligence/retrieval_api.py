"""Unified context retrieval — what matters now for a task."""
from __future__ import annotations

from execution_intelligence.context_intelligence.context_builder import build_context


def retrieve_context(*, task_id: str = "", action_id: str | None = None) -> dict:
    ctx = build_context(task_id=task_id, action_id=action_id)
    ranked = []
    for ex in ctx.get("recent_executions") or []:
        ranked.append({"kind": "execution", "id": ex.get("task_id"), "score": ex.get("relevance_score"), "label": ex.get("action_id")})
    for p in ctx.get("relevant_patterns") or []:
        ranked.append({"kind": "pattern", "id": p.get("pattern_id"), "score": p.get("confidence"), "label": p.get("type")})
    for d in ctx.get("decision_context") or []:
        ranked.append({"kind": "decision", "id": d.get("decision_id"), "score": None, "label": d.get("outcome")})
    ranked.sort(key=lambda x: -(x.get("score") or 0))

    matters_now = {
        "focus_areas": ctx.get("recommended_focus_areas") or [],
        "top_executions": (ctx.get("recent_executions") or [])[:3],
        "top_patterns": (ctx.get("relevant_patterns") or [])[:3],
        "top_decisions": (ctx.get("decision_context") or [])[:3],
        "risks": ctx.get("risk_context") or [],
    }

    return {
        "context": ctx,
        "ranked_relevance": ranked[:20],
        "matters_now": matters_now,
    }
