"""D4 receipt separation enforcement for Brain Core v1."""
from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

LIFECYCLES = {"SUBMITTED", "PASS", "FAIL", "BLOCKED"}
PROTECTED_RECEIPT_TYPES = {"BRAIN_CORE_GATE_RESULT"}
REQUIRED_PASS_EVIDENCE = ("input_hash", "sanitized_output")


def _stable_hash(payload: Mapping[str, Any]) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _lifecycle(receipt: Mapping[str, Any]) -> str:
    raw = receipt.get("lifecycle") or receipt.get("gate_result") or "SUBMITTED"
    value = str(raw).upper()
    return value if value in LIFECYCLES else "BLOCKED"


def _missing_evidence(receipt: Mapping[str, Any]) -> list[str]:
    return [field for field in REQUIRED_PASS_EVIDENCE if not receipt.get(field)]


def enforce_d4(receipt: Mapping[str, Any]) -> dict[str, Any]:
    """Return deterministic D4 enforcement result for a receipt."""
    receipt_type = str(receipt.get("receipt_type") or "")
    lifecycle = _lifecycle(receipt)
    author_runtime = str(receipt.get("author_runtime") or "")
    verifier_runtime = str(receipt.get("verifier_runtime") or "")
    protected = receipt_type in PROTECTED_RECEIPT_TYPES

    reasons: list[str] = []
    if lifecycle not in LIFECYCLES:
        reasons.append("invalid_lifecycle")
    if lifecycle == "PASS":
        if not verifier_runtime:
            reasons.append("missing_verifier_runtime")
        if author_runtime and verifier_runtime and author_runtime == verifier_runtime:
            reasons.append("author_verifier_not_independent")
        for field in _missing_evidence(receipt):
            reasons.append(f"missing_evidence:{field}")
    if protected and author_runtime and verifier_runtime and author_runtime == verifier_runtime:
        reasons.append("protected_receipt_self_verified")
    if lifecycle in {"FAIL", "BLOCKED"} and not receipt.get("reasons") and not receipt.get("reason"):
        reasons.append("missing_reason")

    enforced_lifecycle = "BLOCKED" if reasons else lifecycle
    return {
        "schema": "brain-core-d4-enforcement-v1",
        "ok": not reasons,
        "receipt_type": receipt_type,
        "input_lifecycle": lifecycle,
        "lifecycle": enforced_lifecycle,
        "author_runtime": author_runtime,
        "verifier_runtime": verifier_runtime,
        "author_subject_separated": author_runtime != str(receipt.get("subject_runtime") or author_runtime),
        "author_verifier_separated": bool(author_runtime and verifier_runtime and author_runtime != verifier_runtime),
        "protected_receipt": protected,
        "reasons": reasons,
        "enforcement_hash": _stable_hash(
            {
                "receipt_type": receipt_type,
                "lifecycle": lifecycle,
                "author_runtime": author_runtime,
                "verifier_runtime": verifier_runtime,
                "subject_runtime": receipt.get("subject_runtime"),
                "reasons": reasons,
                "input_hash": receipt.get("input_hash"),
            }
        ),
    }
