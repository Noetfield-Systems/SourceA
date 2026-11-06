#!/usr/bin/env python3
"""Focused fail-closed regression checks for Founder Command integration."""
from __future__ import annotations

import base64
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from forge_swarm_blackboard_v1 import aggregate_critic_verdicts
from forge_agent_kernel_v1 import normalize_verifier_response
from forge_agent_kernel_v3_swarm import (
    ForgeState,
    critics_reputation_eligible,
    swarm_quality_success,
)
from forge_prompt_os_compiler_v3 import (
    quality_verification_gate,
    decide_learning_update,
)
from forge_quality_attestation_v1 import verify_quality_attestation


def _canonical_payload(attestation: dict) -> bytes:
    payload = {key: value for key, value in attestation.items() if key != "signature_b64"}
    return json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False
    ).encode("utf-8")


def signed_attestation(
    *,
    builder_identity: str = "builder-001",
    repairer_identity: str | None = None,
    verifier_identity: str = "critic-003",
    run_id: str = "run-fixture-001",
    verdict: str = "PASS",
) -> tuple[dict, dict]:
    """Create a deterministic test-only Ed25519 signer and injected trust registry."""
    private_key = Ed25519PrivateKey.from_private_bytes(bytes(range(32)))
    public_key = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    attestation = {
        "schema": "sourcea-independent-verifier-attestation-v1",
        "key_id": "test-key-critic-003",
        "algorithm": "Ed25519",
        "run_id": run_id,
        "builder_identity": builder_identity,
        "repairer_identity": repairer_identity,
        "verifier_identity": verifier_identity,
        "verdict": verdict,
        "evidence": [
            {
                "ref": "artifacts/tests/unit-test-results.json",
                "sha256": "a" * 64,
            },
            {
                "ref": "artifacts/diff/patch.diff",
                "sha256": "b" * 64,
            },
        ],
        "receipt_id": "REC-QUALITY-0001",
        "issued_at": "2026-11-06T08:00:00Z",
        "signature_b64": "",
    }
    attestation["signature_b64"] = base64.b64encode(
        private_key.sign(_canonical_payload(attestation))
    ).decode("ascii")
    registry = {
        "schema": "sourcea-forge-verifier-trust-registry-v1",
        "version": "1.0.0",
        "status": "TEST_FIXTURE_ONLY",
        "keys": [
            {
                "key_id": "test-key-critic-003",
                "agent_id": "critic-003",
                "status": "ACTIVE",
                "purposes": ["quality_verification"],
                "public_key_b64": base64.b64encode(public_key).decode("ascii"),
            }
        ],
    }
    return attestation, registry


class FailClosedRegressionTests(unittest.TestCase):
    def test_empty_critic_set_is_not_approval(self):
        result = aggregate_critic_verdicts([])
        self.assertIs(result["approved"], False)
        self.assertEqual(result["blocked_reason"], "NO_CRITIC_VERDICTS")

    def test_critic_provider_failure_is_not_approval(self):
        result = aggregate_critic_verdicts([
            {"ok": False, "approved": False, "score": 0.0, "provider_error": True}
        ])
        self.assertIs(result["approved"], False)
        self.assertEqual(result["blocked_reason"], "CRITIC_PROVIDER_OR_RESPONSE_FAILURE")

    def test_critic_malformed_response_is_not_approval(self):
        result = aggregate_critic_verdicts([
            {"ok": True, "score": 0.9, "issues": []}
        ])
        self.assertIs(result["approved"], False)
        self.assertEqual(result["blocked_reason"], "CRITIC_PROVIDER_OR_RESPONSE_FAILURE")

    def test_valid_critic_majority_can_approve(self):
        result = aggregate_critic_verdicts([
            {"ok": True, "approved": True, "score": 0.9, "issues": []},
            {"ok": True, "approved": True, "score": 0.8, "issues": []},
            {"ok": True, "approved": False, "score": 0.2, "issues": ["minor issue"]},
        ])
        self.assertIs(result["approved"], True)
        self.assertEqual(result["approved_votes"], 2)

    def test_verifier_provider_failure_is_unverified(self):
        result = normalize_verifier_response({"ok": False, "error": "provider unavailable"})
        self.assertIs(result["pass"], False)
        self.assertEqual(result["status"], "UNVERIFIED")

    def test_verifier_malformed_payload_is_unverified(self):
        result = normalize_verifier_response({"ok": True, "parsed": {"pass": "true"}})
        self.assertIs(result["pass"], False)
        self.assertEqual(result["status"], "UNVERIFIED")

    def test_verifier_explicit_pass_is_accepted(self):
        result = normalize_verifier_response({
            "ok": True, "parsed": {"pass": True, "note": "checks passed"}
        })
        self.assertIs(result["pass"], True)
        self.assertEqual(result["status"], "PASS")

    def test_swarm_success_requires_all_three_gates(self):
        good = [
            {"ok": True, "approved": True, "provider_error": False}
            for _ in range(3)
        ]
        self.assertTrue(swarm_quality_success(
            state=ForgeState.DONE,
            harness={"ok": True},
            critic_aggregate={"approved": True},
            critic_verdicts=good,
        ))
        self.assertFalse(swarm_quality_success(
            state=ForgeState.FAILED,
            harness={"ok": True},
            critic_aggregate={"approved": True},
            critic_verdicts=good,
        ))
        self.assertFalse(swarm_quality_success(
            state=ForgeState.DONE,
            harness={"ok": False},
            critic_aggregate={"approved": True},
            critic_verdicts=good,
        ))
        self.assertFalse(swarm_quality_success(
            state=ForgeState.DONE,
            harness={"ok": True},
            critic_aggregate={"approved": True},
            critic_verdicts=[],
        ))

    def test_swarm_provider_failure_cannot_earn_success(self):
        verdicts = [
            {"ok": True, "approved": True, "provider_error": False},
            {"ok": False, "approved": False, "provider_error": True},
            {"ok": True, "approved": True, "provider_error": False},
        ]
        self.assertFalse(swarm_quality_success(
            state=ForgeState.DONE,
            harness={"ok": True},
            critic_aggregate={"approved": False},
            critic_verdicts=verdicts,
        ))

    def test_single_critic_verdict_is_reputation_eligible(self):
        good = [{"ok": True, "approved": True, "provider_error": False}]
        self.assertTrue(critics_reputation_eligible(good))
        self.assertTrue(swarm_quality_success(
            state=ForgeState.DONE,
            harness={"ok": True},
            critic_aggregate={"approved": True},
            critic_verdicts=good,
        ))

    def test_provider_failure_does_not_change_reputation(self):
        failed = [{"ok": False, "approved": False, "provider_error": True}]
        self.assertFalse(critics_reputation_eligible(failed))
        self.assertFalse(critics_reputation_eligible([]))

    def test_valid_rejection_is_complete_evidence_for_negative_reputation(self):
        rejected = [{"ok": True, "approved": False, "provider_error": False}]
        self.assertTrue(critics_reputation_eligible(rejected))

    def test_done_without_trusted_attestation_is_ineligible(self):
        gate = quality_verification_gate(
            {"state": "DONE", "ok": True},
            expected_run_id="run-fixture-001",
        )
        self.assertFalse(gate["eligible"])
        self.assertEqual(gate["reason"], "quality_attestation_missing")
        self.assertEqual(
            decide_learning_update(
                execution_ok=True, execution_state="DONE", quality_gate=gate
            ),
            "SKIP_UNVERIFIED",
        )

    def test_empty_production_trust_registry_blocks_positive_learning(self):
        attestation, _ = signed_attestation()
        gate = quality_verification_gate(
            {"quality_verification_attestation": attestation},
            expected_run_id="run-fixture-001",
        )
        self.assertFalse(gate["eligible"])
        self.assertEqual(gate["reason"], "no_trusted_verifier_keys_registered")

    def test_valid_ed25519_attestation_passes_injected_test_registry(self):
        attestation, registry = signed_attestation()
        result = verify_quality_attestation(
            attestation,
            expected_run_id="run-fixture-001",
            trust_registry=registry,
        )
        self.assertTrue(result["ok"])
        self.assertEqual(result["verifier_identity"], "critic-003")
        self.assertEqual(result["receipt_id"], "REC-QUALITY-0001")

    def test_valid_attestation_allows_positive_learning_when_key_is_pinned(self):
        attestation, registry = signed_attestation()
        gate = quality_verification_gate(
            {"quality_verification_attestation": attestation},
            expected_run_id="run-fixture-001",
            trust_registry=registry,
        )
        self.assertTrue(gate["eligible"])
        self.assertEqual(gate["status"], "INDEPENDENT_PASS")
        self.assertEqual(
            decide_learning_update(
                execution_ok=True, execution_state="DONE", quality_gate=gate
            ),
            "RECORD_SUCCESS",
        )

    def test_tampered_attestation_signature_is_rejected(self):
        attestation, registry = signed_attestation()
        attestation["evidence"][0]["sha256"] = "c" * 64
        result = verify_quality_attestation(
            attestation,
            expected_run_id="run-fixture-001",
            trust_registry=registry,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "verifier_attestation_signature_invalid")

    def test_attestation_for_another_run_is_rejected(self):
        attestation, registry = signed_attestation()
        result = verify_quality_attestation(
            attestation,
            expected_run_id="different-run",
            trust_registry=registry,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "quality_attestation_run_binding_mismatch")

    def test_unregistered_verifier_key_is_rejected(self):
        attestation, registry = signed_attestation()
        registry["keys"] = []
        result = verify_quality_attestation(
            attestation,
            expected_run_id="run-fixture-001",
            trust_registry=registry,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "no_trusted_verifier_keys_registered")

    def test_revoked_verifier_key_is_rejected(self):
        attestation, registry = signed_attestation()
        registry["keys"][0]["status"] = "REVOKED"
        result = verify_quality_attestation(
            attestation,
            expected_run_id="run-fixture-001",
            trust_registry=registry,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "verifier_key_not_active")

    def test_trusted_key_cannot_claim_another_verifier_identity(self):
        attestation, registry = signed_attestation(verifier_identity="builder-001")
        result = verify_quality_attestation(
            attestation,
            expected_run_id="run-fixture-001",
            trust_registry=registry,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "verifier_not_independent_of_builder_or_repairer")

    def test_repairer_cannot_act_as_independent_verifier(self):
        attestation, registry = signed_attestation(
            repairer_identity="repair-001",
            verifier_identity="repair-001",
        )
        result = verify_quality_attestation(
            attestation,
            expected_run_id="run-fixture-001",
            trust_registry=registry,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "verifier_not_independent_of_builder_or_repairer")

    def test_bad_evidence_hash_is_rejected_before_signature_use(self):
        attestation, registry = signed_attestation()
        attestation["evidence"][0]["sha256"] = "not-a-hash"
        result = verify_quality_attestation(
            attestation,
            expected_run_id="run-fixture-001",
            trust_registry=registry,
        )
        self.assertFalse(result["ok"])
        self.assertEqual(result["reason"], "quality_evidence_sha256_invalid")

    def test_self_reported_integrity_boolean_is_not_accepted(self):
        gate = quality_verification_gate(
            {"quality_verification": {
                "verdict": "PASS",
                "builder_identity": "builder-001",
                "verifier_identity": "critic-003",
                "evidence_refs": ["receipt://evidence"],
                "receipt_ref": "receipt://quality",
                "receipt_integrity": "PASS",
            }},
            expected_run_id="run-fixture-001",
        )
        self.assertFalse(gate["eligible"])
        self.assertEqual(gate["reason"], "quality_attestation_missing")

    def test_failed_execution_remains_negative_learning_signal(self):
        gate = quality_verification_gate(
            {}, expected_run_id="run-fixture-001"
        )
        self.assertEqual(
            decide_learning_update(
                execution_ok=False, execution_state="FAILED", quality_gate=gate
            ),
            "RECORD_FAILURE",
        )


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FailClosedRegressionTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
