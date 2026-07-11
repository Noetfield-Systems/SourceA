"""Integrity score — deductive 100 minus cited violations (authority for hard gates)."""
from __future__ import annotations

from typing import Any


def _collect_deductions(
    det: dict[str, Any],
    sem: dict[str, Any],
    dom: dict[str, Any],
    truth: dict[str, Any],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for v in det.get("violations") or []:
        rows.append(
            {
                "line": v.get("line"),
                "speaker": v.get("speaker"),
                "exact_text": v.get("text") or v.get("match"),
                "rule": v.get("rule"),
                "reason": v.get("reason"),
                "points": 5,
                "source": "deterministic_verifier",
            }
        )
    for d in (sem.get("structured_output") or {}).get("deductions") or []:
        rows.append(
            {
                "line": d.get("line"),
                "speaker": d.get("speaker"),
                "exact_text": d.get("text"),
                "rule": d.get("rule"),
                "reason": d.get("reason"),
                "points": d.get("points", 3),
                "source": "rule_based_semantic_preflight",
            }
        )
    for issue in dom.get("issues") or []:
        rows.append(
            {
                "line": None,
                "speaker": None,
                "exact_text": None,
                "rule": issue.get("rule"),
                "reason": issue.get("reason"),
                "points": 8,
                "source": "domain_policy_preflight",
            }
        )
    for issue in truth.get("issues") or []:
        rows.append(
            {
                "line": None,
                "speaker": None,
                "exact_text": None,
                "rule": issue.get("rule"),
                "reason": issue.get("reason"),
                "points": 10,
                "source": "truth_evidence_verifier",
            }
        )
    return rows


def build_integrity_receipt(
    *,
    det: dict[str, Any],
    sem: dict[str, Any],
    dom: dict[str, Any],
    truth: dict[str, Any],
    judge: dict[str, Any],
) -> dict[str, Any]:
    deductions = _collect_deductions(det, sem, dom, truth)
    lost = sum(int(d.get("points") or 0) for d in deductions)
    score = max(0, 100 - lost)
    hard_fail = judge.get("verdict") == "QUARANTINED" or any(
        s.get("status") == "FAIL" for s in (det, sem, dom, truth)
    )
    return {
        "schema": "integrity-receipt-v1",
        "evaluator": "integrity_machine_v1",
        "scoring_model": "deductive",
        "integrity_score_start": 100,
        "integrity_score": score,
        "deductions": deductions,
        "hard_gate_status": "FAIL" if hard_fail else "PASS",
        "hard_gate_verdict": judge.get("verdict", "QUARANTINED"),
        "synthesis_ready": judge.get("synthesis_ready", False) and not hard_fail,
        "authority": "integrity_machine_remains_authority_for_hard_failures",
    }
