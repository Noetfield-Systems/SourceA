"""Canonical locked-definitions checksum validation for Brain Core v1."""
from __future__ import annotations

import hashlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CANONICAL_LOCKED_DEFINITIONS_PATH = ROOT / "reports" / "locked-definitions-v1.json"
EXPECTED_LOCKED_DEFINITIONS_SHA256 = "f680fdbe52785fadce427af7d1a92f340c8d3b57c92b2cbd7df55aeb5aee2bba"


def sha256_file(path: str | Path) -> str:
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def validate_locked_definitions_checksum(
    *,
    path: str | Path | None = CANONICAL_LOCKED_DEFINITIONS_PATH,
    expected_sha256: str | None = EXPECTED_LOCKED_DEFINITIONS_SHA256,
) -> dict[str, object]:
    """Return deterministic checksum validation for the canonical definitions source."""
    reasons: list[str] = []
    actual_sha256: str | None = None
    path_text = str(path) if path else None

    if not path:
        reasons.append("LOCKED_DEFINITIONS_CANONICAL_SOURCE_MISSING")
    elif not Path(path).is_file():
        reasons.append("LOCKED_DEFINITIONS_CANONICAL_SOURCE_MISSING")
    else:
        actual_sha256 = sha256_file(path)

    if not expected_sha256:
        reasons.append("LOCKED_DEFINITIONS_EXPECTED_SHA256_MISSING")

    match = bool(actual_sha256 and expected_sha256 and actual_sha256 == expected_sha256)
    if actual_sha256 and expected_sha256 and not match:
        reasons.append("LOCKED_DEFINITIONS_CHECKSUM_MISMATCH")

    return {
        "path": path_text,
        "expected_sha256": expected_sha256,
        "actual_sha256": actual_sha256,
        "match": match,
        "validation_result": "PASS" if match and not reasons else "BLOCK",
        "reasons": reasons,
    }
