"""Deterministic public-output sanitizer for Brain Core v1."""
from __future__ import annotations

import re
from typing import Any, Mapping

FORBIDDEN_PATTERNS: list[tuple[str, re.Pattern[str], str]] = [
    ("API keys", re.compile(r"\b(?:api[_ -]?key|sk-[A-Za-z0-9_-]+|CF_[A-Z0-9_]*TOKEN)\b[:=]?\s*[A-Za-z0-9_-]*", re.I), ""),
    ("OpenRouter", re.compile(r"\bOpenRouter\b", re.I), ""),
    ("model names", re.compile(r"\b(?:Llama|Qwen|Gemini|Claude|GPT-?4o?|DeepSeek|OpenAI)\b(?:\s+[A-Za-z0-9.:-]+){0,4}", re.I), "AI model"),
    ("Mac ports", re.compile(r"\b(?:https?://)?(?:127\.0\.0\.1|localhost):\d+\b|:\b13\d{3}\b", re.I), ""),
    ("internal factory jargon", re.compile(r"\binternal factory\b|\bfactory jargon\b|\bcloud forge railway\b", re.I), "public route"),
    ("broken_gears", re.compile(r"\bbroken_gears\b|\bbroken gears\b", re.I), "the route/tool/status looks unavailable, incomplete, or needs review"),
    ("PASS", re.compile(r"\bPASS\b", re.I), "available"),
    ("BLOCK", re.compile(r"\bBLOCK\b", re.I), "needs review"),
]

UNIVERSAL_PROOF = re.compile(r"\bevery (?:possible )?sourcea run (?:always )?has perfect public proof\b", re.I)
PRICING = re.compile(r"(?:[$]\s*\d+|\b\d+\s*(?:usd|dollars?)\b|\bper\s+month\b|\b/month\b)", re.I)
UNSUPPORTED_HEALTH = re.compile(r"\bfully healthy\b|\bevery internal system\b|\ball internal systems\b", re.I)


def _approved_text(decision: Mapping[str, Any]) -> str:
    fallback = decision.get("fallback_text")
    if fallback:
        return str(fallback)
    return str(decision.get("approved_claim") or "")


def _remove_forbidden(text: str) -> tuple[str, list[str]]:
    output = text
    removed: list[str] = []
    for label, pattern, replacement in FORBIDDEN_PATTERNS:
        if pattern.search(output):
            removed.append(label)
            output = pattern.sub(replacement, output)
    output = re.sub(r"\s+", " ", output).strip()
    output = re.sub(r"\s+([,.!?])", r"\1", output)
    output = re.sub(r"\(\s*\)", "", output).strip()
    return output, removed


def _blocks_supported_claim(decision: Mapping[str, Any], text: str) -> str | None:
    gear = str(decision.get("ladder_gear") or "")
    if UNIVERSAL_PROOF.search(text):
        return "unsupported_universal_proof_claim"
    if PRICING.search(text):
        return "pricing_invented"
    if UNSUPPORTED_HEALTH.search(text):
        return "unsupported_public_claim"
    if gear != "confident" and re.search(r"\bSourceA is live\b", text, re.I):
        return "status_invented_or_strengthened"
    if gear != "confident" and re.search(r"\bForge Terminal is available\b", text, re.I):
        return "status_invented_or_strengthened"
    return None


def sanitize_model_output(decision: Mapping[str, Any], model_output: str) -> dict[str, Any]:
    """Sanitize model output and enforce the pre-model decision object."""
    safe_text = _approved_text(decision)
    if not model_output:
        return {
            "ok": True,
            "public_language": safe_text,
            "forbidden_public_language_removed": [],
        }

    raw_block_reason = _blocks_supported_claim(decision, model_output)
    sanitized, removed = _remove_forbidden(model_output)
    block_reason = raw_block_reason or _blocks_supported_claim(decision, sanitized)
    if "API keys" in removed:
        block_reason = "secret_or_api_key_leak"

    if block_reason:
        return {
            "ok": False,
            "reason": block_reason,
            "safe_public_language": safe_text,
            "forbidden_public_language_removed": removed,
        }

    # Any forbidden removal means the model drifted; use the approved text as the final public output.
    if removed:
        return {
            "ok": True,
            "public_language": safe_text,
            "forbidden_public_language_removed": removed,
        }

    if sanitized.strip() != safe_text.strip():
        return {
            "ok": False,
            "reason": "unsupported_public_claim",
            "safe_public_language": safe_text,
            "forbidden_public_language_removed": removed,
        }

    return {
        "ok": True,
        "public_language": sanitized,
        "forbidden_public_language_removed": removed,
    }
