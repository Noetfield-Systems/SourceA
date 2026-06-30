"""Deterministic Brain Core v1 gate path."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Mapping

from scripts.brain_core_v1.decision_core import decide, load_locked_definitions
from scripts.brain_core_v1.d4_enforcement import enforce_d4
from scripts.brain_core_v1.locked_definitions import (
    CANONICAL_LOCKED_DEFINITIONS_PATH,
    EXPECTED_LOCKED_DEFINITIONS_SHA256,
    validate_locked_definitions_checksum,
)
from scripts.brain_core_v1.live_status_probe import decision_status_map
from scripts.brain_core_v1.sanitizer import sanitize_model_output

PASS_RE = re.compile(r"\bPASS\b", re.I)
DEFAULT_CREATED_AT = "1970-01-01T00:00:00Z"


def _default_model_output(decision: Mapping[str, Any]) -> str:
    return str(decision.get("fallback_text") or decision.get("approved_claim") or "")


def _input_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def run_gate(
    user_message: str,
    model_output: str = "",
    *,
    live_status: Mapping[str, Any] | None = None,
    definitions: Mapping[str, Any] | None = None,
    definitions_path: str | Path | None = CANONICAL_LOCKED_DEFINITIONS_PATH,
    expected_definitions_sha256: str | None = EXPECTED_LOCKED_DEFINITIONS_SHA256,
    created_at: str = DEFAULT_CREATED_AT,
) -> dict[str, Any]:
    """Run probe-result -> mapped-status -> decision -> sanitizer -> gate result.

    This function is deterministic and performs no network calls. Callers may pass a
    real probe result from live_status_probe or a manual mocked status map.
    """
    live_status_map = dict(live_status or {})
    mapped_status = decision_status_map(live_status_map)
    definitions_validation = validate_locked_definitions_checksum(
        path=definitions_path,
        expected_sha256=expected_definitions_sha256,
    )
    if definitions_validation["validation_result"] == "BLOCK":
        reasons = ["locked_definitions_checksum_block", *definitions_validation["reasons"]]
        input_hash = _input_hash(
            {
                "user_message": user_message,
                "model_output": model_output,
                "live_status": live_status_map,
                "mapped_status": mapped_status,
                "locked_definitions_validation": definitions_validation,
            }
        )
        receipt = {
            "schema": "brain-core-gate-v1",
            "schema_version": "1.0.0",
            "receipt_type": "BRAIN_CORE_GATE_RESULT",
            "status": "BLOCKED",
            "lifecycle": "BLOCKED",
            "created_at": created_at,
            "author_runtime": "brain_core_v1",
            "subject_runtime": "public_brain_reply",
            "verifier_runtime": "test_suite",
            "live_status": live_status_map,
            "mapped_status": mapped_status,
            "decision": {},
            "sanitized_output": {
                "ok": False,
                "reason": "locked_definitions_checksum_block",
                "safe_public_language": "",
                "forbidden_public_language_removed": [],
            },
            "pass_claimed": bool(PASS_RE.search(model_output or "")),
            "gate_result": "BLOCK",
            "reasons": reasons,
            "evidence": {
                "decision": {},
                "sanitized_output": {
                    "ok": False,
                    "reason": "locked_definitions_checksum_block",
                    "safe_public_language": "",
                    "forbidden_public_language_removed": [],
                },
                "live_status": live_status_map,
                "mapped_status": mapped_status,
                "locked_definitions_validation": definitions_validation,
            },
            "locked_definitions_validation": definitions_validation,
            "input_hash": input_hash,
        }
        receipt["d4_enforcement"] = enforce_d4(receipt)
        return receipt

    locked_definitions = definitions or load_locked_definitions(definitions_path)
    decision = decide(user_message, mapped_status, definitions=locked_definitions)
    draft = model_output or _default_model_output(decision)
    sanitized_output = sanitize_model_output(decision, draft)
    pass_claimed = bool(PASS_RE.search(model_output or ""))
    input_hash = _input_hash(
        {
            "user_message": user_message,
            "model_output": model_output,
            "live_status": live_status_map,
            "mapped_status": mapped_status,
            "definitions_status": locked_definitions.get("status"),
            "founder_decisions_resolved": locked_definitions.get("founder_decisions_resolved"),
        }
    )

    reasons: list[str] = []
    if decision.get("ladder_gear") != "confident":
        reasons.append(f"status_not_confident:{decision.get('ladder_gear')}")
    if pass_claimed and decision.get("ladder_gear") != "confident":
        reasons.append("pass_claimed_without_confident_status")
    if not sanitized_output.get("ok"):
        reasons.append(f"sanitizer_block:{sanitized_output.get('reason', 'unknown')}")

    receipt = {
        "schema": "brain-core-gate-v1",
        "schema_version": "1.0.0",
        "receipt_type": "BRAIN_CORE_GATE_RESULT",
        "status": "PASS" if not reasons else "BLOCKED",
        "lifecycle": "PASS" if not reasons else "BLOCKED",
        "created_at": created_at,
        "author_runtime": "brain_core_v1",
        "subject_runtime": "public_brain_reply",
        "verifier_runtime": "test_suite",
        "live_status": live_status_map,
        "mapped_status": mapped_status,
        "decision": decision,
        "sanitized_output": sanitized_output,
        "pass_claimed": pass_claimed,
        "gate_result": "PASS" if not reasons else "BLOCK",
        "reasons": reasons,
        "evidence": {
            "decision": decision,
            "sanitized_output": sanitized_output,
            "live_status": live_status_map,
            "mapped_status": mapped_status,
            "locked_definitions_validation": definitions_validation,
        },
        "locked_definitions_validation": definitions_validation,
        "input_hash": input_hash,
    }
    receipt["d4_enforcement"] = enforce_d4(receipt)
    if not receipt["d4_enforcement"]["ok"] and "d4_enforcement_blocked" not in receipt["reasons"]:
        receipt["reasons"].append("d4_enforcement_blocked")
        receipt["gate_result"] = "BLOCK"
        receipt["lifecycle"] = "BLOCKED"
        receipt["status"] = "BLOCKED"
    return receipt
