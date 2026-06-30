import json
from pathlib import Path

from scripts.brain_core_v1.compatibility_probe import run_mock_cases


FIXTURE_PATH = Path("tests/brain_core_v1/fixtures/gate_receipts_v1.json")


def test_mock_compatibility_probe_has_required_cases() -> None:
    cases = run_mock_cases()
    ids = [case["id"] for case in cases]
    assert ids == [
        "sourcea_live_good",
        "sourcea_unknown_fake_pass",
        "forge_degraded_block",
        "proof_unknown",
    ]


def test_mock_compatibility_probe_receipts_are_deterministic() -> None:
    assert run_mock_cases() == run_mock_cases()


def test_fixture_matches_current_mock_probe() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert fixture["cases"] == run_mock_cases()


def test_fixture_covers_pass_block_unknown_degraded() -> None:
    fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    receipts = {case["id"]: case["receipt"] for case in fixture["cases"]}

    assert receipts["sourcea_live_good"]["gate_result"] == "PASS"
    assert receipts["sourcea_unknown_fake_pass"]["pass_claimed"] is True
    assert receipts["sourcea_unknown_fake_pass"]["gate_result"] == "BLOCK"
    assert "PASS" in receipts["sourcea_unknown_fake_pass"]["sanitized_output"]["forbidden_public_language_removed"]
    assert receipts["forge_degraded_block"]["gate_result"] == "BLOCK"
    assert receipts["proof_unknown"]["gate_result"] == "BLOCK"
