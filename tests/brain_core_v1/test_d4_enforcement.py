from scripts.brain_core_v1.d4_enforcement import enforce_d4


BASE_RECEIPT = {
    "receipt_type": "BRAIN_CORE_GATE_RESULT",
    "schema_version": "1.0.0",
    "status": "SUBMITTED",
    "author_runtime": "brain_core_v1",
    "subject_runtime": "public_brain_reply",
    "verifier_runtime": "test_suite",
    "input_hash": "abc123",
    "created_at": "2026-06-30T15:54:00Z",
    "reasons": [],
    "evidence": {
        "decision": {"allowed_claim_id": "sourcea_is_live"},
        "sanitized_output": {"ok": True, "public_language": "SourceA has public routes."},
    },
}


def test_valid_submitted_accepted() -> None:
    row = enforce_d4({**BASE_RECEIPT, "status": "SUBMITTED", "verifier_runtime": ""})
    assert row["ok"] is True
    assert row["lifecycle"] == "SUBMITTED"
    assert row["reasons"] == []


def test_valid_pass_accepted_only_with_independent_verifier() -> None:
    row = enforce_d4({**BASE_RECEIPT, "status": "PASS"})
    assert row["ok"] is True
    assert row["lifecycle"] == "PASS"
    assert row["author_verifier_separated"] is True
    assert row["author_subject_separated"] is True


def test_author_equals_verifier_pass_is_blocked() -> None:
    row = enforce_d4({**BASE_RECEIPT, "status": "PASS", "verifier_runtime": "brain_core_v1"})
    assert row["ok"] is False
    assert row["lifecycle"] == "BLOCKED"
    assert "author_verifier_not_independent" in row["reasons"]
    assert "protected_receipt_self_verified" in row["reasons"]


def test_missing_verifier_pass_is_blocked() -> None:
    row = enforce_d4({**BASE_RECEIPT, "status": "PASS", "verifier_runtime": ""})
    assert row["ok"] is False
    assert row["lifecycle"] == "BLOCKED"
    assert "missing_verifier_runtime" in row["reasons"]


def test_missing_evidence_pass_is_blocked() -> None:
    receipt = {**BASE_RECEIPT, "status": "PASS"}
    receipt.pop("evidence")
    row = enforce_d4(receipt)
    assert row["ok"] is False
    assert row["lifecycle"] == "BLOCKED"
    assert "missing_schema_field:evidence" in row["reasons"]
    assert "missing_evidence:evidence" in row["reasons"]


def test_fail_receipt_accepted_with_reason() -> None:
    row = enforce_d4({**BASE_RECEIPT, "status": "FAIL", "reasons": ["sanitizer_block"]})
    assert row["ok"] is True
    assert row["lifecycle"] == "FAIL"


def test_blocked_receipt_accepted_with_reason() -> None:
    row = enforce_d4({**BASE_RECEIPT, "status": "BLOCKED", "reasons": ["status_not_confident:unknown"]})
    assert row["ok"] is True
    assert row["lifecycle"] == "BLOCKED"


def test_deterministic_same_input_same_enforcement_result() -> None:
    receipt = {**BASE_RECEIPT, "status": "PASS"}
    assert enforce_d4(receipt) == enforce_d4(receipt)


def test_author_equals_subject_for_protected_receipt_is_blocked() -> None:
    row = enforce_d4({**BASE_RECEIPT, "status": "PASS", "subject_runtime": "brain_core_v1"})
    assert row["ok"] is False
    assert row["status"] == "BLOCKED"
    assert "author_subject_not_separated" in row["reasons"]


def test_deterministic_same_input_gives_same_enforcement_hash() -> None:
    receipt = {**BASE_RECEIPT, "status": "PASS"}
    assert enforce_d4(receipt)["enforcement_hash"] == enforce_d4(receipt)["enforcement_hash"]
