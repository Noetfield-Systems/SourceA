#!/usr/bin/env python3
"""Founder Intent Approval Machine — input → intent → critic → machine verdict.

This machine does not edit product code. It turns founder language into a
verifiable interpretation and approval receipt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SPEC_PATH = ROOT / "data/founder-intent-approval-machine-v1.json"
RECEIPT_PATH = Path.home() / ".sina/founder-intent-approval-machine-v1.json"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def sha16(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def load_spec() -> dict[str, Any]:
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def has_any(text: str, patterns: list[str]) -> bool:
    return any(re.search(p, text, re.I) for p in patterns)


def classify_intent(message: str) -> str:
    low = (message or "").strip().lower()
    if not low:
        return "ambiguous"

    if has_any(low, [r"\bgo ahead\b", r"\bapproved?\b", r"\bship it\b", r"\bproceed\b"]):
        return "approval"
    if has_any(low, [r"^work:", r"\bimplement\b", r"\bbuild\b", r"\bfix\b", r"\bdeploy\b", r"\bvalidate\b"]):
        return "work_order"
    if has_any(low, [r"\bmust never\b", r"\bmandatory\b", r"\brule\b", r"\blaw\b", r"\bforbidden\b", r"\bshould not\b"]):
        return "boundary_law"
    if has_any(low, [r"\bexample\b", r"\bexamples\b", r"\bfarsi\b", r"\bspanish\b", r"\btranslate generally\b"]):
        return "example_generalization"
    if has_any(low, [r"\bweird\b", r"\bconfus", r"\bwrong\b", r"\bbad\b", r"\byou missed\b", r"\byou misunderstood\b"]):
        return "emotional_diagnostic"
    if has_any(low, [r"\bwrite\b.*\bcopy\b", r"\bheadline\b", r"\bhero\b", r"\bpublic copy\b", r"\bcta\b"]):
        return "public_copy"
    if has_any(low, [r"\barchitect", r"\barchitecture\b", r"\bintent\b", r"\bmachine\b", r"\bhighest confidence\b", r"\bhandle everything\b", r"\bstate\b"]):
        return "architecture_intent"
    if len(low.split()) <= 3 and has_any(low, [r"\bbetter\b", r"\bimprove\b", r"\bupgrade\b"]):
        return "ambiguous"
    return "architecture_intent" if "should" in low else "ambiguous"


def compile_meaning(message: str, intent_class: str) -> str:
    low = (message or "").lower()
    if "highest confidence" in low or "handle everything" in low:
        return (
            "Founder wants a system property: Brain should behave with evidence-backed confidence "
            "through retrieval, live tools, guardrails, uncertainty handling, evals, and clean public writing. "
            "The phrase must not become public identity copy."
        )
    if intent_class == "example_generalization":
        return "Founder examples expose a general capability. Implement the capability once and test variants, not only examples."
    if intent_class == "public_copy":
        return "Founder is asking for visitor-facing wording. Preserve plain language and route through public voice checks."
    if intent_class == "boundary_law":
        return "Founder is defining an invariant or safety boundary. Encode as guardrail/rule/eval, not just prose."
    if intent_class == "emotional_diagnostic":
        return "Founder frustration is a bug signal. Extract root cause and add regression coverage."
    if intent_class == "work_order":
        return "Founder is asking for implementation. Convert to scoped tasks with proof and validators."
    if intent_class == "approval":
        return "Founder approved a proposed path. Record approval and proceed only inside the approved scope."
    return "Intent is underspecified. Ask a focused clarification before writing code or public copy."


ROUTES_BY_INTENT = {
    "architecture_intent": ["meaning_compiler", "architecture_mapper", "retrieval", "live_tools", "guardrail", "eval"],
    "public_copy": ["copy_layer", "public_voice_gate", "eval"],
    "example_generalization": ["capability_layer", "llm_capability", "generalized_eval"],
    "boundary_law": ["guardrail", "rule", "validator", "eval"],
    "emotional_diagnostic": ["incident", "critic_loop", "public_voice_eval"],
    "work_order": ["todo", "implementation", "validator", "receipt"],
    "approval": ["approval_receipt", "next_action"],
    "ambiguous": ["ask_founder"],
}


def approved_shape(intent_class: str) -> dict[str, Any]:
    if intent_class == "public_copy":
        return {"copy": True, "code": False, "eval": True, "approval_needed": False}
    if intent_class in {"architecture_intent", "example_generalization", "boundary_law"}:
        return {"copy": False, "code": True, "eval": True, "approval_needed": False}
    if intent_class == "emotional_diagnostic":
        return {"incident": True, "code": "if root cause requires it", "eval": True}
    if intent_class == "work_order":
        return {"implementation": True, "validator": True, "receipt": True}
    if intent_class == "approval":
        return {"approval_receipt": True, "next_action": True}
    return {"clarifying_question": True}


def critic_findings(message: str, intent_class: str, candidate_output: str = "") -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    low_out = (candidate_output or "").lower()
    low_msg = (message or "").lower()

    if not candidate_output:
        findings.append({"id": "no_candidate_output", "severity": "info", "message": "No candidate output supplied; approving interpretation/spec only."})
        return findings

    if intent_class == "architecture_intent" and re.search(r"highest[- ]confidence", low_out):
        findings.append({"id": "literal_copy", "severity": "blocker", "message": "Candidate copied architecture intent into output."})
    if "farsi" in low_out and "spanish" in low_out and ("if" in low_out or "branch" in low_out):
        findings.append({"id": "hardcoded_example", "severity": "blocker", "message": "Candidate appears to branch on examples instead of capability."})
    if any(x in low_out for x in ["docs/", "sourcea-landing", "brain-os", "api key", ":13020", ":13027"]):
        findings.append({"id": "internal_leakage", "severity": "blocker", "message": "Candidate exposes internal/source details."})
    if len(candidate_output.strip()) < 40:
        findings.append({"id": "weak_benefit", "severity": "warn", "message": "Candidate is too short to prove meaning or benefit."})
    if "example" in low_msg and "general" not in low_out and "capability" not in low_out:
        findings.append({"id": "missing_generalization", "severity": "blocker", "message": "Founder gave examples; candidate does not generalize."})
    if not findings:
        findings.append({"id": "critic_pass", "severity": "pass", "message": "No blocker patterns detected."})
    return findings


def machine_checks(route: list[str], findings: list[dict[str, Any]]) -> list[dict[str, Any]]:
    blockers = [f for f in findings if f.get("severity") == "blocker"]
    checks = [
        {"id": "route_present", "ok": bool(route), "detail": ", ".join(route)},
        {"id": "critic_no_blockers", "ok": not blockers, "detail": [b["id"] for b in blockers]},
        {"id": "proof_route_present", "ok": any(x in route for x in ("eval", "validator", "receipt", "approval_receipt", "public_voice_eval", "generalized_eval")), "detail": route},
    ]
    return checks


def verdict_for(intent_class: str, checks: list[dict[str, Any]], candidate_output: str = "") -> str:
    if intent_class == "ambiguous":
        return "ASK_FOUNDER"
    if any(not c.get("ok") for c in checks):
        return "RETURN_TO_AGENT"
    if candidate_output:
        return "APPROVED"
    if intent_class == "approval":
        return "APPROVED"
    return "APPROVED_SPEC"


def run_machine(message: str, *, surface: str = "unknown", candidate_output: str = "", write: bool = True) -> dict[str, Any]:
    spec = load_spec()
    intent_class = classify_intent(message)
    route = ROUTES_BY_INTENT[intent_class]
    findings = critic_findings(message, intent_class, candidate_output)
    checks = machine_checks(route, findings)
    verdict = verdict_for(intent_class, checks, candidate_output)
    row = {
        "schema": "founder-intent-approval-machine-receipt-v1",
        "at": now(),
        "machine_version": spec["version"],
        "input": {
            "surface": surface,
            "message_preview": (message or "")[:240],
            "input_hash": sha16(message or ""),
            "candidate_hash": sha16(candidate_output) if candidate_output else None,
        },
        "intent_class": intent_class,
        "meaning": compile_meaning(message, intent_class),
        "route": route,
        "approved_output_shape": approved_shape(intent_class),
        "critic_findings": findings,
        "machine_checks": checks,
        "verdict": verdict,
        "return_package": None,
        "next_action": "Proceed inside approved route." if verdict in {"APPROVED", "APPROVED_SPEC"} else "Fix findings before output approval.",
    }
    if verdict == "ASK_FOUNDER":
        row["return_package"] = {"question": "Should this become public copy, code behavior, a rule/guardrail, or a work order?"}
    elif verdict == "RETURN_TO_AGENT":
        row["return_package"] = {"blockers": [f for f in findings if f.get("severity") == "blocker"]}
    if write:
        RECEIPT_PATH.parent.mkdir(parents=True, exist_ok=True)
        RECEIPT_PATH.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return row


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--message", required=True)
    parser.add_argument("--surface", default="unknown")
    parser.add_argument("--candidate-output", default="")
    parser.add_argument("--no-write", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    row = run_machine(args.message, surface=args.surface, candidate_output=args.candidate_output, write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(f"{row['verdict']} · {row['intent_class']} · {row['meaning']}")
    return 0 if row["verdict"] in {"APPROVED", "APPROVED_SPEC"} else 2


if __name__ == "__main__":
    raise SystemExit(main())
