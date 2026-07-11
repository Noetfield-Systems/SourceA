"""Optional LLM excellence reviewer — additive scoring, non-blocking by default."""
from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from typing import Any

from content_quality_spine.llm_bridge import dispatch_excellence_llm, resolve_sourcea_scripts

PROMPT_VERSION = "llm-excellence-reviewer-v1"
EXCELLENCE_DIMENSIONS: dict[str, int] = {
    "natural_conversational_flow": 20,
    "specificity_and_realism": 15,
    "emotional_and_tonal_fit": 15,
    "clarity_and_efficiency": 15,
    "domain_authenticity": 15,
    "creative_or_memorable_expression": 10,
    "overall_coherence": 10,
}

LANGUAGE_ROLE_MAP = {
    "language": "spoken naturalness, grammar, customer-facing language",
    "reasoning": "conversation progression, contradictions, missing steps",
    "proof": "claim/evidence and tool-state interpretation",
    "advisor": "domain fit and commercial usefulness",
    "critic": "tone, realism, clarity, originality",
    "close": "outcome-specific final expression",
    "judge": "aggregate excellence score and targeted recommendation",
}

REUSED_ASSETS = {
    "scripts/chat_founder_loop_v1.py": "7-stage language layer (language→reasoning→proof→advisor→critic→close)",
    "scripts/chat_founder_language_v1.py": "rule-based language compose + optional AI polish",
    "scripts/ai_unify_api_v1.py": "dispatch_raw provider routing + receipts",
    "scripts/model_dispatch.py": "cost gate + forge model matrix",
    "data/cursor-cost-intelligence-routing-v1.json": "low-cost tier default policy",
}

JUDGE_SYSTEM = """You are the llm_excellence_reviewer judge for content-quality-spine.

Score ADDITIVELY from 0 per dimension. Award points ONLY when positive_evidence cites exact lines.
Generic praise earns zero points. Missing evidence means zero for that dimension.

Language layer roles (single bounded call):
- language: spoken naturalness, grammar, customer-facing language
- reasoning: conversation progression, contradictions, missing steps
- proof: claim/evidence and tool-state interpretation
- advisor: domain fit and commercial usefulness
- critic: tone, realism, clarity, originality
- close: outcome-specific final expression
- judge: aggregate excellence score and targeted recommendation

Calibration:
- 90+ on a dimension requires multiple precise positive_evidence citations with line, exact_text, reason
- 95+ overall requires written distinction from ordinary strong work in exceptional_distinction
- 100 overall only for calibrated reference-quality output with exceptional distinction text
- Known-bad artifacts (policy leaks, fake confirmations, medical advice) must score low with specific weaknesses

You MUST populate every dimension object with score, max, positive_evidence (array), weaknesses (array), targeted_improvement, confidence.
Every positive_evidence item MUST include line, speaker_if_applicable, exact_text (verbatim quote), reason.

Example positive_evidence item:
{"line": 3, "speaker_if_applicable": "Receptionist", "exact_text": "Is the water actively running?", "reason": "Natural triage question"}

Return ONLY valid JSON:
{
  "excellence_score": <0-100 sum of dimension scores>,
  "dimensions": {
    "<dimension_key>": {
      "score": <int>,
      "max": <int>,
      "positive_evidence": [{"line": <int|null>, "speaker_if_applicable": <str|null>, "exact_text": <str>, "reason": <str>}],
      "weaknesses": [<str>],
      "targeted_improvement": <str>,
      "confidence": <0.0-1.0>
    }
  },
  "exceptional_distinction": <str|null>,
  "quality_recommendation": <str>
}"""


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _extract_json(raw: str) -> dict[str, Any] | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        return None
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:
        return None


def _empty_dimension(max_pts: int) -> dict[str, Any]:
    return {
        "score": 0,
        "max": max_pts,
        "positive_evidence": [],
        "weaknesses": [],
        "targeted_improvement": "",
        "confidence": 0.0,
    }


def _normalize_evidence(items: list[Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for item in items or []:
        if not isinstance(item, dict):
            continue
        exact = (item.get("exact_text") or item.get("text") or item.get("quote") or "").strip()
        if not exact:
            continue
        out.append(
            {
                "line": item.get("line"),
                "speaker_if_applicable": item.get("speaker_if_applicable") or item.get("speaker"),
                "exact_text": exact,
                "reason": item.get("reason") or item.get("why") or "",
            }
        )
    return out


def _normalize_dimensions(parsed: dict[str, Any]) -> dict[str, Any]:
    dims = parsed.get("dimensions")
    if isinstance(dims, list):
        mapped: dict[str, Any] = {}
        for row in dims:
            if not isinstance(row, dict):
                continue
            key = row.get("dimension") or row.get("name") or row.get("key")
            if key:
                mapped[str(key)] = row
        dims = mapped
    if not isinstance(dims, dict):
        dims = {}
    return dims


def _apply_calibration(parsed: dict[str, Any]) -> dict[str, Any]:
    dims_in = _normalize_dimensions(parsed)
    dims_out: dict[str, Any] = {}
    total = 0
    for key, max_pts in EXCELLENCE_DIMENSIONS.items():
        row = dict(dims_in.get(key) or _empty_dimension(max_pts))
        row["max"] = max_pts
        row["positive_evidence"] = _normalize_evidence(row.get("positive_evidence"))
        weaknesses = [w for w in (row.get("weaknesses") or []) if str(w).strip()]
        row["weaknesses"] = weaknesses
        raw_score = int(row.get("score") or 0)
        evidence = row["positive_evidence"]
        if not evidence:
            if weaknesses and raw_score > 0:
                row["score"] = min(raw_score, int(max_pts * 0.35))
            else:
                row["score"] = 0
        else:
            capped = raw_score
            if capped >= max_pts * 0.9 and len(evidence) < 2:
                capped = min(capped, int(max_pts * 0.75))
            row["score"] = max(0, min(max_pts, capped))
        total += row["score"]
        dims_out[key] = row

    parsed_total = parsed.get("excellence_score")
    if total == 0 and isinstance(parsed_total, (int, float)) and parsed_total > 0:
        total = int(parsed_total)

    distinction = (parsed.get("exceptional_distinction") or "").strip()
    if total >= 95 and not distinction:
        total = min(total, 94)
    if total >= 100 and len(distinction) < 40:
        total = min(total, 99)
    if total >= 90 and sum(len(d.get("positive_evidence") or []) for d in dims_out.values()) < 2:
        total = min(total, 89)

    return {
        "excellence_score": total,
        "dimensions": dims_out,
        "exceptional_distinction": distinction or None,
        "quality_recommendation": parsed.get("quality_recommendation") or "",
    }


def _build_user_prompt(*, artifact: dict[str, Any], adapter: dict[str, Any]) -> str:
    body = artifact.get("body") or artifact.get("transcript") or artifact.get("text") or ""
    meta = {
        "artifact_type": artifact.get("artifact_type") or adapter.get("artifact_type"),
        "domain_profile": adapter.get("domain_profile"),
        "summary": adapter.get("summary"),
        "tool_evidence": adapter.get("tool_evidence"),
    }
    return json.dumps({"artifact_body": body, "adapter_meta": meta}, ensure_ascii=False, indent=2)


def _build_receipt(
    *,
    status: str,
    excellence_score: int | None,
    reason: str,
    calibrated: dict[str, Any] | None,
    llm_raw: dict[str, Any] | None,
    input_hash: str,
    llm_mode: str,
    pipeline_continues: bool = True,
) -> dict[str, Any]:
    structured_hash = _hash_text(json.dumps(calibrated or {}, sort_keys=True))
    usage = (llm_raw or {}).get("usage") or {}
    gate = (llm_raw or {}).get("gate") or {}
    has_usage = bool(usage)
    token_usage = usage if has_usage else None
    estimated_cost = usage.get("estimated_cost") if has_usage else None
    actual_cost = usage.get("actual_cost") if has_usage else None
    cost_status = "REPORTED" if estimated_cost is not None or actual_cost is not None else "NOT_REPORTED_BY_PROVIDER_PATH"
    return {
        "schema": "llm-excellence-receipt-v1",
        "evaluator": "llm_excellence_reviewer",
        "status": status,
        "score": excellence_score,
        "excellence_score": excellence_score,
        "llm_excellence_bonus": round(excellence_score / 10) if excellence_score is not None else None,
        "reason": reason,
        "llm_mode": llm_mode,
        "pipeline_continues": pipeline_continues,
        "scoring_model": "additive",
        "excellence_score_start": 0,
        "language_role_mapping": LANGUAGE_ROLE_MAP,
        "reused_language_assets": REUSED_ASSETS,
        "prompt_version": PROMPT_VERSION,
        "dimensions": (calibrated or {}).get("dimensions"),
        "quality_recommendation": (calibrated or {}).get("quality_recommendation"),
        "exceptional_distinction": (calibrated or {}).get("exceptional_distinction"),
        "receipt": {
            "provider": (llm_raw or {}).get("provider"),
            "model": (llm_raw or {}).get("model") or (llm_raw or {}).get("api_model"),
            "role": "judge",
            "prompt_version": PROMPT_VERSION,
            "input_hash": input_hash,
            "structured_output_hash": structured_hash if calibrated else None,
            "token_usage": token_usage,
            "estimated_cost": estimated_cost,
            "actual_cost_if_available": actual_cost,
            "cost_status": cost_status,
            "cost_policy_pass": gate.get("mode") in ("light", "explicit_lock", "bypass", None) or status in ("NOT_EVALUATED", "SKIPPED"),
            "timestamp": _now(),
        },
        "sourcea_scripts_path": str(resolve_sourcea_scripts() or ""),
    }


def evaluate_excellence(
    *,
    artifact: dict[str, Any],
    adapter: dict[str, Any],
    llm_mode: str = "off",
) -> dict[str, Any]:
    mode = (llm_mode or "off").lower()
    if mode == "off":
        return _build_receipt(
            status="SKIPPED",
            excellence_score=None,
            reason="LLM_MODE_OFF",
            calibrated=None,
            llm_raw=None,
            input_hash="",
            llm_mode=mode,
        )

    user_prompt = _build_user_prompt(artifact=artifact, adapter=adapter)
    input_hash = _hash_text(JUDGE_SYSTEM + user_prompt)

    llm_raw = dispatch_excellence_llm(system=JUDGE_SYSTEM, user=user_prompt[:48000])
    if not llm_raw.get("ok"):
        err = llm_raw.get("error") or "LLM_UNAVAILABLE_OR_BUDGET_POLICY"
        return _build_receipt(
            status="NOT_EVALUATED",
            excellence_score=None,
            reason="LLM_UNAVAILABLE_OR_BUDGET_POLICY" if "key" in str(err) or err == "no_api_key" else str(err),
            calibrated=None,
            llm_raw=llm_raw,
            input_hash=input_hash,
            llm_mode=mode,
        )

    parsed = _extract_json(llm_raw.get("response") or "")
    if not parsed:
        return _build_receipt(
            status="NOT_EVALUATED",
            excellence_score=None,
            reason="LLM_PARSE_FAILED",
            calibrated=None,
            llm_raw=llm_raw,
            input_hash=input_hash,
            llm_mode=mode,
        )

    calibrated = _apply_calibration(parsed)
    return _build_receipt(
        status="EVALUATED",
        excellence_score=calibrated["excellence_score"],
        reason="OK",
        calibrated=calibrated,
        llm_raw=llm_raw,
        input_hash=input_hash,
        llm_mode=mode,
    )


def score_distribution(scores: list[int | None]) -> dict[str, Any]:
    vals = [s for s in scores if isinstance(s, int)]
    if not vals:
        return {
            "minimum": None,
            "maximum": None,
            "mean": None,
            "median": None,
            "standard_deviation": None,
            "90_plus_count": 0,
            "95_plus_count": 0,
            "100_count": 0,
            "calibration_warning": False,
            "sample_count": 0,
        }
    vals_sorted = sorted(vals)
    n = len(vals_sorted)
    mean = sum(vals_sorted) / n
    mid = n // 2
    median = vals_sorted[mid] if n % 2 else (vals_sorted[mid - 1] + vals_sorted[mid]) / 2
    variance = sum((x - mean) ** 2 for x in vals_sorted) / n
    c90 = sum(1 for x in vals_sorted if x >= 90)
    c95 = sum(1 for x in vals_sorted if x >= 95)
    c100 = sum(1 for x in vals_sorted if x == 100)
    warn = n >= 5 and (c95 / n) > 0.35
    return {
        "minimum": vals_sorted[0],
        "maximum": vals_sorted[-1],
        "mean": round(mean, 2),
        "median": median,
        "standard_deviation": round(variance**0.5, 2),
        "90_plus_count": c90,
        "95_plus_count": c95,
        "100_count": c100,
        "calibration_warning": warn,
        "sample_count": n,
    }
