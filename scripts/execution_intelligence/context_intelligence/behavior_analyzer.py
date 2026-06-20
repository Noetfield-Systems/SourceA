"""Behavioral understanding from patterns, decisions, signals, memory (read-only)."""
from __future__ import annotations

from collections import Counter

from execution_intelligence.pattern_engine.helpers import action_from_pattern
from execution_intelligence.planner_upgrade.planner_context import (
    load_decisions_readonly,
    load_patterns_readonly,
    load_signals_readonly,
)
from execution_intelligence.reader import read_execution_memory


def _action_from_decision(decision: dict) -> str:
    if decision.get("action_id"):
        return str(decision["action_id"])
    why = decision.get("why_summary") or ""
    if why.startswith("'") and "'" in why[1:]:
        return why[1 : why.index("'", 1)]
    return ""


def analyze_behavior(
    *,
    patterns: list[dict] | None = None,
    decisions: list[dict] | None = None,
    signals: list[dict] | None = None,
    memory: list[dict] | None = None,
) -> dict:
    patterns = patterns if patterns is not None else load_patterns_readonly()
    decisions = decisions if decisions is not None else load_decisions_readonly()
    signals = signals if signals is not None else load_signals_readonly()
    memory = memory if memory is not None else read_execution_memory()

    dominant_patterns = sorted(
        patterns,
        key=lambda p: (-int(p.get("frequency") or 0), -float(p.get("confidence") or 0)),
    )[:8]
    dominant_patterns_out = [
        {
            "pattern_id": p.get("pattern_id"),
            "type": p.get("type"),
            "signature": p.get("signature"),
            "frequency": p.get("frequency"),
            "confidence": p.get("confidence"),
            "action_id": action_from_pattern(p),
        }
        for p in dominant_patterns
    ]

    cause_counts = Counter(d.get("cause_type") or "unknown" for d in decisions)
    dominant_decisions = sorted(
        decisions,
        key=lambda d: -float(d.get("confidence") or 0),
    )[:8]
    dominant_decisions_out = [
        {
            "decision_id": d.get("decision_id"),
            "cause_type": d.get("cause_type"),
            "action_id": _action_from_decision(d),
            "why_summary": (d.get("why_summary") or "")[:120],
            "confidence": d.get("confidence"),
        }
        for d in dominant_decisions
    ]

    behavioral_risks: list[dict] = []
    for p in patterns:
        if p.get("type") in ("failure", "repetition"):
            behavioral_risks.append(
                {
                    "kind": "pattern",
                    "pattern_id": p.get("pattern_id"),
                    "type": p.get("type"),
                    "signature": p.get("signature"),
                    "frequency": p.get("frequency"),
                    "action_id": action_from_pattern(p),
                }
            )
    for sig in signals:
        if sig.get("signal_type") in ("avoid", "deprioritize"):
            behavioral_risks.append(
                {
                    "kind": "signal",
                    "signal_id": sig.get("signal_id"),
                    "signal_type": sig.get("signal_type"),
                    "action_id": sig.get("action_id"),
                    "weight": sig.get("weight"),
                    "reason": (sig.get("reason") or "")[:100],
                }
            )

    action_hits = Counter(r.get("action_id") or "unknown" for r in memory)
    execution_habits = [
        {"action_id": act, "runs": count}
        for act, count in action_hits.most_common(8)
    ]

    return {
        "dominant_patterns": dominant_patterns_out,
        "dominant_decisions": dominant_decisions_out,
        "behavioral_risks": behavioral_risks[:12],
        "repeated_actions": [p for p in dominant_patterns_out if p.get("type") == "repetition"],
        "common_failures": [p for p in dominant_patterns_out if p.get("type") == "failure"],
        "common_successes": [p for p in dominant_patterns_out if p.get("type") == "success"],
        "execution_habits": execution_habits,
        "decision_trends": dict(cause_counts),
        "signal_summary": {
            st: len([s for s in signals if s.get("signal_type") == st])
            for st in ("prefer", "avoid", "reinforce", "deprioritize")
        },
    }
