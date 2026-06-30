from scripts.brain_core_v1.decision_core import load_locked_definitions
from scripts.brain_core_v1.gate import run_gate


DEFINITIONS = load_locked_definitions()
RECEIPT_FIELDS = {
    "receipt_type",
    "lifecycle",
    "gate_result",
    "decision",
    "live_status",
    "mapped_status",
    "pass_claimed",
    "reasons",
    "sanitized_output",
    "input_hash",
    "created_at",
    "author_runtime",
    "subject_runtime",
    "verifier_runtime",
    "d4_enforcement",
}


def test_live_healthy_pass_allowed_only_if_decision_confident() -> None:
    row = run_gate(
        "Is SourceA live?",
        live_status={"sourcea_app_http_status": {"status": "good", "http_status": 200}},
        definitions=DEFINITIONS,
    )
    assert row["gate_result"] == "PASS"
    assert row["receipt_type"] == "BRAIN_CORE_GATE_RESULT"
    assert RECEIPT_FIELDS.issubset(row)
    assert row["author_runtime"] == "brain_core_v1"
    assert row["subject_runtime"] == "public_brain_reply"
    assert row["verifier_runtime"] == "test_suite"
    assert row["d4_enforcement"]["ok"] is True
    assert row["decision"]["ladder_gear"] == "confident"
    assert row["decision"]["allowed_claim_id"] == "sourcea_is_live"
    assert row["sanitized_output"]["ok"] is True
    assert row["reasons"] == []


def test_live_unhealthy_blocks() -> None:
    row = run_gate(
        "Is Forge Terminal available?",
        live_status={"forge_terminal_runtime_status": {"status": "degraded", "http_status": 503}},
        definitions=DEFINITIONS,
    )
    assert row["gate_result"] == "BLOCK"
    assert row["receipt_type"] == "BRAIN_CORE_GATE_RESULT"
    assert RECEIPT_FIELDS.issubset(row)
    assert row["decision"]["allowed_claim_id"] == "forge_terminal_guaranteed_live_runtime"
    assert row["decision"]["ladder_gear"] == "degraded"
    assert "status_not_confident:degraded" in row["reasons"]


def test_fake_pass_claim_sanitized_and_blocked_when_status_unknown() -> None:
    row = run_gate(
        "Is SourceA live?",
        "SourceA is live because PASS.",
        live_status={"sourcea_app_http_status": {"status": "unknown", "error": "timeout"}},
        definitions=DEFINITIONS,
    )
    assert row["gate_result"] == "BLOCK"
    assert row["pass_claimed"] is True
    assert "PASS" in row["sanitized_output"]["forbidden_public_language_removed"]
    assert "PASS" not in row["sanitized_output"]["safe_public_language"]
    assert "PASS" not in str(row["sanitized_output"].get("public_language", ""))
    assert "pass_claimed_without_confident_status" in row["reasons"]


def test_unknown_live_state_blocks() -> None:
    row = run_gate(
        "Does every possible SourceA run have perfect public proof?",
        live_status={"specific_run_public_proof_status": {"status": "unknown"}},
        definitions=DEFINITIONS,
    )
    assert row["gate_result"] == "BLOCK"
    assert row["receipt_type"] == "BRAIN_CORE_GATE_RESULT"
    assert row["decision"]["allowed_claim_id"] == "every_possible_run_has_public_proof"
    assert row["decision"]["ladder_gear"] == "unsure"
    assert "status_not_confident:unsure" in row["reasons"]


def test_deterministic_same_input_same_output() -> None:
    kwargs = {
        "user_message": "Forge Terminal is not connecting.",
        "model_output": "Forge Terminal is BLOCK right now.",
        "live_status": {"forge_terminal_runtime_status": {"status": "degraded", "http_status": 503}},
        "definitions": DEFINITIONS,
    }
    first = run_gate(**kwargs)
    second = run_gate(**kwargs)
    assert first == second
    assert first["gate_result"] == "BLOCK"
    assert "BLOCK" in first["sanitized_output"]["forbidden_public_language_removed"]


def test_same_input_gives_same_input_hash() -> None:
    kwargs = {
        "user_message": "Is SourceA live?",
        "model_output": "SourceA is live because PASS.",
        "live_status": {"sourcea_app_http_status": {"status": "unknown", "error": "timeout"}},
        "definitions": DEFINITIONS,
        "created_at": "2026-06-30T15:46:00Z",
    }
    first = run_gate(**kwargs)
    second = run_gate(**kwargs)
    assert first["input_hash"] == second["input_hash"]
    assert len(first["input_hash"]) == 64
