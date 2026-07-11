"""Portable evaluate interface — JSON in, receipts out."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from content_quality_spine.decision import artifact_decision, build_combined_receipt
from content_quality_spine.integrity import build_integrity_receipt
from content_quality_spine.ivr_engine import (
    deterministic_ivr,
    domain_policy_preflight,
    final_rule_judge,
    semantic_preflight,
    truth_evidence_preflight,
)
from content_quality_spine.llm_excellence import evaluate_excellence
from content_quality_spine.version import SPINE_VERSION, rules_hash


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def _read_json(path: Path | None) -> dict[str, Any]:
    if path is None or not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def evaluate(
    *,
    artifact: dict[str, Any],
    adapter: dict[str, Any] | None = None,
    rules: dict[str, Any] | None = None,
    llm_mode: str = "shadow",
) -> dict[str, Any]:
    adapter = adapter or {}
    rules = rules or {}
    content = str(artifact.get("artifact_content") or artifact.get("body") or "")
    adapter_type = str(
        artifact.get("adapter_type")
        or artifact.get("artifact_type")
        or adapter.get("adapter_type")
        or "ivr_receptionist"
    )
    run_id = f"CQS-{uuid.uuid4().hex[:12]}"
    input_hash = _sha16(content)

    classification = {
        "artifact_class": artifact.get("artifact_class", "E_ivr_receptionist"),
        "adapter_type": adapter_type,
        "evaluation_mode": artifact.get("evaluation_mode", "rule_based"),
        "model_budget": artifact.get("model_budget", "low"),
    }

    merged_adapter = {
        **adapter,
        "domain_profile": artifact.get("domain_profile") or adapter.get("domain_profile"),
        "summary": adapter.get("summary") or artifact.get("source_context", {}).get("summary"),
        "tool_evidence": artifact.get("tool_evidence") or adapter.get("tool_evidence") or {},
        "domain_profile_config": adapter.get("domain_profile_config") or {},
    }

    if adapter_type in ("ivr_receptionist", "product_demo_dialogue", "E_ivr_receptionist"):
        det = deterministic_ivr(content, adapter=merged_adapter, rules=rules)
        sem = semantic_preflight(det, adapter=merged_adapter, rules=rules)
        dom = domain_policy_preflight(content, adapter=merged_adapter, rules=rules)
        truth = truth_evidence_preflight(content, adapter=merged_adapter)
        judge = final_rule_judge(det=det, sem=sem, dom=dom, truth=truth)
    elif adapter_type in ("email", "commercial_film", "landing_page", "website_copy", "sales_outreach"):
        det, sem, dom, truth, judge = generic_text_pipeline(content, adapter=merged_adapter, artifact_type=adapter_type)
    else:
        det = {"status": "FAIL", "evaluator": "deterministic_verifier", "violations": [{"reason": f"unsupported adapter {adapter_type}"}]}
        sem = dom = truth = judge = {"status": "FAIL", "evaluator": "n/a"}

    integrity = build_integrity_receipt(det=det, sem=sem, dom=dom, truth=truth, judge=judge)
    excellence = evaluate_excellence(
        artifact={"body": content, "artifact_type": adapter_type, **artifact},
        adapter=merged_adapter,
        llm_mode=llm_mode,
    )
    decision = artifact_decision(integrity=integrity, excellence=excellence, llm_mode=llm_mode)
    combined = build_combined_receipt(
        integrity=integrity,
        rule_semantic=sem,
        excellence=excellence,
        decision=decision,
        llm_mode=llm_mode,
    )

    revision_history: list[dict[str, Any]] = []
    final_status = judge.get("verdict", "QUARANTINED")
    if final_status != "APPROVED":
        revision_history.append(
            {
                "attempt": 1,
                "action": "targeted_revision",
                "failed_rules": list(
                    {
                        *(v.get("rule") for v in det.get("violations") or []),
                        *(d.get("rule") for d in (sem.get("structured_output") or {}).get("deductions") or []),
                        *(i.get("rule") for i in dom.get("issues") or []),
                        *(i.get("rule") for i in truth.get("issues") or []),
                    }
                ),
            }
        )

    out = {
        "schema": "content-quality-spine-evaluate-v1.1",
        "run_id": run_id,
        "at": _now(),
        "sourcea_spine_version": SPINE_VERSION,
        "sourcea_rules_hash": rules_hash(),
        "input_hash": input_hash,
        "llm_mode": llm_mode,
        "classification_receipt": classification,
        "deterministic_receipt": det,
        "semantic_preflight_receipt": sem,
        "domain_advisor_receipt": dom,
        "truth_evidence_receipt": truth,
        "final_judge_receipt": judge,
        "integrity_receipt": integrity,
        "rule_semantic_receipt": sem,
        "llm_excellence_receipt": excellence,
        "combined_quality_receipt": combined,
        "revision_history": revision_history,
        "final_status": final_status,
        "synthesis_ready": integrity.get("synthesis_ready", False),
        "integrity_score": integrity.get("integrity_score"),
        "excellence_score": excellence.get("excellence_score"),
        "llm_excellence_bonus": excellence.get("llm_excellence_bonus"),
        "artifact_decision": combined.get("artifact_decision"),
        "llm_invoked": excellence.get("status") == "EVALUATED",
    }
    out["output_receipt_hash"] = _sha16(json.dumps(out, sort_keys=True))
    return out


def evaluate_files(
    *,
    artifact_path: Path,
    adapter_path: Path | None,
    rules_path: Path | None,
    output_dir: Path,
    llm_mode: str = "shadow",
) -> dict[str, Any]:
    artifact = _read_json(artifact_path)
    adapter = _read_json(adapter_path) if adapter_path else {}
    rules = _read_json(rules_path) if rules_path else {}
    result = evaluate(artifact=artifact, adapter=adapter, rules=rules, llm_mode=llm_mode)
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "canonical_evaluation_receipt.json").write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    receipt_map = {
        "integrity_receipt.json": result.get("integrity_receipt"),
        "rule_semantic_receipt.json": result.get("rule_semantic_receipt"),
        "llm_excellence_receipt.json": result.get("llm_excellence_receipt"),
        "combined_quality_receipt.json": result.get("combined_quality_receipt"),
        "deterministic_receipt.json": result.get("deterministic_receipt"),
        "semantic_preflight_receipt.json": result.get("semantic_preflight_receipt"),
        "domain_advisor_receipt.json": result.get("domain_advisor_receipt"),
        "truth_evidence_receipt.json": result.get("truth_evidence_receipt"),
        "final_judge_receipt.json": result.get("final_judge_receipt"),
    }
    for fname, payload in receipt_map.items():
        if payload is not None:
            (output_dir / fname).write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (output_dir / "revision_history.json").write_text(
        json.dumps(result.get("revision_history") or [], indent=2) + "\n",
        encoding="utf-8",
    )
    return result
