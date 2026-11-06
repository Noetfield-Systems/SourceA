#!/usr/bin/env python3
"""Focused fail-closed regression checks for Founder Command integration."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from forge_swarm_blackboard_v1 import aggregate_critic_verdicts
from forge_agent_kernel_v1 import normalize_verifier_response
from forge_agent_kernel_v3_swarm import ForgeState, critics_reputation_eligible, swarm_quality_success
from forge_prompt_os_compiler_v3 import quality_verification_gate, decide_learning_update


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
        result = normalize_verifier_response({"ok": True, "parsed": {"pass": True, "note": "checks passed"}})
        self.assertIs(result["pass"], True)
        self.assertEqual(result["status"], "PASS")

    def test_swarm_success_requires_all_three_gates(self):
        good = [{"ok": True, "approved": True, "provider_error": False} for _ in range(3)]
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

    def test_single_critic_verdict_is_recorded_for_swarm_gate(self):
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

    def test_repairer_cannot_act_as_independent_verifier(self):
        gate = quality_verification_gate({"quality_verification": {
            "verdict": "PASS",
            "builder_identity": "builder-001",
            "repairer_identity": "repair-001",
            "verifier_identity": "repair-001",
            "evidence_refs": ["receipt://evidence"],
            "receipt_ref": "receipt://quality",
            "receipt_integrity": "PASS",
        }})
        self.assertFalse(gate["eligible"])
        self.assertEqual(gate["reason"], "builder_or_repairer_verifier_identity_missing_or_not_independent")

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

    def test_done_without_independent_quality_receipt_is_ineligible(self):
        gate = quality_verification_gate({"state": "DONE", "ok": True})
        self.assertFalse(gate["eligible"])
        self.assertEqual(
            decide_learning_update(execution_ok=True, execution_state="DONE", quality_gate=gate),
            "SKIP_UNVERIFIED",
        )

    def test_same_builder_and_verifier_cannot_pass(self):
        gate = quality_verification_gate({"quality_verification": {
            "verdict": "PASS",
            "builder_identity": "builder-001",
            "verifier_identity": "builder-001",
            "evidence_refs": ["receipt://evidence"],
            "receipt_ref": "receipt://quality",
            "receipt_integrity": "PASS",
        }})
        self.assertFalse(gate["eligible"])
        self.assertEqual(gate["reason"], "builder_verifier_identity_missing_or_not_independent")

    def test_independent_receipt_allows_positive_learning(self):
        gate = quality_verification_gate({"quality_verification": {
            "verdict": "PASS",
            "builder_identity": "builder-001",
            "verifier_identity": "critic-003",
            "evidence_refs": ["receipt://test-log", "receipt://diff"],
            "receipt_ref": "receipt://quality-pass",
            "receipt_integrity": "PASS",
        }})
        self.assertTrue(gate["eligible"])
        self.assertEqual(
            decide_learning_update(execution_ok=True, execution_state="DONE", quality_gate=gate),
            "RECORD_SUCCESS",
        )

    def test_failed_execution_remains_negative_learning_signal(self):
        gate = quality_verification_gate({})
        self.assertEqual(
            decide_learning_update(execution_ok=False, execution_state="FAILED", quality_gate=gate),
            "RECORD_FAILURE",
        )

    def test_missing_receipt_integrity_is_not_verified(self):
        gate = quality_verification_gate({"quality_verification": {
            "verdict": "PASS",
            "builder_identity": "builder-001",
            "verifier_identity": "critic-003",
            "evidence_refs": ["receipt://evidence"],
            "receipt_ref": "receipt://quality-pass",
            "receipt_integrity": "UNKNOWN",
        }})
        self.assertFalse(gate["eligible"])
        self.assertEqual(gate["reason"], "quality_receipt_integrity_not_pass")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(FailClosedRegressionTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
