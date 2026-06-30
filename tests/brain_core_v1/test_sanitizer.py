from scripts.brain_core_v1.decision_core import decide, load_locked_definitions
from scripts.brain_core_v1.sanitizer import sanitize_model_output


DEFINITIONS = load_locked_definitions()


def test_pass_never_survives_sanitizer() -> None:
    decision = decide("Is SourceA live?", {"sourcea_app_http_status": "ok"}, definitions=DEFINITIONS)
    row = sanitize_model_output(decision, "Live proof is available (PASS).")
    assert row["ok"] is True
    assert "PASS" in row["forbidden_public_language_removed"]
    assert "PASS" not in row["public_language"]


def test_block_never_survives_sanitizer() -> None:
    decision = decide(
        "Forge Terminal is not connecting.",
        {"forge_terminal_runtime_status": "degraded"},
        definitions=DEFINITIONS,
    )
    row = sanitize_model_output(decision, "Forge Terminal is BLOCK right now.")
    assert row["ok"] is True
    assert "BLOCK" in row["forbidden_public_language_removed"]
    assert "BLOCK" not in row["public_language"]
    assert row["public_language"] == decision["fallback_text"]


def test_openrouter_model_name_and_mac_port_removed() -> None:
    decision = decide("Can I try Forge Terminal?", {}, definitions=DEFINITIONS)
    row = sanitize_model_output(decision, "OpenRouter with Llama says try http://127.0.0.1:13029.")
    assert row["ok"] is True
    assert "OpenRouter" in row["forbidden_public_language_removed"]
    assert "model names" in row["forbidden_public_language_removed"]
    assert "Mac ports" in row["forbidden_public_language_removed"]
    assert "OpenRouter" not in row["public_language"]
    assert "Llama" not in row["public_language"]
    assert "13029" not in row["public_language"]


def test_api_key_language_blocks_output() -> None:
    decision = decide("Is SourceA live?", {"sourcea_app_http_status": "ok"}, definitions=DEFINITIONS)
    row = sanitize_model_output(decision, "SourceA is live. API key: sk-test-123.")
    assert row["ok"] is False
    assert row["reason"] == "secret_or_api_key_leak"
    assert "sk-test-123" not in row["safe_public_language"]


def test_internal_factory_jargon_removed() -> None:
    decision = decide("Is SourceA up?", {"sourcea_app_http_status": "degraded"}, definitions=DEFINITIONS)
    row = sanitize_model_output(decision, "The internal factory is degraded.")
    assert row["ok"] is True
    assert "internal factory jargon" in row["forbidden_public_language_removed"]
    assert "internal factory" not in row["public_language"].lower()
    assert row["public_language"] == decision["fallback_text"]


def test_broken_gears_private_language_removed() -> None:
    decision = decide("Something is broken in the product route.", {"route_or_tool_status": "degraded"}, definitions=DEFINITIONS)
    row = sanitize_model_output(decision, "broken_gears detected. The path is BLOCK.")
    assert row["ok"] is True
    assert "broken_gears" in row["forbidden_public_language_removed"]
    assert "BLOCK" in row["forbidden_public_language_removed"]
    assert "broken" not in row["public_language"].lower()
    assert "BLOCK" not in row["public_language"]


def test_model_output_cannot_add_unapproved_status_claim() -> None:
    decision = decide("Is SourceA live?", {}, definitions=DEFINITIONS)
    row = sanitize_model_output(decision, "SourceA is live.")
    assert row["ok"] is False
    assert row["reason"] == "status_invented_or_strengthened"
    assert row["safe_public_language"] == decision["fallback_text"]


def test_model_output_cannot_add_unapproved_universal_proof_claim() -> None:
    decision = decide("Does every possible SourceA run have perfect public proof?", {}, definitions=DEFINITIONS)
    row = sanitize_model_output(decision, "Every possible SourceA run has perfect public proof.")
    assert row["ok"] is False
    assert row["reason"] == "unsupported_universal_proof_claim"
    assert row["safe_public_language"] == decision["fallback_text"]


def test_model_output_cannot_invent_pricing() -> None:
    decision = decide("Is SourceA live?", {"sourcea_app_http_status": "ok"}, definitions=DEFINITIONS)
    row = sanitize_model_output(decision, "SourceA is live and costs $99/month.")
    assert row["ok"] is False
    assert row["reason"] == "pricing_invented"
