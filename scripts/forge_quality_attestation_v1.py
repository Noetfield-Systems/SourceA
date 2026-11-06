#!/usr/bin/env python3
"""Verify independent Forge quality attestations against pinned Ed25519 keys.

Positive quality learning is disabled unless a verifier key is explicitly
registered in data/forge-verifier-trust-registry-v1.json. A self-reported
receipt_integrity field is never accepted as proof.
"""
from __future__ import annotations

import base64
import binascii
import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TRUST_REGISTRY_PATH = ROOT / "data" / "forge-verifier-trust-registry-v1.json"
ATTESTATION_SCHEMA = "sourcea-independent-verifier-attestation-v1"
TRUST_REGISTRY_SCHEMA = "sourcea-forge-verifier-trust-registry-v1"

REQUIRED_ATTESTATION_FIELDS = {
    "schema",
    "key_id",
    "algorithm",
    "run_id",
    "builder_identity",
    "repairer_identity",
    "verifier_identity",
    "verdict",
    "evidence",
    "receipt_id",
    "issued_at",
    "signature_b64",
}
SHA256_RE = re.compile(r"^[0-9a-fA-F]{64}$")


def _canonical_payload(attestation: dict[str, Any]) -> bytes:
    payload = {key: value for key, value in attestation.items() if key != "signature_b64"}
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")


def _load_trust_registry() -> dict[str, Any]:
    try:
        raw = TRUST_REGISTRY_PATH.read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return {}
    return value if isinstance(value, dict) else {}


def verify_quality_attestation(
    attestation: dict[str, Any] | None,
    *,
    expected_run_id: str,
    trust_registry: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a verified attestation only when its pinned Ed25519 key passes."""
    if not isinstance(attestation, dict):
        return {"ok": False, "reason": "quality_attestation_missing"}

    if set(attestation) != REQUIRED_ATTESTATION_FIELDS:
        return {"ok": False, "reason": "quality_attestation_schema_mismatch"}

    if attestation.get("schema") != ATTESTATION_SCHEMA:
        return {"ok": False, "reason": "quality_attestation_bad_schema"}

    if attestation.get("algorithm") != "Ed25519":
        return {"ok": False, "reason": "quality_attestation_algorithm_not_allowed"}

    if attestation.get("verdict") != "PASS":
        return {"ok": False, "reason": "independent_verdict_not_pass"}

    if not expected_run_id or attestation.get("run_id") != expected_run_id:
        return {"ok": False, "reason": "quality_attestation_run_binding_mismatch"}

    builder = attestation.get("builder_identity")
    verifier = attestation.get("verifier_identity")
    repairer = attestation.get("repairer_identity")
    if not isinstance(builder, str) or not builder.strip():
        return {"ok": False, "reason": "builder_identity_missing"}
    if not isinstance(verifier, str) or not verifier.strip():
        return {"ok": False, "reason": "verifier_identity_missing"}
    if builder == verifier or (repairer and repairer == verifier):
        return {"ok": False, "reason": "verifier_not_independent_of_builder_or_repairer"}

    receipt_id = attestation.get("receipt_id")
    issued_at = attestation.get("issued_at")
    if not isinstance(receipt_id, str) or not receipt_id.strip():
        return {"ok": False, "reason": "quality_receipt_id_missing"}
    if not isinstance(issued_at, str) or not issued_at.strip():
        return {"ok": False, "reason": "quality_attestation_timestamp_missing"}
    try:
        parsed_time = datetime.fromisoformat(issued_at.replace("Z", "+00:00"))
        if parsed_time.tzinfo is None:
            return {"ok": False, "reason": "quality_attestation_timestamp_not_timezone_aware"}
    except ValueError:
        return {"ok": False, "reason": "quality_attestation_timestamp_invalid"}

    evidence = attestation.get("evidence")
    if not isinstance(evidence, list) or not evidence:
        return {"ok": False, "reason": "quality_evidence_missing"}
    for item in evidence:
        if not isinstance(item, dict) or set(item) != {"ref", "sha256"}:
            return {"ok": False, "reason": "quality_evidence_schema_invalid"}
        if not isinstance(item.get("ref"), str) or not item["ref"].strip():
            return {"ok": False, "reason": "quality_evidence_ref_missing"}
        if not isinstance(item.get("sha256"), str) or not SHA256_RE.fullmatch(item["sha256"]):
            return {"ok": False, "reason": "quality_evidence_sha256_invalid"}

    registry = trust_registry if trust_registry is not None else _load_trust_registry()
    if not isinstance(registry, dict) or registry.get("schema") != TRUST_REGISTRY_SCHEMA:
        return {"ok": False, "reason": "verifier_trust_registry_missing_or_invalid"}
    keys = registry.get("keys")
    if not isinstance(keys, list) or not keys:
        return {"ok": False, "reason": "no_trusted_verifier_keys_registered"}

    key_id = attestation.get("key_id")
    matches = [key for key in keys if isinstance(key, dict) and key.get("key_id") == key_id]
    if len(matches) != 1:
        return {"ok": False, "reason": "verifier_key_not_uniquely_registered"}
    key = matches[0]
    if key.get("status") != "ACTIVE":
        return {"ok": False, "reason": "verifier_key_not_active"}
    if key.get("agent_id") != verifier:
        return {"ok": False, "reason": "verifier_key_identity_mismatch"}
    purposes = key.get("purposes")
    if not isinstance(purposes, list) or "quality_verification" not in purposes:
        return {"ok": False, "reason": "verifier_key_purpose_not_allowed"}

    try:
        public_key = base64.b64decode(key.get("public_key_b64", ""), validate=True)
        signature = base64.b64decode(attestation.get("signature_b64", ""), validate=True)
    except (binascii.Error, ValueError, TypeError):
        return {"ok": False, "reason": "verifier_key_or_signature_encoding_invalid"}

    if len(public_key) != 32 or len(signature) != 64:
        return {"ok": False, "reason": "verifier_key_or_signature_length_invalid"}

    try:
        from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PublicKey
    except ImportError:
        return {"ok": False, "reason": "ed25519_verifier_dependency_unavailable"}

    try:
        Ed25519PublicKey.from_public_bytes(public_key).verify(
            signature,
            _canonical_payload(attestation),
        )
    except Exception:
        return {"ok": False, "reason": "verifier_attestation_signature_invalid"}

    return {
        "ok": True,
        "reason": None,
        "run_id": expected_run_id,
        "receipt_id": receipt_id,
        "builder_identity": builder,
        "repairer_identity": repairer,
        "verifier_identity": verifier,
        "evidence": evidence,
        "key_id": key_id,
    }
