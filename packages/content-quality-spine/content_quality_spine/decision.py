"""Combined artifact decision — integrity authority + optional excellence ranking."""
from __future__ import annotations

from typing import Any


def artifact_decision(
    *,
    integrity: dict[str, Any],
    excellence: dict[str, Any],
    llm_mode: str,
) -> dict[str, Any]:
    hard_fail = integrity.get("hard_gate_status") == "FAIL"
    if hard_fail:
        return {
            "artifact_decision": "QUARANTINED",
            "quality_recommendation": "Fix integrity violations before polish or ranking.",
            "decision_authority": "integrity_machine",
            "excellence_influenced_decision": False,
        }

    ex_status = excellence.get("status")
    ex_score = excellence.get("excellence_score")
    mode = (llm_mode or "shadow").lower()

    if ex_status in ("NOT_EVALUATED", "SKIPPED") or ex_score is None:
        decision = "APPROVED_WITH_EXCELLENCE_NOT_EVALUATED"
        rec = excellence.get("reason") or "Excellence reviewer did not run."
    elif ex_score >= 95:
        decision = "PUBLIC_NOMINEE"
        rec = excellence.get("quality_recommendation") or "Exceptional excellence — candidate for public showcase."
    elif ex_score >= 70:
        decision = "APPROVED_AND_RANKED"
        rec = excellence.get("quality_recommendation") or "Strong excellence — rank among approved artifacts."
    else:
        decision = "APPROVED_WITH_POLISH_RECOMMENDED"
        rec = excellence.get("quality_recommendation") or "Integrity pass with polish opportunities."

    if mode == "shadow":
        if integrity.get("synthesis_ready"):
            pipeline_decision = "APPROVED"
        else:
            pipeline_decision = "QUARANTINED"
        return {
            "artifact_decision": pipeline_decision,
            "quality_recommendation": rec,
            "excellence_rank_decision": decision,
            "decision_authority": "integrity_machine",
            "excellence_influenced_decision": False,
            "shadow_excellence_decision": decision,
        }

    return {
        "artifact_decision": decision,
        "quality_recommendation": rec,
        "decision_authority": "integrity_machine_with_advisory_excellence" if mode == "advisory" else "integrity_machine",
        "excellence_influenced_decision": mode == "advisory",
    }


def build_combined_receipt(
    *,
    integrity: dict[str, Any],
    rule_semantic: dict[str, Any],
    excellence: dict[str, Any],
    decision: dict[str, Any],
    llm_mode: str,
) -> dict[str, Any]:
    ex_score = excellence.get("excellence_score")
    return {
        "schema": "combined-quality-receipt-v1",
        "integrity_score": integrity.get("integrity_score"),
        "excellence_score": ex_score,
        "llm_excellence_bonus": round(ex_score / 10) if isinstance(ex_score, int) else None,
        "hard_gate_status": integrity.get("hard_gate_status"),
        "artifact_decision": decision.get("artifact_decision"),
        "quality_recommendation": decision.get("quality_recommendation"),
        "synthesis_ready": integrity.get("synthesis_ready"),
        "llm_mode": llm_mode,
        "excellence_status": excellence.get("status"),
        "shadow_excellence_decision": decision.get("shadow_excellence_decision"),
        "integrity_receipt_ref": "integrity_receipt.json",
        "rule_semantic_receipt_ref": "rule_semantic_receipt.json",
        "llm_excellence_receipt_ref": "llm_excellence_receipt.json",
        "rule_semantic_total_score": rule_semantic.get("total_score"),
    }
