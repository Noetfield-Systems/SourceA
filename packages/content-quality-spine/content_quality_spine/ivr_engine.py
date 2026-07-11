"""IVR evaluation engine — canonical R1-R16 with cited deductions."""
from __future__ import annotations

import json
import re
from importlib import resources
from typing import Any

GRAMMAR_FAIL_PATTERNS = [
    (r"\bA intake\b", "R16"),
    (r"good day\.\s*goodbye", "R16"),
    (r"not booked yet,\s*just a request", "R16"),
    (r"can't confirm that on this line", "R7"),
    (r"stay warm as best you can", "R16"),
]

UNSUPPORTED_PROMISE_PATTERNS = [
    (r"\barrive (?:at|by) \d", "R8", "promise.arrival_time"),
    (r"call you (?:back )?(?:within|in) \d+ (?:minute|hour)", "R8", "promise.callback_time"),
    (r"maintenance will call within", "R8", "promise.sla_unverified"),
    (r"within thirty minutes", "R8", "promise.sla_unverified"),
    (r"\bdispatched emergency\b", "R1", "claim.dispatch_without_receipt"),
    (r"\bguaranteed\b", "R8", "promise.guaranteed"),
]

POLICY_LEAKAGE = [
    r"cannot do that on this line",
    r"not allowed to provide",
    r"only a request and not a booking",
    r"cannot comment on that yet",
    r"can't confirm that on this line",
    r"cannot give pricing on this line",
]

DIMENSIONS = {
    "naturalness": 20,
    "conversation_efficiency": 15,
    "intent_capture": 15,
    "business_usefulness": 15,
    "truthfulness": 15,
    "summary_accuracy": 10,
    "structure_arc": 10,
}


def _load_registry() -> dict[str, Any]:
    raw = resources.files("content_quality_spine.rules").joinpath(
        "conversation-script-logic-registry-v1.json"
    ).read_text(encoding="utf-8")
    return json.loads(raw)


def parse_transcript(text: str) -> list[dict[str, Any]]:
    turns: list[dict[str, Any]] = []
    line_no = 0
    for raw in text.splitlines():
        line_no += 1
        s = raw.strip()
        if not s or s.startswith("#"):
            continue
        m = re.match(r"^\*\*(Receptionist|Caller):\*\*\s*(.+)$", s, re.I)
        if m:
            turns.append({"line": line_no, "speaker": m.group(1).title(), "text": m.group(2).strip()})
            continue
        m2 = re.match(r"^(Receptionist|Caller):\s*(.+)$", s, re.I)
        if m2:
            turns.append({"line": line_no, "speaker": m2.group(1).title(), "text": m2.group(2).strip()})
    return turns


def cite(turns: list[dict[str, Any]], speaker: str | None, pattern: str | re.Pattern[str]) -> dict[str, Any] | None:
    rx = re.compile(pattern, re.I) if isinstance(pattern, str) else pattern
    for t in turns:
        if speaker and t["speaker"] != speaker:
            continue
        if rx.search(t["text"]):
            return {"line": t["line"], "speaker": t["speaker"], "text": t["text"]}
    return None


def deterministic_ivr(
    text: str,
    *,
    adapter: dict[str, Any],
    rules: dict[str, Any],
) -> dict[str, Any]:
    registry = rules or _load_registry()
    turns = parse_transcript(text)
    all_text = " ".join(t["text"] for t in turns)
    recv_text = " ".join(t["text"] for t in turns if t["speaker"] == "Receptionist")
    low = all_text.lower()
    violations: list[dict[str, Any]] = []
    summary = adapter.get("summary") or {}
    profile = adapter.get("domain_profile_config") or {}

    for term in registry.get("system_language", []):
        hit = cite(turns, None, re.escape(term))
        if hit:
            violations.append({**hit, "rule": "R3", "reason": f"Internal system language: {term}"})

    for pattern, rule, vid in UNSUPPORTED_PROMISE_PATTERNS:
        hit = cite(turns, "Receptionist", pattern)
        if hit:
            violations.append({**hit, "rule": rule, "id": vid, "reason": "Unsupported promise or action claim"})

    for pattern, rule in GRAMMAR_FAIL_PATTERNS:
        hit = cite(turns, None, pattern)
        if hit:
            violations.append({**hit, "rule": rule, "reason": "Grammar/naturalness fail pattern"})

    if re.search(r"drive safe", low) and re.search(r"grind|brake|unsafe", low):
        hit = cite(turns, "Receptionist", r"drive safe")
        violations.append({**(hit or {}), "rule": "R6", "reason": "Dismissive safety close after brake hazard"})

    if summary.get("terminal_outcome") and summary["terminal_outcome"] not in registry.get("terminal_outcomes", []):
        violations.append({"rule": "R2", "reason": "Invalid terminal_outcome in summary"})

    for check in profile.get("domain_checks") or []:
        field = check.get("field", "field")
        rx = check.get("pattern") or check.get("re", "")
        if rx and not re.search(rx, all_text, re.I):
            violations.append({"rule": "R4", "reason": f"Missing domain field: {field}"})

    if profile.get("canonical_values"):
        recv_only = recv_text
        for row in profile["canonical_values"]:
            bad = row.get("must_not_remain", "")
            if bad and re.search(bad, recv_only, re.I):
                hit = cite(turns, "Receptionist", bad)
                violations.append({**(hit or {}), "rule": "R10", "reason": f"Superseded value; expected {row.get('value')}"})

    if re.search(r"cannot provide medical advice", low) and re.search(
        r"\b(take|try|use|recommend)\b.+\b(aspirin|medicine|pill|dose|treatment)\b", low
    ):
        hit = cite(turns, "Receptionist", r"\b(take|try|use|recommend)\b")
        violations.append({**(hit or {}), "rule": "R6", "reason": "Medical disclaimer followed by improvised advice"})

    if summary.get("terminal_outcome") == "appointment_requested" and re.search(
        r"appointment is confirmed|is booked", recv_text, re.I
    ):
        hit = cite(turns, "Receptionist", r"appointment is confirmed|is booked")
        violations.append({**(hit or {}), "rule": "R15", "reason": "Transcript upgrades summary state"})

    ok = not violations
    return {
        "pass_type": "DETERMINISTIC_STRUCTURE_PASS",
        "status": "PASS" if ok else "FAIL",
        "evaluator": registry.get("evaluator_labels", {}).get("deterministic", "deterministic_verifier"),
        "turns_parsed": len(turns),
        "violations": violations,
        "turns": turns,
        "all_text": all_text,
        "recv_text": recv_text,
    }


def _deduct(deductions: list[dict[str, Any]], row: dict[str, Any]) -> None:
    deductions.append(row)


def semantic_preflight(
    det: dict[str, Any],
    *,
    adapter: dict[str, Any],
    rules: dict[str, Any],
) -> dict[str, Any]:
    registry = rules or _load_registry()
    evaluator = registry.get("evaluator_labels", {}).get("semantic", "rule_based_semantic_preflight")
    turns = det.get("turns") or []
    recv_text = det.get("recv_text") or ""
    all_text = det.get("all_text") or ""
    summary = adapter.get("summary") or {}
    profile = adapter.get("domain_profile_config") or {}
    deductions: list[dict[str, Any]] = []

    for v in det.get("violations") or []:
        _deduct(
            deductions,
            {
                "line": v.get("line"),
                "speaker": v.get("speaker"),
                "text": v.get("text"),
                "rule": v.get("rule"),
                "dimension": "truthfulness",
                "points": 5,
                "reason": v.get("reason"),
            },
        )

    for t in turns:
        if t["speaker"] != "Receptionist":
            continue
        if len(t["text"]) > 220:
            _deduct(
                deductions,
                {
                    "line": t["line"],
                    "speaker": t["speaker"],
                    "text": t["text"],
                    "rule": "R12",
                    "dimension": "naturalness",
                    "points": 2,
                    "reason": "Receptionist line exceeds brevity band",
                },
            )

    for leak in POLICY_LEAKAGE:
        hit = cite(turns, "Receptionist", leak)
        if hit:
            _deduct(
                deductions,
                {
                    **hit,
                    "rule": "R7",
                    "dimension": "structure_arc",
                    "points": 3,
                    "reason": "Policy leakage instead of useful next action",
                },
            )

    if re.search(r"cannot provide medical advice", all_text, re.I) and re.search(
        r"\b(take|try|use|recommend)\b.+\b(aspirin|medicine|pill|dose|treatment)\b", all_text, re.I
    ):
        hit = cite(turns, "Receptionist", r"\b(take|try|use|recommend)\b")
        _deduct(
            deductions,
            {
                **(hit or {}),
                "rule": "R6",
                "dimension": "truthfulness",
                "points": 6,
                "reason": "Medical disclaimer followed by improvised advice",
            },
        )

    if summary.get("terminal_outcome") == "appointment_requested" and re.search(
        r"appointment is confirmed|is booked", recv_text, re.I
    ):
        hit = cite(turns, "Receptionist", r"appointment is confirmed|is booked")
        _deduct(
            deductions,
            {
                **(hit or {}),
                "rule": "R15",
                "dimension": "summary_accuracy",
                "points": 4,
                "reason": "Transcript upgrades summary state",
            },
        )

    scores: dict[str, Any] = {}
    for dim, max_score in DIMENSIONS.items():
        lost = sum(d["points"] for d in deductions if d.get("dimension") == dim)
        scores[dim] = {
            "dimension": dim,
            "status": "EVALUATED",
            "score": max(0, max_score - lost),
            "max": max_score,
            "evaluator": evaluator,
        }

    total = sum(s["score"] for s in scores.values())
    evaluated = all(s["status"] == "EVALUATED" for s in scores.values())
    approved = evaluated and total >= 85 and all(s["score"] >= s["max"] * 0.6 for s in scores.values())

    return {
        "pass_type": "SEMANTIC_QUALITY_PASS",
        "status": "PASS" if approved and not deductions else "FAIL",
        "evaluator": evaluator,
        "provider": None,
        "model": None,
        "role": "rule_based_semantic_preflight",
        "structured_output": {"deductions": deductions, "dimensions": list(scores.values()), "total_score": total},
        "semantic_approved": approved,
        "total_score": total,
        "total_score_computable": evaluated,
    }


def domain_policy_preflight(text: str, *, adapter: dict[str, Any], rules: dict[str, Any]) -> dict[str, Any]:
    registry = rules or _load_registry()
    evaluator = registry.get("evaluator_labels", {}).get("domain", "domain_policy_preflight")
    issues: list[dict[str, Any]] = []
    low = text.lower()
    pack = adapter.get("domain_profile") or "general_SMB"
    if re.search(r"\bsourcea\b|\bsourceb\b", low):
        issues.append({"rule": "D2", "reason": "Platform brand on customer line"})
    if pack == "automotive" and "brake" in low and "drive safe" in low:
        issues.append({"rule": "R6", "reason": "Automotive safety: dismissive close after brake symptom"})
    ok = not issues
    return {
        "pass_type": "DOMAIN_POLICY_PASS",
        "status": "PASS" if ok else "FAIL",
        "evaluator": evaluator,
        "domain_pack": pack,
        "issues": issues,
    }


def truth_evidence_preflight(text: str, *, adapter: dict[str, Any]) -> dict[str, Any]:
    evidence = adapter.get("tool_evidence") or {}
    issues: list[dict[str, Any]] = []
    low = text.lower()
    claims = (
        (r"\bdispatched\b", "dispatch_receipt"),
        (r"\bconfirmed your appointment\b", "appointment_receipt"),
        (r"\bupdated your reservation\b", "update_receipt"),
    )
    for pattern, key in claims:
        if re.search(pattern, low) and not evidence.get(key) and not adapter.get("summary", {}).get("tool_action_receipt"):
            issues.append({"rule": "R1", "reason": f"Action claim without evidence key {key}"})
    ok = not issues
    return {
        "pass_type": "TRUTH_EVIDENCE_PASS",
        "status": "PASS" if ok else "FAIL",
        "evaluator": "truth_evidence_verifier",
        "issues": issues,
    }


def final_rule_judge(*, det: dict[str, Any], sem: dict[str, Any], dom: dict[str, Any], truth: dict[str, Any]) -> dict[str, Any]:
    stages = [det, sem, dom, truth]
    failed = [s for s in stages if s.get("status") != "PASS"]
    verdict = "APPROVED" if not failed else "QUARANTINED"
    return {
        "pass_type": "SEMANTIC_QUALITY_PASS",
        "status": "PASS" if verdict == "APPROVED" else "FAIL",
        "evaluator": "final_rule_judge",
        "verdict": verdict,
        "failed_stages": [s.get("pass_type") for s in failed],
        "synthesis_ready": verdict == "APPROVED" and sem.get("semantic_approved") is True,
    }
