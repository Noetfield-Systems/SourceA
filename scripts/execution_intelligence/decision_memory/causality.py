"""Cause → effect mapping from execution records + patterns (read-only)."""
from __future__ import annotations

from execution_intelligence.pattern_engine.helpers import pattern_matches_action


def cause_signal_from_record(record: dict) -> str:
    if record.get("status") == "success":
        ms = record.get("execution_time_ms") or 0
        return f"exit_0_in_{ms}ms"
    sig = (record.get("error_signature") or "").strip()
    if sig:
        return sig[:120]
    stderr = (record.get("stderr") or "").strip().splitlines()
    if stderr:
        return stderr[-1][:120]
    return f"exit_{record.get('exit_code', 1)}"


def effect_signal_from_record(record: dict) -> str:
    if record.get("status") == "success":
        return "outcome:success"
    return "outcome:failure"


def effect_signal_from_pattern(pattern: dict) -> str:
    ptype = pattern.get("type") or ""
    return f"pattern:{ptype}:{(pattern.get('signature') or '')[:60]}"


def classify_cause_type(
    record: dict,
    *,
    had_prior_failure: bool,
    is_retry_success: bool,
    pattern: dict | None,
) -> str:
    if record.get("status") == "success" and had_prior_failure:
        return "fix_cause"
    if is_retry_success:
        return "fix_cause"
    if record.get("status") == "success":
        return "success_cause"
    cause = cause_signal_from_record(record)
    if "timeout" in cause.lower() or "constraint" in (pattern or {}).get("type", ""):
        return "constraint"
    return "failure_cause"


def map_cause_effect(record: dict, pattern: dict | None) -> dict:
    action = record.get("action_id") or record.get("producer") or "unknown"
    cause = cause_signal_from_record(record)
    effect = effect_signal_from_record(record)
    if pattern:
        effect = f"{effect}|{effect_signal_from_pattern(pattern)}"
    return {
        "action_id": action,
        "task_id": record.get("task_id"),
        "cause_signal": cause,
        "effect_signal": effect,
        "pattern_id": (pattern or {}).get("pattern_id") or "",
    }


def match_pattern(patterns: list[dict], record: dict) -> dict | None:
    action = record.get("action_id") or ""
    want = "success" if record.get("status") == "success" else "failure"
    for p in patterns:
        if p.get("type") == "fix" and record.get("status") == "success":
            if pattern_matches_action(p, action):
                return p
        if p.get("type") == want and pattern_matches_action(p, action):
            return p
    return None


def build_cause_effect_mappings(decisions: list[dict]) -> list[dict]:
    out = []
    for d in decisions:
        out.append(
            {
                "cause": d.get("cause_signal"),
                "effect": d.get("effect_signal"),
                "pattern_id": d.get("pattern_id"),
                "cause_type": d.get("cause_type"),
                "why_summary": d.get("why_summary"),
                "confidence": d.get("confidence"),
            }
        )
    return out
