"""Build per-action planner context from read-only SSOT inputs."""
from __future__ import annotations

import json
from pathlib import Path

from execution_intelligence.pattern_engine.helpers import action_from_pattern, pattern_matches_action

STATE_DIR = Path.home() / ".sina"
PATTERNS_V1_PATH = STATE_DIR / "execution_patterns_v1.json"
DECISIONS_V1_PATH = STATE_DIR / "execution_decisions_v1.jsonl"
SIGNALS_V1_PATH = STATE_DIR / "execution_feedback_signals.jsonl"


def load_patterns_readonly() -> list[dict]:
    if not PATTERNS_V1_PATH.is_file():
        return []
    try:
        data = json.loads(PATTERNS_V1_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data.get("patterns") or []


def load_decisions_readonly(*, limit: int = 500) -> list[dict]:
    if not DECISIONS_V1_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in DECISIONS_V1_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def load_signals_readonly(*, limit: int = 500) -> list[dict]:
    if not SIGNALS_V1_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in SIGNALS_V1_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def _action_from_decision(decision: dict) -> str:
    if decision.get("action_id"):
        return str(decision["action_id"])
    why = decision.get("why_summary") or ""
    if why.startswith("'") and "'" in why[1:]:
        return why[1 : why.index("'", 1)]
    return ""


def discover_actions(
    patterns: list[dict],
    decisions: list[dict],
    signals: list[dict],
    *,
    candidates: list[str] | None = None,
) -> list[str]:
    actions: set[str] = set(candidates or [])
    for pattern in patterns:
        act = action_from_pattern(pattern)
        if act:
            actions.add(act)
    for decision in decisions:
        act = _action_from_decision(decision)
        if act:
            actions.add(act)
    for signal in signals:
        act = signal.get("action_id") or ""
        if act:
            actions.add(act)
    return sorted(actions)


def build_action_context(
    action_id: str,
    *,
    patterns: list[dict] | None = None,
    decisions: list[dict] | None = None,
    signals: list[dict] | None = None,
) -> dict:
    patterns = patterns if patterns is not None else load_patterns_readonly()
    decisions = decisions if decisions is not None else load_decisions_readonly()
    signals = signals if signals is not None else load_signals_readonly()

    relevant_patterns = [p for p in patterns if pattern_matches_action(p, action_id)]
    relevant_decisions = [d for d in decisions if _action_from_decision(d) == action_id]
    relevant_signals = [s for s in signals if s.get("action_id") == action_id]

    return {
        "action_id": action_id,
        "patterns": relevant_patterns,
        "decisions": relevant_decisions,
        "signals": relevant_signals,
        "pattern_count": len(relevant_patterns),
        "decision_count": len(relevant_decisions),
        "signal_count": len(relevant_signals),
    }


def build_planner_context_package(
    *,
    candidate_actions: list[str] | None = None,
) -> dict:
    patterns = load_patterns_readonly()
    decisions = load_decisions_readonly()
    signals = load_signals_readonly()
    actions = discover_actions(patterns, decisions, signals, candidates=candidate_actions)

    return {
        "patterns_total": len(patterns),
        "decisions_total": len(decisions),
        "signals_total": len(signals),
        "candidate_actions": actions,
        "action_contexts": [build_action_context(a, patterns=patterns, decisions=decisions, signals=signals) for a in actions],
    }
