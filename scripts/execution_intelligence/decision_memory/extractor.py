"""Derive v1 decisions from execution memory + patterns only."""
from __future__ import annotations

import uuid

from execution_intelligence.decision_memory.causality import (
    classify_cause_type,
    map_cause_effect,
    match_pattern,
)
from execution_intelligence.decision_memory.reasoning import build_why_summary, confidence_from_pattern


def extract_decisions_v1(records: list[dict], patterns: list[dict]) -> list[dict]:
    if not records:
        return []

    seen_fail: dict[str, bool] = {}
    run_counts: dict[str, int] = {}
    decisions: list[dict] = []

    for rec in sorted(records, key=lambda r: r.get("timestamp") or ""):
        tid = rec.get("task_id") or ""
        if not tid:
            continue
        action = rec.get("action_id") or rec.get("producer") or "unknown"
        run_counts[action] = run_counts.get(action, 0) + 1

        pattern = match_pattern(patterns, rec)
        had_fail = seen_fail.get(action, False)
        is_retry = rec.get("status") == "success" and run_counts[action] > 1

        mapped = map_cause_effect(rec, pattern)
        cause_type = classify_cause_type(
            rec, had_prior_failure=had_fail, is_retry_success=is_retry, pattern=pattern
        )
        why = build_why_summary(
            cause_type=cause_type,
            action_id=action,
            cause_signal=mapped["cause_signal"],
            effect_signal=mapped["effect_signal"],
        )
        conf = confidence_from_pattern(pattern)
        if cause_type == "fix_cause":
            conf = max(conf, 0.65)

        if rec.get("status") != "success":
            seen_fail[action] = True

        decisions.append(
            {
                "decision_id": str(uuid.uuid4()),
                "task_id": tid,
                "pattern_id": mapped.get("pattern_id") or "",
                "cause_type": cause_type,
                "why_summary": why,
                "cause_signal": mapped["cause_signal"],
                "effect_signal": mapped["effect_signal"],
                "confidence": conf,
                # integration helpers (not required by strict schema consumers)
                "action_id": action,
            }
        )

    return decisions
