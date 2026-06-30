from scripts.brain_core_v1.decision_core import (
    CLAIM_BROKEN_GEARS,
    CLAIM_FORGE_RUNTIME,
    CLAIM_PUBLIC_PROOF,
    CLAIM_SOURCEA_LIVE,
    decide,
    load_locked_definitions,
)


DEFINITIONS = load_locked_definitions()


def test_same_input_same_decision() -> None:
    status = {"forge_terminal_runtime_status": "unknown"}
    first = decide("Is Forge Terminal available?", status, definitions=DEFINITIONS)
    second = decide("Is Forge Terminal available?", status, definitions=DEFINITIONS)
    assert first == second
    assert first["deterministic"] is True


def test_live_signal_good_confident_gear() -> None:
    row = decide("Is SourceA live?", {"sourcea_app_http_status": "ok"}, definitions=DEFINITIONS)
    assert row["intent"] == CLAIM_SOURCEA_LIVE
    assert row["allowed_claim_id"] == CLAIM_SOURCEA_LIVE
    assert row["requires_status_signal"] is True
    assert row["status_key"] == "sourcea_app_http_status"
    assert row["status_value"] == "ok"
    assert row["ladder_gear"] == "confident"
    assert row["fallback_text"] is None
    assert "fresh site/status check" in row["approved_claim"]


def test_missing_signal_unsure_gear() -> None:
    row = decide("Is SourceA live?", {}, definitions=DEFINITIONS)
    assert row["intent"] == CLAIM_SOURCEA_LIVE
    assert row["status_value"] == "unknown"
    assert row["ladder_gear"] == "unsure"
    assert row["fallback_text"] == (
        "SourceA has public product routes on sourcea.app. I don’t have a fresh live-status check "
        "in this answer, so start from the current product route."
    )


def test_degraded_signal_degraded_gear() -> None:
    row = decide(
        "Forge Terminal is not connecting.",
        {"forge_terminal_runtime_status": "degraded"},
        definitions=DEFINITIONS,
    )
    assert row["intent"] == CLAIM_FORGE_RUNTIME
    assert row["status_key"] == "forge_terminal_runtime_status"
    assert row["status_value"] == "degraded"
    assert row["ladder_gear"] == "degraded"
    assert row["fallback_text"] == (
        "Forge Terminal may be degraded right now. Start from the SourceA product/proof route, "
        "then use the demo escalation if the browser route does not connect."
    )


def test_public_proof_uses_specific_status_signal() -> None:
    row = decide("Does every possible SourceA run have perfect public proof?", {}, definitions=DEFINITIONS)
    assert row["intent"] == CLAIM_PUBLIC_PROOF
    assert row["status_key"] == "specific_run_public_proof_status"
    assert row["ladder_gear"] == "unsure"
    assert "Do not claim every possible run has perfect public proof" in row["approved_claim"]


def test_broken_gears_resolves_route_status_key() -> None:
    row = decide(
        "Something is broken in the product route.",
        {"route_or_tool_status": "unavailable"},
        definitions=DEFINITIONS,
    )
    assert row["intent"] == CLAIM_BROKEN_GEARS
    assert row["status_key"] == "route_or_tool_status"
    assert row["status_value"] == "unavailable"
    assert row["ladder_gear"] == "degraded"
    assert "degraded or unavailable" in row["fallback_text"]
