from pathlib import Path

from scripts.brain_core_v1.gate import run_gate
from scripts.brain_core_v1.locked_definitions import sha256_file, validate_locked_definitions_checksum


def test_valid_checksum_pass(tmp_path: Path) -> None:
    path = tmp_path / "locked-definitions.json"
    path.write_text('{"schema":"test"}\n')
    expected = sha256_file(path)
    row = validate_locked_definitions_checksum(path=path, expected_sha256=expected)
    assert row["validation_result"] == "PASS"
    assert row["match"] is True
    assert row["actual_sha256"] == expected
    assert row["reasons"] == []


def test_checksum_mismatch_blocks(tmp_path: Path) -> None:
    path = tmp_path / "locked-definitions.json"
    path.write_text('{"schema":"test"}\n')
    row = validate_locked_definitions_checksum(path=path, expected_sha256="0" * 64)
    assert row["validation_result"] == "BLOCK"
    assert row["match"] is False
    assert "LOCKED_DEFINITIONS_CHECKSUM_MISMATCH" in row["reasons"]


def test_missing_file_blocks(tmp_path: Path) -> None:
    path = tmp_path / "missing.json"
    row = validate_locked_definitions_checksum(path=path, expected_sha256="0" * 64)
    assert row["validation_result"] == "BLOCK"
    assert row["actual_sha256"] is None
    assert "LOCKED_DEFINITIONS_CANONICAL_SOURCE_MISSING" in row["reasons"]


def test_missing_canonical_path_blocks() -> None:
    row = validate_locked_definitions_checksum(path=None, expected_sha256="0" * 64)
    assert row["validation_result"] == "BLOCK"
    assert row["path"] is None
    assert "LOCKED_DEFINITIONS_CANONICAL_SOURCE_MISSING" in row["reasons"]


def test_gate_blocks_on_checksum_block(tmp_path: Path) -> None:
    path = tmp_path / "locked-definitions.json"
    path.write_text('{"claims":[]}\n')
    row = run_gate(
        "Is SourceA live?",
        live_status={"sourcea_app_http_status": {"status": "good"}},
        definitions_path=path,
        expected_definitions_sha256="1" * 64,
    )
    assert row["gate_result"] == "BLOCK"
    assert row["status"] == "BLOCKED"
    assert row["locked_definitions_validation"]["validation_result"] == "BLOCK"
    assert "locked_definitions_checksum_block" in row["reasons"]


def test_checksum_validation_deterministic_same_input(tmp_path: Path) -> None:
    path = tmp_path / "locked-definitions.json"
    path.write_text('{"schema":"test"}\n')
    expected = sha256_file(path)
    first = validate_locked_definitions_checksum(path=path, expected_sha256=expected)
    second = validate_locked_definitions_checksum(path=path, expected_sha256=expected)
    assert first == second
