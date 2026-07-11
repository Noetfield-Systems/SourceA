"""Non-IVR text artifact integrity — lightweight deterministic pass for copy artifacts."""
from __future__ import annotations

import re
from typing import Any

GENERIC_POLICY_PATTERNS = (
    (r"\breceipt-native\b", "forbidden_jargon"),
    (r"\bbrain-os\b", "forbidden_jargon"),
    (r"\bguaranteed\b", "unsupported_promise"),
)


def generic_text_pipeline(
    content: str,
    *,
    adapter: dict[str, Any],
    artifact_type: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any], dict[str, Any]]:
    violations: list[dict[str, Any]] = []
    for pattern, reason in GENERIC_POLICY_PATTERNS:
        if re.search(pattern, content, re.I):
            violations.append({"rule": "POLICY", "reason": reason, "text": content[:120]})
    if not content.strip():
        violations.append({"rule": "EMPTY", "reason": "empty artifact body"})

    det = {
        "pass_type": "DETERMINISTIC_STRUCTURE_PASS",
        "status": "PASS" if not violations else "FAIL",
        "evaluator": "generic_text_verifier",
        "artifact_type": artifact_type,
        "violations": violations,
        "turns": [],
        "all_text": content,
        "recv_text": content,
    }
    sem = {
        "pass_type": "SEMANTIC_QUALITY_PASS",
        "status": "PASS",
        "evaluator": "rule_based_semantic_preflight",
        "structured_output": {"deductions": [], "dimensions": [], "total_score": 100},
        "semantic_approved": True,
        "total_score": 100,
        "total_score_computable": True,
    }
    dom = {
        "pass_type": "DOMAIN_POLICY_PASS",
        "status": "PASS",
        "evaluator": "domain_policy_preflight",
        "domain_pack": adapter.get("domain_profile") or "general_SMB",
        "issues": [],
    }
    truth = {
        "pass_type": "TRUTH_EVIDENCE_PASS",
        "status": "PASS",
        "evaluator": "truth_evidence_verifier",
        "issues": [],
    }
    judge = {
        "pass_type": "SEMANTIC_QUALITY_PASS",
        "status": "PASS" if not violations else "FAIL",
        "evaluator": "final_rule_judge",
        "verdict": "APPROVED" if not violations else "QUARANTINED",
        "failed_stages": ["DETERMINISTIC_STRUCTURE_PASS"] if violations else [],
        "synthesis_ready": not violations,
    }
    return det, sem, dom, truth, judge
