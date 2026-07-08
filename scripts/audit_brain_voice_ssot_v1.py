#!/usr/bin/env python3
"""Audit Brain public voice SSOT chain — logic, not phrase bans."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "reports"
POSITIONING = ROOT / "sites/SourceA-landing/green-unified/data/sourcea-positioning-v1.json"
MANUAL = ROOT / "data/chatbot-knowledge/manual/positioning-public.md"
RULES_JSON = ROOT / "data/brain-public-rules-v1.json"
BUNDLE = ROOT / "cloud/workers/sourcea-brain-chat-v1/src/knowledge-bundle.json"
GUARDRAILS = ROOT / "cloud/workers/sourcea-brain-chat-v1/src/guardrails.js"
WORKER_INDEX = ROOT / "cloud/workers/sourcea-brain-chat-v1/src/index.js"
RETRIEVAL = ROOT / "cloud/workers/sourcea-brain-chat-v1/src/retrieval.js"
HUB_CHAT = ROOT / "scripts/sourcea_brain_chat_v1.py"

STALE_VOICE_RE = re.compile(
    r"sourcea is an ai execution platform powered by forge|ai execution platform powered by forge",
    re.I,
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _one_line_from_md(text: str) -> str:
    m = re.search(r"## One line\s*\n+(.+)", text)
    return m.group(1).strip() if m else ""


def audit() -> dict:
    findings: list[dict] = []
    pos = json.loads(POSITIONING.read_text(encoding="utf-8")) if POSITIONING.is_file() else {}
    ssot_line = str(pos.get("one_line") or "").strip()

    if not ssot_line:
        findings.append({"id": "ssot_missing", "severity": "FAIL", "detail": "positioning JSON one_line empty"})

    manual_line = ""
    if MANUAL.is_file():
        manual_line = _one_line_from_md(MANUAL.read_text(encoding="utf-8"))
        if manual_line != ssot_line:
            findings.append(
                {
                    "id": "manual_drift",
                    "severity": "FAIL",
                    "detail": "positioning-public.md one_line != JSON SSOT",
                    "ssot": ssot_line[:120],
                    "manual": manual_line[:120],
                }
            )
    else:
        findings.append({"id": "manual_missing", "severity": "FAIL", "detail": str(MANUAL)})

    rules = json.loads(RULES_JSON.read_text(encoding="utf-8")) if RULES_JSON.is_file() else {}
    if str(rules.get("one_line") or "").strip() != ssot_line:
        findings.append({"id": "rules_json_drift", "severity": "FAIL", "detail": "brain-public-rules one_line != JSON SSOT"})

    bundle_row: dict = {}
    stale_chunks: list[str] = []
    bundle_one_line = ""
    if BUNDLE.is_file():
        bundle_row = json.loads(BUNDLE.read_text(encoding="utf-8"))
        bundle_one_line = str(bundle_row.get("public_one_line") or "").strip()
        if bundle_one_line and bundle_one_line != ssot_line:
            findings.append({"id": "bundle_field_drift", "severity": "FAIL", "detail": "bundle.public_one_line != JSON SSOT"})
        if not bundle_one_line:
            findings.append(
                {
                    "id": "bundle_missing_public_one_line",
                    "severity": "FAIL",
                    "detail": "knowledge-bundle.json missing public_one_line (sync must embed SSOT)",
                }
            )
        for ch in bundle_row.get("chunks") or []:
            if STALE_VOICE_RE.search(str(ch.get("content") or "")):
                stale_chunks.append(str(ch.get("id") or ch.get("source_path")))
        if stale_chunks:
            findings.append(
                {
                    "id": "bundle_stale_chunks",
                    "severity": "FAIL",
                    "detail": f"{len(stale_chunks)} chunks contain stale phrase",
                    "chunk_ids": stale_chunks[:20],
                }
            )
    else:
        findings.append({"id": "bundle_missing", "severity": "FAIL", "detail": str(BUNDLE)})

    for label, path in (
        ("guardrails_js", GUARDRAILS),
        ("hub_chat_py", HUB_CHAT),
    ):
        if path.is_file() and STALE_VOICE_RE.search(path.read_text(encoding="utf-8")):
            findings.append({"id": f"{label}_hardcoded_stale", "severity": "FAIL", "detail": str(path)})

    retrieval_src = RETRIEVAL.read_text(encoding="utf-8") if RETRIEVAL.is_file() else ""
    logic_checks = {
        "identity_question_helper": "isIdentityQuestion" in retrieval_src,
        "bundle_public_one_line_in_prompt": "public_one_line" in retrieval_src,
        "rules_first_pipeline": "rules_first" in retrieval_src or "splitCorpus" in retrieval_src,
    }
    for key, ok in logic_checks.items():
        if not ok:
            findings.append(
                {"id": f"retrieval_logic_gap_{key}", "severity": "FAIL", "detail": f"missing {key} in retrieval.js"}
            )

    if "cleanKnownPublicAnswer" in (GUARDRAILS.read_text(encoding="utf-8") if GUARDRAILS.is_file() else ""):
        if re.search(
            r"what is sourcea\|one sentence[\s\S]{0,200}return SOURCEA_ONE_LINE",
            GUARDRAILS.read_text(encoding="utf-8"),
            re.I,
        ):
            findings.append(
                {
                    "id": "prohibited_rule_override",
                    "severity": "FAIL",
                    "detail": "guardrails short-circuits identity answers instead of retrieval SSOT",
                }
            )

    fail = [f for f in findings if f["severity"] == "FAIL"]
    return {
        "schema": "audit-brain-voice-ssot-v1",
        "at": _now(),
        "verdict": "FAIL" if fail else "PASS",
        "ssot_one_line": ssot_line,
        "manual_one_line": manual_line,
        "bundle_public_one_line": bundle_one_line,
        "bundle_chunk_count": bundle_row.get("chunk_count"),
        "stale_chunk_count": len(stale_chunks),
        "logic_checks": logic_checks,
        "findings": findings,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    report = audit()
    REPORTS.mkdir(parents=True, exist_ok=True)
    out = REPORTS / "audit-brain-voice-ssot-v1.json"
    out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    md = REPORTS / "audit-brain-voice-ssot-v1.md"
    md.write_text(
        "\n".join(
            [
                "# Brain voice SSOT audit",
                "",
                f"**Verdict:** `{report['verdict']}`",
                f"**At:** {report['at']}",
                "",
                f"**SSOT one line:** {report.get('ssot_one_line', '')}",
                "",
                "## Findings",
                "",
            ]
            + [f"- **{f['severity']}** `{f['id']}` — {f['detail']}" for f in report.get("findings") or []]
            + ["", f"JSON: `{out.relative_to(ROOT)}`", ""]
        ),
        encoding="utf-8",
    )
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"{report['verdict']}: {len(report.get('findings') or [])} findings → {out.relative_to(ROOT)}")
    return 1 if report["verdict"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
