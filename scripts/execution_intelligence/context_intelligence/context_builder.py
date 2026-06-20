"""Merge operational, repo, behavior, and planner state into unified context."""
from __future__ import annotations

from datetime import datetime, timezone

from execution_intelligence.context_intelligence.behavior_analyzer import analyze_behavior
from execution_intelligence.context_intelligence.context_store import load_planner_context_readonly
from execution_intelligence.context_intelligence.repo_analyzer import analyze_repo_state
from execution_intelligence.context_intelligence.state_analyzer import analyze_operational_state
from execution_intelligence.context_intelligence.relevance_ranker import (
    rank_items,
    resolve_action_key,
    score_decision,
    score_execution,
    score_pattern,
)
from execution_intelligence.decision_memory.api import read_decisions
from execution_intelligence.feedback_loop.loop_engine import load_patterns_readonly
from execution_intelligence.planner_upgrade.planner_context import load_signals_readonly
from execution_intelligence.reader import read_execution_memory


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _build_summary(
    system_state: dict,
    repo_state: dict,
    behavior_state: dict,
    planner_state: dict,
) -> str:
    parts: list[str] = []
    if system_state.get("last_action_id"):
        parts.append(f"Last run: {system_state['last_action_id']} ({system_state.get('last_status')})")
    prog = repo_state.get("progress_summary") or {}
    if prog.get("p0_id"):
        parts.append(f"P0={prog['p0_id']} ({prog.get('p0_progress_pct')}%)")
    if behavior_state.get("dominant_patterns"):
        top = behavior_state["dominant_patterns"][0]
        parts.append(f"Top pattern: {top.get('type')} {top.get('signature', '')[:40]}")
    if behavior_state.get("decision_trends"):
        top_cause = max(behavior_state["decision_trends"].items(), key=lambda x: x[1])[0]
        parts.append(f"Dominant decision trend: {top_cause}")
    rec = (planner_state.get("recommendation") or {}).get("recommended_actions") or []
    if rec:
        parts.append(f"Planner recommends: {', '.join(rec[:3])}")
    parts.append(f"Health={system_state.get('system_health', 0):.2f}")
    return " · ".join(parts)


def build_unified_context() -> dict:
    memory = read_execution_memory()
    patterns = load_patterns_readonly()
    decisions = read_decisions(limit=200)
    signals = load_signals_readonly()
    planner_raw = load_planner_context_readonly()

    system_state = analyze_operational_state(records=memory)
    repo_state = analyze_repo_state()
    behavior_state = analyze_behavior(
        patterns=patterns,
        decisions=decisions,
        signals=signals,
        memory=memory,
    )
    planner_state = {
        "planner_context_summary": planner_raw.get("planner_context_summary") or {},
        "recommendation": planner_raw.get("recommendation") or {},
        "outcome_evaluations": planner_raw.get("outcome_evaluations") or [],
        "updated_at": planner_raw.get("updated_at"),
    }

    summary = _build_summary(system_state, repo_state, behavior_state, planner_state)

    return {
        "schema": "context-intelligence-v1",
        "system_state": system_state,
        "repo_state": repo_state,
        "behavior_state": behavior_state,
        "planner_state": planner_state,
        "context_summary": summary,
        "generated_at": _now(),
    }


def build_task_context(*, task_id: str = "", action_id: str | None = None) -> dict:
    """Task-scoped view for legacy /api/execution-context consumers."""
    unified = build_unified_context()
    action_key = resolve_action_key(task_id, action_id)
    memory = read_execution_memory()
    patterns = load_patterns_readonly()
    decisions = read_decisions(limit=100)

    ranked_exec = rank_items(
        memory[-50:],
        key_fn=lambda r: score_execution(r, action_key=action_key, task_id=task_id),
    )
    ranked_patterns = rank_items(
        patterns,
        key_fn=lambda p: score_pattern(p, action_key=action_key),
    )
    ranked_decisions = rank_items(
        decisions,
        key_fn=lambda d: score_decision(d, action_key=action_key, task_id=task_id),
    )

    repo = unified.get("repo_state") or {}
    focus_areas = list((repo.get("progress_summary") or {}).get("must_do_today") or [])
    prog = repo.get("progress_summary") or {}
    if prog.get("p0_id") and repo.get("critical_paths"):
        focus_areas.insert(0, repo["critical_paths"][0])

    return {
        "task_id": task_id or (f"action:{action_key}" if action_key else "system"),
        "system_state_summary": unified.get("context_summary", ""),
        "recent_executions": [
            {
                "task_id": r.get("task_id"),
                "action_id": r.get("action_id"),
                "status": r.get("status"),
                "timestamp": r.get("timestamp"),
                "execution_time_ms": r.get("execution_time_ms"),
                "relevance_score": r.get("_relevance_score"),
            }
            for r in ranked_exec[:12]
        ],
        "relevant_patterns": [
            {k: v for k, v in p.items() if k != "_relevance_score"} for p in ranked_patterns[:10]
        ],
        "decision_context": [
            {
                **{k: v for k, v in d.items() if k != "_relevance_score"},
                "why": d.get("why_summary") or d.get("why"),
                "outcome": "success" if "success" in (d.get("cause_type") or "") else "failure",
            }
            for d in ranked_decisions[:8]
        ],
        "risk_context": (unified.get("behavior_state") or {}).get("behavioral_risks") or [],
        "recommended_focus_areas": focus_areas[:8],
        "active_constraints": [
            "Auto-paste into Cursor blocked by default (incident law)",
            "Execution spine SSOT: execution_memory.jsonl",
            *(
                [f"P0 thread locked: {prog['locks']['p0_thread']}"]
                if (prog.get("locks") or {}).get("p0_thread")
                else []
            ),
        ],
        "unified_context_ref": "context_intelligence_v1.json",
        "meta": {
            "action_key": action_key,
            "generated_at": unified.get("generated_at"),
        },
    }


# Backward-compatible alias
def build_context(*, task_id: str = "", action_id: str | None = None) -> dict:
    return build_task_context(task_id=task_id, action_id=action_id)
