"""Deterministic Brain Core v1 decision engine."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from scripts.brain_core_v1.status_map import get_status, ladder_for_status, resolve_status_key

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DEFINITIONS_PATH = ROOT / "reports" / "locked-definitions-v1.json"

CLAIM_SOURCEA_LIVE = "sourcea_is_live"
CLAIM_FORGE_RUNTIME = "forge_terminal_guaranteed_live_runtime"
CLAIM_PUBLIC_PROOF = "every_possible_run_has_public_proof"
CLAIM_BROKEN_GEARS = "broken_gears"

SUPPORTED_CLAIMS = {
    CLAIM_SOURCEA_LIVE,
    CLAIM_FORGE_RUNTIME,
    CLAIM_PUBLIC_PROOF,
    CLAIM_BROKEN_GEARS,
}


def load_locked_definitions(path: str | Path = DEFAULT_DEFINITIONS_PATH) -> dict[str, Any]:
    """Load locked definitions from disk."""
    return json.loads(Path(path).read_text(encoding="utf-8"))


def _claim_index(definitions: Mapping[str, Any]) -> dict[str, Mapping[str, Any]]:
    return {str(row.get("id")): row for row in definitions.get("claims", [])}


def classify_intent(user_message: str) -> str:
    """Classify public user intent using stable keyword precedence."""
    text = user_message.lower()

    if any(token in text for token in ("broken gears", "gear", "not connecting", "degraded", "unavailable", "broken", "does not connect")):
        if "forge" in text or "terminal" in text:
            return CLAIM_FORGE_RUNTIME
        if "proof" in text or "receipt" in text or "run" in text:
            return CLAIM_PUBLIC_PROOF
        return CLAIM_BROKEN_GEARS

    if "forge" in text or "terminal" in text:
        return CLAIM_FORGE_RUNTIME

    if "proof" in text or "receipt" in text or "every possible run" in text or "specific run" in text:
        return CLAIM_PUBLIC_PROOF

    if "sourcea" in text or "source a" in text or "live" in text or "up" in text or "status" in text:
        return CLAIM_SOURCEA_LIVE

    return CLAIM_SOURCEA_LIVE


def _fallback_for_gear(claim: Mapping[str, Any], gear: str) -> str | None:
    if gear == "unsure":
        return str(claim.get("fallback_when_unsure") or "")
    if gear == "degraded":
        return str(claim.get("fallback_when_degraded") or "")
    return None


def decide(
    user_message: str,
    live_status_map: Mapping[str, Any] | None = None,
    *,
    definitions: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return the deterministic decision object for a public user message."""
    locked_definitions = definitions or load_locked_definitions()
    claims = _claim_index(locked_definitions)
    claim_id = classify_intent(user_message)
    if claim_id not in SUPPORTED_CLAIMS or claim_id not in claims:
        claim_id = CLAIM_SOURCEA_LIVE

    claim = claims[claim_id]
    requires_status_signal = bool(claim.get("requires_status_signal"))
    raw_status_key = claim.get("status_key")
    status_key = resolve_status_key(str(raw_status_key) if raw_status_key else None, live_status_map or {})
    status = get_status(live_status_map, status_key)
    ladder_gear = ladder_for_status(status, requires_status_signal=requires_status_signal)
    approved_claim = str(claim.get("final_approved_claim") or claim.get("approved_text") or "")
    fallback_text = _fallback_for_gear(claim, ladder_gear)

    return {
        "schema": "brain-core-decision-v1",
        "intent": claim_id,
        "allowed_claim_id": claim_id,
        "requires_status_signal": requires_status_signal,
        "status_key": status_key,
        "status_value": status,
        "ladder_gear": ladder_gear,
        "approved_claim": approved_claim,
        "fallback_text": fallback_text,
        "draft_instructions": (
            "Draft public prose using only approved_claim when ladder_gear is confident, "
            "otherwise use fallback_text exactly. Do not invent status, pricing, product truth, "
            "definitions, or strategy. Do not expose PASS, BLOCK, OpenRouter, model names, "
            "API keys, Mac ports, internal factory jargon, or broken_gears."
        ),
        "deterministic": True,
    }
