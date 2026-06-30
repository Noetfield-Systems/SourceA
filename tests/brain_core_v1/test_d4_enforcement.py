from scripts.brain_core_v1.d4_enforcement import enforce_d4


BASE_RECEIPT = {
    "receipt_type": "BRAIN_CORE_GATE_RESULT",
    "author_runtime": "brain_core_v1",
    "subject_runtime": "public_brain_reply",
    "verifier_runtime": "test_suite",
    "input_hash": "abc123",
    "sanitized_output": {"ok": True, "public_language": "SourceA has public routes."},
}


def test_valid_submitted_accepted() -> None:
    row = enforce_d4({**BASE_RECEIPT, "lifecycle": "SUBMITTED", "verifier_runtime": ""})
    assert row["ok"] is True
    assert row["lifecycle"] == "SUBMITTED"
    assert row["reasons"] == []


def test_valid_pass_accepted_only_with_independent_verifier() -> None:
    row = enforce_d4({**BASE_RECEIPT, "lifecycle": "PASS"})
    assert row["ok"] is True
    assert row["lifecycle"] == "PASS"
    assert row["author_verifier_separated"] is True
    assert row["author_subject_separated"] is True


def test_author_equals_verifier_pass_is_blocked() -> None:
    row = enforce_d4({**BASE_RECEIPT, "lifecycle": "PASS", "verifier_runtime": "brain_core_v1"})
    assert row["ok"] is False
    assert row["lifecycle"] == "BLOCKED"
    assert "author_verifier_not_independent" in row["reasons"]
    assert "protected_receipt_self_verified" in row["reasons"]


def test_missing_verifier_pass_is_blocked() -> None:
    row = enforce_d4({**BASE_RECEIPT, "lifecycle": "PASS", "verifier_runtime": ""})
    assert row["ok"] is False
    assert row["lifecycle"] == "BLOCKED"
    assert "missing_verifier_runtime" in row["reasons"]


def test_missing_evidence_pass_is_blocked() -> None:
    receipt = {**BASE_RECEIPT, "lifecycle": "PASS"}
    receipt.pop("sanitized_output")
    row = enforce_d4(receipt)
    assert row["ok"] is False
    assert row["lifecycle"] == "BLOCKED"
    assert "missing_evidence:sanitized_output" in row["reasons"]


def test_fail_receipt_accepted_with_reason() -> None:
    row = enforce_d4({**BASE_RECEIPT, "lifecycle": "FAIL", "reasons": ["sanitizer_block"]})
    assert row["ok"] is True
    assert row["lifecycle"] == "FAIL"


def test_blocked_receipt_accepted_with_reason() -> None:
    row = enforce_d4({**BASE_RECEIPT, "lifecycle": "BLOCKED", "reasons": ["status_not_confident:unknown"]})
    assert row["ok"] is True
    assert row["lifecycle"] == "BLOCKED"


def test_deterministic_same_input_same_enforcement_result() -> None:
    receipt = {**BASE_RECEIPT, "lifecycle": "PASS"}
    assert enforce_d4(receipt) == enforce_d4(receipt)
