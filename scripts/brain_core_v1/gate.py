"""Deterministic Brain Core v1 gate path."""
from __future__ import annotations

import re
from typing import Any, Mapping

from scripts.brain_core_v1.decision_core import decide, load_locked_definitions
from scripts.brain_core_v1.live_status_probe import decision_status_map
from scripts.brain_core_v1.sanitizer import sanitize_model_output

PASS_RE = re.compile(r"\bPASS\b", re.I)


def _default_model_output(decision: Mapping[str, Any]) -> str:
    return str(decision.get("fallback_text") or decision.get("approved_claim") or "")


def run_gate(
    user_message: str,
    model_output: str = "",
    *,
    live_status: Mapping[str, Any] | None = None,
    definitions: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run probe-result -> mapped-status -> decision -> sanitizer -> gate result.

    This function is deterministic and performs no network calls. Callers may pass a
    real probe result from live_status_probe or a manual mocked status map.
    """
    locked_definitions = definitions or load_locked_definitions()
    live_status_map = dict(live_status or {})
    mapped_status = decision_status_map(live_status_map)
    decision = decide(user_message, mapped_status, definitions=locked_definitions)
    draft = model_output or _default_model_output(decision)
    sanitized_output = sanitize_model_output(decision, draft)
    pass_claimed = bool(PASS_RE.search(model_output or ""))

    reasons: list[str] = []
    if decision.get("ladder_gear") != "confident":
        reasons.append(f"status_not_confident:{decision.get('ladder_gear')}")
    if pass_claimed and decision.get("ladder_gear") != "confident":
        reasons.append("pass_claimed_without_confident_status")
    if not sanitized_output.get("ok"):
        reasons.append(f"sanitizer_block:{sanitized_output.get('reason', 'unknown')}")

    return {
        "schema": "brain-core-gate-v1",
        "live_status": live_status_map,
        "mapped_status": mapped_status,
        "decision": decision,
        "sanitized_output": sanitized_output,
        "pass_claimed": pass_claimed,
        "gate_result": "PASS" if not reasons else "BLOCK",
        "reasons": reasons,
    }
