#!/usr/bin/env python3
"""Signal Factory v1 — classify, score, decide, receipt (Architect/Fable contract).

Synthetic tests + structural verification only. No production inbox connections.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data/signal-factory-v1.json"
SKILL_DIR = ROOT / ".cursor/skills/signal-factory"
TESTS_DIR = SKILL_DIR / "tests"
REPORT_PATH = SKILL_DIR / "reports/test-report-v1.json"

CLASSIFICATION_KEYWORDS: list[tuple[str, str]] = [
    ("risk", r"\b(msb|psp|custody|settlement|banking|regulator|legal|compliance|subpoena|fintrac|rpaa)\b"),
    ("spam", r"\b(unsubscribe|lottery|crypto airdrop|nigerian prince|winner|claim prize)\b"),
    ("investor", r"\b(investor|funding|seed round|angel|vc|venture capital|term sheet)\b"),
    ("partner", r"\b(partner|equity|co-founder|cofounder|advisor|joint venture|jv)\b"),
    ("client", r"\b(quote|contact us|web form|intake|repair shop|auto shop|kim'?s auto)\b"),
    ("vendor", r"\b(seo|marketing agency|backlink|guest post|lead gen|vendor pitch)\b"),
    ("bug", r"\b(bug|broken|error|crash|regression|500 error)\b"),
    ("idea", r"\b(idea|feature request|suggestion|what if|could you build)\b"),
]

ENTITY_NAMES = ("Noetfield", "TrustField", "SourceA", "WitnessBC", "SG", "NOOS")

PRODUCTION_PATTERNS = (
    r"gmail\.com",
    r"googleapis\.com/gmail",
    r"linkedin\.com/api",
    r"graph\.microsoft\.com",
    r"imap\.|smtp\.",
    r"website.?form.?hook",
)

OPTIONAL_SECTION_KEYS = ("automation_recipe", "commercial_idea")


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_ssot() -> dict[str, Any]:
    return json.loads(SSOT.read_text(encoding="utf-8"))


def classify_signal(text: str) -> str:
    lower = text.lower()
    for classification, pattern in CLASSIFICATION_KEYWORDS:
        if re.search(pattern, lower, re.I):
            return classification
    return "unclear"


def score_signal(text: str, classification: str, sender_claims: list[dict[str, Any]]) -> dict[str, int]:
    lower = text.lower()
    trust = 2
    risk = 1
    automation = 1
    commercial = 1

    if re.search(r"\b(verified|contract|invoice|existing customer)\b", lower):
        trust += 1
    if sender_claims:
        trust = max(0, trust - 1)

    if classification == "risk":
        risk = max(risk, 4)
    if re.search(r"\b(msb|psp|custody|settlement|banking)\b", lower):
        risk = max(risk, 4)
    if classification == "partner":
        risk = max(risk, 3)
    if classification == "spam":
        risk = max(risk, 1)
        trust = 0

    if classification in ("bug", "idea"):
        automation += 2
    if classification == "client":
        commercial += 2
        automation += 1
    if classification in ("vendor", "investor"):
        commercial += 1
    if classification == "partner":
        commercial += 1

    return {
        "trust_score": min(5, max(0, trust)),
        "risk_score": min(5, max(0, risk)),
        "automation_value": min(5, max(0, automation)),
        "commercial_value": min(5, max(0, commercial)),
    }


def infer_entity_scope(text: str) -> str:
    for entity in ENTITY_NAMES:
        if re.search(rf"\b{re.escape(entity)}\b", text, re.I):
            return entity
    return "SourceA"


def decide(
    classification: str,
    scores: dict[str, int],
    entity_scope: str,
    text: str = "",
) -> tuple[str, str, str]:
    risk = scores["risk_score"]
    lower = text.lower()
    if risk >= 4:
        return (
            "route",
            "Route to Sina / legal / human review — risk override (risk ≥ 4).",
            f"route:{entity_scope}:human_legal_review",
        )

    if classification == "spam":
        return ("archive", "Archive spam signal with receipt only.", f"archive:{entity_scope}")

    if classification == "client" or re.search(r"kim'?s auto", lower):
        return (
            "create_service_pattern",
            "Draft bounded SMB intake chatbot service pattern — no employment outreach.",
            f"service_pattern:{entity_scope}:smb_intake",
        )

    if classification == "bug" and scores["automation_value"] >= 3:
        return (
            "build_automation",
            "Propose automation recipe scoped to entity — adapters remain empty hooks.",
            f"automation:{entity_scope}:recipe",
        )

    if classification == "idea" and scores["automation_value"] >= 3:
        return (
            "build_automation",
            "Propose automation recipe for repeatable idea intake — adapters remain empty hooks.",
            f"automation:{entity_scope}:recipe",
        )

    if classification == "investor":
        return (
            "reply",
            "Bounded reply to investor signal — no unverified claims.",
            f"reply:{entity_scope}:investor",
        )

    if classification == "partner":
        return (
            "reply",
            "Bounded exploratory reply — partner/advisor signal only.",
            f"reply:{entity_scope}:partner_explore",
        )

    if classification == "vendor":
        return ("ignore", "Ignore vendor pitch — market telemetry logged.", f"ignore:{entity_scope}")

    if classification == "risk":
        return (
            "route",
            "Route to Sina / legal / human review.",
            f"route:{entity_scope}:human_legal_review",
        )

    return ("ignore", "Monitor signal; no automation or service pattern yet.", f"ignore:{entity_scope}")


def build_memory_line(entity_scope: str, classification: str, decision: str, signal_id: str) -> str:
    return (
        f"signal-factory-v1 | entity={entity_scope} | class={classification} | "
        f"decision={decision} | id={signal_id}"
    )


def build_receipt(
    *,
    signal_id: str,
    entity_scope: str,
    classification: str,
    scores: dict[str, int],
    decision: str,
    next_action: str,
    sender_claims: list[dict[str, Any]],
    ssot: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema": "signal-factory-receipt-v1",
        "signal_id": signal_id,
        "timestamp": _now_iso(),
        "source": "signal_factory_core_v1",
        "created_at": _now_iso(),
        "entity_scope": entity_scope,
        "classification": classification,
        "scores": scores,
        "decision": decision,
        "action": next_action,
        "result": "classified",
        "status": "ok",
        "next_action": next_action,
        "risk_score": scores["risk_score"],
        "sender_claims": sender_claims,
        "adapter_hooks": dict(ssot.get("adapter_hooks") or {}),
        "claim_ladder_note": "Externally-facing text uses VERIFIED / DECLARED / PLANNED only.",
        "production_connected": False,
    }


def analyze_signal(
    text: str,
    *,
    sender_claims: list[dict[str, Any]] | None = None,
    entity_scope: str | None = None,
) -> dict[str, Any]:
    ssot = load_ssot()
    sender_claims = sender_claims or []
    normalized_claims = []
    for claim in sender_claims:
        normalized_claims.append(
            {
                "text": claim.get("text", ""),
                "tag": "sender_declared",
                "source": claim.get("source", "sender"),
            }
        )

    classification = classify_signal(text)
    scores = score_signal(text, classification, normalized_claims)
    scope = entity_scope or infer_entity_scope(text)
    decision, next_action, _route_key = decide(classification, scores, scope, text)
    signal_id = str(uuid.uuid4())

    report: dict[str, Any] = {
        "schema": "signal-factory-decision-report-v1",
        "signal_summary": text.strip()[:500],
        "classification": classification,
        "implied_need": f"Address {classification.replace('_', ' ')} for {scope}.",
        **scores,
        "decision": decision,
        "next_action": next_action,
        "receipt": build_receipt(
            signal_id=signal_id,
            entity_scope=scope,
            classification=classification,
            scores=scores,
            decision=decision,
            next_action=next_action,
            sender_claims=normalized_claims,
            ssot=ssot,
        ),
        "memory_line": build_memory_line(scope, classification, decision, signal_id),
    }

    if decision == "build_automation":
        report["automation_recipe"] = {
            "entity_scope": scope,
            "steps": ["intake", "classify", "score", "receipt"],
            "adapters": "hooks_only_empty",
            "status": "PLANNED",
        }
    if decision == "create_service_pattern":
        report["commercial_idea"] = {
            "entity_scope": scope,
            "pattern": "bounded_service_outline",
            "employment_outreach": False,
            "status": "PLANNED",
        }

    return report


def _collect_text_blobs(report: dict[str, Any]) -> str:
    parts = [
        str(report.get("signal_summary", "")),
        str(report.get("implied_need", "")),
        str(report.get("next_action", "")),
        str(report.get("memory_line", "")),
        json.dumps(report.get("receipt") or {}, sort_keys=True),
    ]
    for key in OPTIONAL_SECTION_KEYS:
        if key in report:
            parts.append(json.dumps(report[key], sort_keys=True))
    return "\n".join(parts)


def check_entity_hygiene(report: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    scope = (report.get("receipt") or {}).get("entity_scope") or infer_entity_scope(
        report.get("signal_summary", "")
    )
    blob = _collect_text_blobs(report)
    for entity in ENTITY_NAMES:
        if entity == scope:
            continue
        if re.search(rf"\b{re.escape(entity)}\b offers\b.*\b{re.escape(scope)}\b", blob, re.I):
            errors.append(f"cross-attribution: {entity} offers attributed to {scope}")
        if re.search(rf"\b{re.escape(scope)}\b is (a|an) .*\b{re.escape(entity)}\b", blob, re.I):
            errors.append(f"cross-attribution: {scope} mislabeled as {entity}")
    return errors


def verify_report(report: dict[str, Any], ssot: dict[str, Any] | None = None) -> dict[str, Any]:
    ssot = ssot or load_ssot()
    errors: list[str] = []

    for field in ssot["required_report_fields"]:
        if field not in report:
            errors.append(f"missing required field: {field}")

    classification = report.get("classification")
    if classification not in ssot["classifications"]:
        errors.append(f"invalid classification: {classification}")

    decision = report.get("decision")
    if decision not in ssot["decisions"]:
        errors.append(f"invalid decision: {decision}")

    for score_field in ssot["score_fields"]:
        value = report.get(score_field)
        if not isinstance(value, int) or value < 0 or value > 5:
            errors.append(f"invalid score {score_field}: {value}")

    risk = report.get("risk_score")
    if isinstance(risk, int) and risk >= ssot["risk_override"]["threshold"]:
        if decision != "route":
            errors.append("risk ≥ 4 must force decision=route")
        route_phrase = ssot["risk_override"]["route_target"]
        next_action = str(report.get("next_action", "")).lower()
        if route_phrase.lower() not in next_action and "human" not in next_action and "legal" not in next_action:
            errors.append("route must target human/legal review")

    for section, meta in ssot["optional_sections"].items():
        present = section in report
        allowed = set(meta["allowed_decisions"])
        if present and decision not in allowed:
            errors.append(f"{section} present but decision={decision} not in {sorted(allowed)}")
        if decision in allowed and section not in report:
            errors.append(f"{section} required when decision={decision}")

    for forbidden_decision, sections in (
        ("ignore", OPTIONAL_SECTION_KEYS),
        ("archive", OPTIONAL_SECTION_KEYS),
        ("reply", OPTIONAL_SECTION_KEYS),
        ("route", OPTIONAL_SECTION_KEYS),
    ):
        if decision == forbidden_decision:
            for section in sections:
                if section in report:
                    errors.append(f"{section} must not appear when decision={forbidden_decision}")

    receipt = report.get("receipt") or {}
    if receipt.get("production_connected") is True:
        errors.append("production_connected must be false in v1 core")

    hooks = receipt.get("adapter_hooks") or {}
    expected_hooks = ssot.get("adapter_hooks") or {}
    if set(hooks.keys()) != set(expected_hooks.keys()):
        errors.append("adapter_hooks keys mismatch")
    for name, value in hooks.items():
        if value not in (None, {}, []):
            errors.append(f"adapter hook {name} must be empty")

    for claim in receipt.get("sender_claims") or []:
        if claim.get("tag") != "sender_declared":
            errors.append("sender claim missing sender_declared tag")

    errors.extend(check_entity_hygiene(report))

    return {"ok": not errors, "errors": errors}


def check_no_production_connection() -> list[str]:
    errors: list[str] = []
    paths = [
        SKILL_DIR / "SKILL.md",
        Path(__file__),
    ]
    for path in paths:
        if not path.is_file():
            errors.append(f"missing file for production scan: {path}")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        for pattern in PRODUCTION_PATTERNS:
            if re.search(pattern, text, re.I):
                errors.append(f"production connection pattern {pattern} in {path}")
    return errors


def _apply_case_expectations(
    report: dict[str, Any],
    case: dict[str, Any],
    verification: dict[str, Any],
    ssot: dict[str, Any],
) -> None:
    for key, expected in (case.get("expect") or {}).items():
        actual = report.get(key)
        if actual != expected:
            verification["errors"].append(f"expect {key}={expected} got {actual}")

    for key, minimum in (case.get("expect_min") or {}).items():
        actual = report.get(key)
        if not isinstance(actual, int) or actual < minimum:
            verification["errors"].append(f"expect_min {key}>={minimum} got {actual}")

    for key, maximum in (case.get("expect_max") or {}).items():
        actual = report.get(key)
        if not isinstance(actual, int) or actual > maximum:
            verification["errors"].append(f"expect_max {key}<={maximum} got {actual}")

    if case.get("expect_score_bounds"):
        for score_field in ssot["score_fields"]:
            value = report.get(score_field)
            if not isinstance(value, int) or value < 0 or value > 5:
                verification["errors"].append(f"score bounds failed for {score_field}: {value}")

    for key in case.get("expect_absent") or []:
        if key in report:
            verification["errors"].append(f"expect absent {key}")

    for key in case.get("expect_present") or []:
        if key not in report:
            verification["errors"].append(f"expect present {key}")

    for key, expected in (case.get("expect_receipt") or {}).items():
        actual = (report.get("receipt") or {}).get(key)
        if actual != expected:
            verification["errors"].append(f"expect receipt.{key}={expected} got {actual}")

    entity_scope = (case.get("expect_receipt") or {}).get("entity_scope")
    if entity_scope:
        memory_line = str(report.get("memory_line", ""))
        if f"entity={entity_scope}" not in memory_line:
            verification["errors"].append(f"memory_line missing entity={entity_scope}")
        for other in ENTITY_NAMES:
            if other == entity_scope:
                continue
            if f"entity={other}" in memory_line:
                verification["errors"].append(f"memory_line cross-entity leak: entity={other}")

    verification["ok"] = not verification["errors"]


def run_tests() -> dict[str, Any]:
    ssot = load_ssot()
    cases = sorted(TESTS_DIR.glob("test_*.json"))
    results: list[dict[str, Any]] = []
    passed = 0

    for case_path in cases:
        case = json.loads(case_path.read_text(encoding="utf-8"))
        case_id = case.get("id") or case_path.stem
        mode = case.get("mode", "analyze")

        if mode == "verify_fixture":
            report = case["report"]
            verification = verify_report(report, ssot)
            _apply_case_expectations(report, case, verification, ssot)
        else:
            report = analyze_signal(
                case["input"]["text"],
                sender_claims=case["input"].get("sender_claims"),
                entity_scope=case["input"].get("entity_scope"),
            )
            verification = verify_report(report, ssot)
            _apply_case_expectations(report, case, verification, ssot)

        ok = verification["ok"]
        if ok:
            passed += 1
        results.append(
            {
                "id": case_id,
                "file": str(case_path.relative_to(ROOT)),
                "ok": ok,
                "errors": verification["errors"],
            }
        )

    production_errors = check_no_production_connection()
    summary = {
        "schema": "signal-factory-test-report-v1",
        "created_at": _now_iso(),
        "total": len(results),
        "passed": passed,
        "failed": len(results) - passed,
        "ok": passed == len(results) and not production_errors,
        "production_scan_errors": production_errors,
        "results": results,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description="Signal Factory v1 core")
    parser.add_argument("--text", help="Signal text to analyze")
    parser.add_argument("--verify-json", help="Path to decision report JSON to verify")
    parser.add_argument("--run-tests", action="store_true", help="Run synthetic test suite")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.run_tests:
        summary = run_tests()
        if args.json:
            print(json.dumps(summary, indent=2))
        else:
            print(f"tests: {summary['passed']}/{summary['total']} ok={summary['ok']}")
        return 0 if summary["ok"] else 1

    if args.verify_json:
        report = json.loads(Path(args.verify_json).read_text(encoding="utf-8"))
        result = verify_report(report)
        if args.json:
            print(json.dumps(result, indent=2))
        return 0 if result["ok"] else 1

    if not args.text:
        parser.error("provide --text, --verify-json, or --run-tests")
    report = analyze_signal(args.text)
    verification = verify_report(report)
    out = {"report": report, "verification": verification}
    if args.json:
        print(json.dumps(out, indent=2))
    return 0 if verification["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
