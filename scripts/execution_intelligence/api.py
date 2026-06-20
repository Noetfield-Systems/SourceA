"""Hub read-only payload for execution intelligence."""
from __future__ import annotations

from execution_intelligence.decision_memory import read_decisions
from execution_intelligence.feedback_loop import read_signals, run_feedback_loop
from execution_intelligence.planner_influence import avoid_actions, influence_task_priority, prefer_actions
from execution_intelligence.reader import MEMORY_PATH, read_execution_memory


def intelligence_payload() -> dict:
    loop = run_feedback_loop()
    records = read_execution_memory()
    patterns = loop.get("patterns") or []
    return {
        "ok": True,
        "source": str(MEMORY_PATH),
        "memory_total": len(records),
        "patterns_count": len(patterns),
        "patterns": patterns[:25],
        "repeated_errors": loop.get("repeated_errors") or [],
        "avoid_actions": avoid_actions(),
        "prefer_actions": prefer_actions(),
        "recent_decisions": read_decisions(limit=15),
        "feedback": {
            "updated_at": loop.get("updated_at"),
            "skipped": loop.get("skipped", False),
            "decisions_total": loop.get("decisions_total", 0),
            "signals_count": loop.get("signals_count", 0),
            "active_signals": read_signals(limit=25),
            "weighted_ranking_summary": loop.get("ranking") or [],
        },
    }


def rank_actions(action_ids: list[str]) -> dict:
    return {"ok": True, "ranked": influence_task_priority(action_ids)}
