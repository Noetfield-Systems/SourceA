"""Rank signals by relevance to a task/action (synthesis only, no prediction)."""
from __future__ import annotations

from execution_intelligence.pattern_engine.helpers import action_from_pattern, pattern_matches_action


def _action_from_task(task_id: str, action_id: str | None) -> str:
    if action_id:
        return action_id
    if task_id.startswith("predict:"):
        return task_id.replace("predict:", "", 1)
    if task_id.startswith("risk:"):
        return task_id.replace("risk:", "", 1)
    if ":" in task_id:
        return task_id.split(":", 1)[-1]
    return ""


def score_execution(record: dict, *, action_key: str, task_id: str) -> float:
    score = 0.0
    if task_id and record.get("task_id") == task_id:
        score += 100
    rec_action = record.get("action_id") or ""
    if action_key and rec_action == action_key:
        score += 50
    if record.get("status") == "failure":
        score += 15
    ms = record.get("execution_time_ms") or 0
    if ms:
        score += min(5, ms / 1000)
    return score


def score_pattern(pattern: dict, *, action_key: str) -> float:
    score = 0.0
    freq = pattern.get("frequency") or 0
    score += min(40, freq * 8)
    if pattern_matches_action(pattern, action_key):
        score += 35
    if pattern.get("type") == "failure":
        score += 20
    if pattern.get("type") == "fix":
        score += 25
    if pattern.get("type") == "success":
        score += 10
    score += (pattern.get("confidence") or 0) * 15
    return score


def score_decision(decision: dict, *, action_key: str, task_id: str) -> float:
    score = 0.0
    if task_id and decision.get("task_id") == task_id:
        score += 80
    if action_key and decision.get("action_id") == action_key:
        score += 40
    if decision.get("outcome") in ("failed", "failure") or decision.get("cause_type", "").endswith("_cause") and "failure" in decision.get("cause_type", ""):
        score += 15
    return score


def rank_items(items: list[dict], *, key_fn) -> list[dict]:
    scored = []
    for item in items:
        s = key_fn(item)
        scored.append({**item, "_relevance_score": round(s, 2)})
    scored.sort(key=lambda x: -x["_relevance_score"])
    return scored


def resolve_action_key(task_id: str = "", action_id: str | None = None) -> str:
    return _action_from_task(task_id or "", action_id)
