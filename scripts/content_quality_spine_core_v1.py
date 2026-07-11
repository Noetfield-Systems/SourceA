#!/usr/bin/env python3
"""Shared content-quality spine core — artifact adapters over deterministic + rule-based semantic gates.

Law: data/content-quality-spine/CONTENT_QUALITY_CANONICALIZATION_DECISION_v1.md
Schema: data/content-quality-spine/shared-content-quality-schema-v1.json

Reuses: outbound_email_linter_v1, landing gate patterns, commercial-film routing,
SourceB conversation-script-logic (ported patterns). No paid synthesis or send.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SPINE = ROOT / "data" / "content-quality-spine"
SINA = Path.home() / ".sina"

PASS_TYPES = (
    "DETERMINISTIC_STRUCTURE_PASS",
    "SEMANTIC_QUALITY_PASS",
    "DOMAIN_POLICY_PASS",
    "TRUTH_EVIDENCE_PASS",
    "OUTPUT_ASSET_PASS",
    "LIVE_SURFACE_PASS",
)

SYSTEM_LANGUAGE = (
    "on this line",
    "flagged",
    "queued",
    "ticket created",
    "passed to scheduling",
    "sent to on-call",
    "workflow",
    "database",
    "escalation state",
    "highest-confidence",
    "brain-os",
    "receipt-native",
)

UNSUPPORTED_PROMISE_PATTERNS = (
    (r"\barrive (?:at|by) \d", "R8", "promise.arrival_time"),
    (r"call you (?:back )?(?:within|in) \d+ (?:minute|hour)", "R8", "promise.callback_time"),
    (r"\bguaranteed\b", "R8", "promise.guaranteed"),
    (r"maintenance will call within", "R8", "promise.sla_unverified"),
    (r"\bdispatched emergency\b", "R1", "claim.dispatch_without_receipt"),
)

ARTIFACT_CLASSES = {
    "ivr_receptionist": "E_ivr_receptionist",
    "product_demo_dialogue": "B_product_demo_dialogue",
    "commercial_film": "A_commercial_vo",
    "email": "email_outreach",
    "sales_outreach": "email_outreach",
    "website_copy": "website_copy",
    "landing_page": "website_copy",
    "proof_lab": "D_proof_lab",
    "avatar_social": "C_avatar_social",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _dim(name: str, *, status: str, score: int | None, evaluator: str | None) -> dict[str, Any]:
    return {"dimension": name, "status": status, "score": score, "evaluator": evaluator}


def _unevaluated_dims(names: tuple[str, ...]) -> list[dict[str, Any]]:
    return [_dim(n, status="NOT_EVALUATED", score=None, evaluator=None) for n in names]


def classify_artifact(artifact_type: str) -> dict[str, Any]:
    key = artifact_type.strip().lower().replace("-", "_")
    cls = ARTIFACT_CLASSES.get(key, "unknown")
    return {
        "artifact_type": key,
        "artifact_class": cls,
        "classifier": "content_quality_spine_core_v1.classify_artifact",
    }


def _parse_conversation_turns(text: str) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = []
    line_no = 0
    for raw in text.splitlines():
        line_no += 1
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r"^\*\*(Receptionist|Caller|Agent|Customer):\*\*\s*(.+)$", s, re.I)
        if m:
            turns.append({"line": line_no, "speaker": m.group(1).title(), "text": m.group(2).strip()})
            continue
        m2 = re.match(r"^(Receptionist|Caller|Agent|Customer):\s*(.+)$", s, re.I)
        if m2:
            turns.append({"line": line_no, "speaker": m2.group(1).title(), "text": m2.group(2).strip()})
    return turns


def deterministic_ivr(text: str, *, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    evidence = evidence or {}
    turns = _parse_conversation_turns(text)
    all_text = "\n".join(t["text"] for t in turns)
    low = all_text.lower()
    violations: list[dict[str, Any]] = []

    for phrase in SYSTEM_LANGUAGE:
        if phrase in low:
            violations.append(
                {
                    "rule": "R3",
                    "line": next((t["line"] for t in turns if phrase in t["text"].lower()), None),
                    "match": phrase,
                    "reason": "Internal/system language on customer-facing line",
                }
            )

    for pattern, rule, vid in UNSUPPORTED_PROMISE_PATTERNS:
        m = re.search(pattern, all_text, re.I)
        if m:
            violations.append(
                {
                    "rule": rule,
                    "id": vid,
                    "match": m.group(0),
                    "reason": "Unsupported promise or action claim",
                }
            )

    if re.search(r"drive safe", low) and re.search(r"grind|brake|unsafe", low):
        violations.append(
            {
                "rule": "R6",
                "match": "drive safe",
                "reason": "Dismissive safety close after brake hazard report",
            }
        )

    if re.search(r"cannot give pricing on this line", low):
        violations.append(
            {
                "rule": "R7",
                "match": "cannot give pricing on this line",
                "reason": "Policy leakage instead of useful next action",
            }
        )

    if re.search(r"cannot provide medical advice", low) and re.search(
        r"\b(take|try|use|recommend)\b.+\b(medicine|pill|dose|treatment)\b", low
    ):
        violations.append(
            {
                "rule": "R6",
                "reason": "Medical disclaimer followed by improvised medical advice",
            }
        )

    capability = str(evidence.get("capability_state") or "")
    if re.search(r"\bappointment is confirmed\b", low) and evidence.get("terminal_outcome") != "appointment_confirmed":
        violations.append(
            {
                "rule": "R9",
                "reason": "Request state upgraded into confirmed state",
            }
        )

    if re.search(r"\bI updated\b|\breservation is updated\b", low) and not evidence.get("update_receipt"):
        violations.append(
            {
                "rule": "R1",
                "reason": "Reservation update implied without update receipt",
            }
        )

    if re.search(r"\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday).*(?:open|available)\b", low):
        if not evidence.get("calendar_lookup"):
            violations.append(
                {
                    "rule": "R1",
                    "reason": "Calendar availability claimed without lookup result",
                }
            )

    if re.search(r"\bSourceB\b|\bSourceA\b", all_text) and any(t["speaker"] == "Receptionist" for t in turns):
        violations.append(
            {
                "rule": "R3",
                "reason": "Platform brand spoken inside customer IVR call",
            }
        )

    raw_digits = re.search(r"\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b", all_text)
    if raw_digits and "spoken" not in str(evidence.get("spoken_forms") or {}):
        violations.append(
            {
                "rule": "D4",
                "match": raw_digits.group(0),
                "reason": "Raw phone digits in script without spoken_forms for TTS",
            }
        )

    ok = len(violations) == 0
    return {
        "pass_type": "DETERMINISTIC_STRUCTURE_PASS",
        "status": "PASS" if ok else "FAIL",
        "evaluator": "ivr_deterministic_gates_v1",
        "turns_parsed": len(turns),
        "violations": violations,
    }


def deterministic_email(body: str, *, lane: str = "w3_canada", region: str = "canada") -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from outbound_email_linter_v1 import lint_email  # noqa: WPS433

    result = lint_email(body, lane=lane, region=region)
    ok = result.get("ok") is True or str(result.get("status") or "").upper() == "PASS"
    return {
        "pass_type": "DETERMINISTIC_STRUCTURE_PASS",
        "status": "PASS" if ok else "FAIL",
        "evaluator": "outbound_email_linter_v1",
        "linter": result,
    }


def deterministic_website_copy(text: str) -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    low = text.lower()
    words = len(re.findall(r"\b[\w']+\b", text))

    if words > 120 and not re.search(r"\b(illustrative|sample)\b", low):
        violations.append(
            {
                "rule": "copy_density",
                "reason": "Too much text before the offer",
                "got_words": words,
            }
        )

    cta_hits = len(re.findall(r"\b(book|schedule|start|get started|contact us|buy now)\b", low))
    if cta_hits == 0:
        violations.append({"rule": "cta_logic", "reason": "Unclear primary CTA"})
    if cta_hits >= 3:
        violations.append({"rule": "cta_logic", "reason": "Multiple competing CTAs"})

    prices = re.findall(r"\$\d[\d,]*(?:\.\d{2})?", text)
    if len(set(prices)) > 1:
        violations.append({"rule": "pricing_truth", "reason": "Conflicting prices", "prices": prices})

    for jargon in ("receipt-native", "brain-os", "supabase edge", "durable object", "orchestration mesh"):
        if jargon in low:
            violations.append(
                {
                    "rule": "buyer_language",
                    "match": jargon,
                    "reason": "Architecture jargon presented to SMB buyers",
                }
            )

    if re.search(r"\b(live now|available today)\b", low) and re.search(r"\b(planned|roadmap|coming soon)\b", low):
        violations.append({"rule": "feature_truth", "reason": "Conflicting live vs planned feature claims"})

    if re.search(r"\b\d{1,3}%\s+(faster|more|growth)\b", low) and "illustrative" not in low:
        violations.append({"rule": "claims", "reason": "Unsupported proof claim without illustrative label"})

    ok = len(violations) == 0
    return {
        "pass_type": "DETERMINISTIC_STRUCTURE_PASS",
        "status": "PASS" if ok else "FAIL",
        "evaluator": "website_copy_deterministic_gates_v1",
        "violations": violations,
    }


def deterministic_commercial_film(text: str, *, artifact_class: str = "A_commercial_vo") -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    low = text.lower()

    if artifact_class == "A_commercial_vo":
        if re.search(r"\*\*(Receptionist|Caller):\*\*", text):
            violations.append(
                {
                    "rule": "D1",
                    "reason": "Commercial narration pasted into product demo dialogue format",
                }
            )
    if artifact_class == "B_product_demo_dialogue" and re.search(r"\b(narrator|voiceover)\b", low):
        violations.append(
            {
                "rule": "D1",
                "reason": "Product demo dialogue mixed with commercial VO narrator cues",
            }
        )

    if not re.search(r"\b(close|goodbye|cta|book|proof)\b", low):
        violations.append({"rule": "D5", "reason": "Script with no complete interaction outcome"})

    ok = len(violations) == 0
    return {
        "pass_type": "DETERMINISTIC_STRUCTURE_PASS",
        "status": "PASS" if ok else "FAIL",
        "evaluator": "commercial_film_deterministic_gates_v1",
        "violations": violations,
    }


def semantic_critic(
    text: str,
    *,
    artifact_type: str,
    deterministic: dict[str, Any],
) -> dict[str, Any]:
    """Rule-based semantic critic — not an LLM. Cites lines and rules."""
    deductions: list[dict[str, Any]] = []
    evaluator = "rule_based_semantic_critic_v1"

    for v in deterministic.get("violations") or deterministic.get("linter", {}).get("failures") or []:
        deductions.append(
            {
                "rule": v.get("rule") or v.get("id"),
                "reason": v.get("reason") or v.get("hint"),
                "match": v.get("match"),
                "dimension": "truthfulness",
                "points": 5,
            }
        )

    dims = {
        "naturalness": 20,
        "tone": 15,
        "brand_separation": 15,
        "truthfulness": 15,
        "promise_discipline": 15,
        "grammar": 10,
        "summary_alignment": 10,
    }
    scores: list[dict[str, Any]] = []
    total_lost = sum(d.get("points", 0) for d in deductions)
    for name, max_score in dims.items():
        lost = sum(d.get("points", 0) for d in deductions if d.get("dimension") == name)
        if name == "truthfulness":
            lost = min(max_score, total_lost)
        scores.append(
            _dim(
                name,
                status="EVALUATED",
                score=max(0, max_score - lost) if deductions else max_score,
                evaluator=evaluator,
            )
        )

    status = "PASS" if not deductions else "FAIL"
    return {
        "pass_type": "SEMANTIC_QUALITY_PASS",
        "status": status,
        "evaluator": evaluator,
        "provider": None,
        "model": None,
        "role": "semantic_critic",
        "prompt_version": "content-quality-spine-v1",
        "input_hash": _sha16(text),
        "structured_output": {"deductions": deductions, "dimensions": scores},
        "token_or_cost_estimate": 0,
        "timestamp": _now(),
    }


def domain_brand_advisor(text: str, *, artifact_type: str, domain_pack: str = "general_SMB") -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    low = text.lower()

    if artifact_type in ("ivr_receptionist", "product_demo_dialogue"):
        if re.search(r"\bsourcea\b|\bsourceb\b|\bnoetfield\b", low):
            issues.append({"rule": "D2", "reason": "Platform brand on customer line"})

    if domain_pack == "automotive" and artifact_type == "ivr_receptionist":
        if "brake" in low and "drive safe" in low:
            issues.append({"rule": "R6", "reason": "Automotive safety: dismissive close after brake symptom"})

    if domain_pack == "medical" and re.search(r"\b(diagnos|prescri)\w+", low):
        issues.append({"rule": "R14", "reason": "Regulated medical language without approved block"})

    ok = len(issues) == 0
    return {
        "pass_type": "DOMAIN_POLICY_PASS",
        "status": "PASS" if ok else "FAIL",
        "evaluator": "domain_brand_advisor_v1",
        "domain_pack": domain_pack,
        "issues": issues,
    }


def truth_evidence_verify(text: str, *, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    evidence = evidence or {}
    issues: list[dict[str, Any]] = []
    low = text.lower()

    action_claims = (
        (r"\bdispatched\b", "dispatch_receipt"),
        (r"\bconfirmed your appointment\b", "appointment_receipt"),
        (r"\bupdated your reservation\b", "update_receipt"),
        (r"\bsent (?:the )?email\b", "send_receipt"),
    )
    for pattern, key in action_claims:
        if re.search(pattern, low) and not evidence.get(key):
            issues.append(
                {
                    "rule": "R1",
                    "pattern": pattern,
                    "reason": f"Action claim without evidence key {key}",
                }
            )

    ok = len(issues) == 0
    return {
        "pass_type": "TRUTH_EVIDENCE_PASS",
        "status": "PASS" if ok else "FAIL",
        "evaluator": "truth_evidence_verifier_v1",
        "evidence_keys_required": [k for _, k in action_claims if re.search(_, low)],
        "issues": issues,
    }


def final_judge(
    *,
    deterministic: dict[str, Any],
    semantic: dict[str, Any],
    advisor: dict[str, Any],
    truth: dict[str, Any],
) -> dict[str, Any]:
    stages = [deterministic, semantic, advisor, truth]
    failed = [s for s in stages if s.get("status") != "PASS"]
    verdict = "APPROVED" if not failed else "QUARANTINED"
    return {
        "pass_type": "SEMANTIC_QUALITY_PASS",
        "status": "PASS" if verdict == "APPROVED" else "FAIL",
        "evaluator": "final_machine_judge_v1",
        "verdict": verdict,
        "failed_stages": [s.get("pass_type") for s in failed],
        "founder_escalation_required": verdict == "QUARANTINED",
        "timestamp": _now(),
    }


def run_spine(
    *,
    artifact_type: str,
    draft: str,
    domain_pack: str = "general_SMB",
    evidence: dict[str, Any] | None = None,
    lane: str = "w3_canada",
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    evidence = evidence or {}
    metadata = metadata or {}
    run_id = f"CQS-{uuid.uuid4().hex[:12]}"
    classification = classify_artifact(artifact_type)
    revision_history: list[dict[str, Any]] = []

    key = classification["artifact_type"]
    if key in ("ivr_receptionist", "product_demo_dialogue"):
        det = deterministic_ivr(draft, evidence=evidence)
    elif key in ("email", "sales_outreach"):
        det = deterministic_email(draft, lane=lane)
    elif key in ("website_copy", "landing_page"):
        det = deterministic_website_copy(draft)
    elif key == "commercial_film":
        det = deterministic_commercial_film(draft, artifact_class=classification["artifact_class"])
    else:
        det = {
            "pass_type": "DETERMINISTIC_STRUCTURE_PASS",
            "status": "FAIL",
            "evaluator": "unknown_adapter",
            "violations": [{"reason": f"Unsupported artifact_type: {key}"}],
        }

    sem = semantic_critic(draft, artifact_type=key, deterministic=det)
    adv = domain_brand_advisor(draft, artifact_type=key, domain_pack=domain_pack)
    tru = truth_evidence_verify(draft, evidence=evidence)
    judge = final_judge(deterministic=det, semantic=sem, advisor=adv, truth=tru)

    if judge["verdict"] == "QUARANTINED":
        revision_history.append(
            {
                "attempt": 1,
                "action": "targeted_revision_recommended",
                "failed_rules": [
                    *(v.get("rule") for v in det.get("violations") or []),
                    *(i.get("rule") for i in adv.get("issues") or []),
                    *(i.get("rule") for i in tru.get("issues") or []),
                ],
            }
        )

    approved = judge["verdict"] == "APPROVED"
    return {
        "schema": "content-quality-spine-run-v1",
        "run_id": run_id,
        "at": _now(),
        "classification": classification,
        "domain_pack": domain_pack,
        "metadata": metadata,
        "draft_artifact": {"text": draft, "input_hash": _sha16(draft)},
        "deterministic_receipt": det,
        "semantic_critic_receipt": sem,
        "domain_brand_advisor_receipt": adv,
        "truth_evidence_receipt": tru,
        "final_judge_receipt": judge,
        "revision_history": revision_history,
        "final_artifact": {
            "status": "APPROVED" if approved else "QUARANTINED",
            "text": draft if approved else None,
            "quarantine_reason": judge.get("failed_stages") if not approved else None,
        },
        "expensive_generation_allowed": approved,
        "model_and_cost": {
            "routing": "rule_based_only",
            "llm_invoked": False,
            "token_or_cost_estimate": 0,
            "escalation_contract": "data/cursor-cost-intelligence-routing-v1.json",
        },
    }
