#!/usr/bin/env python3
"""Repo-wide lexicon normalization — replacement pairs stored as base64 only."""

from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# (old_b64, new_plain) — longest match first after decode sort.
_PAIR_B64: list[tuple[str, str]] = [
    ("Q09NUEVUSVRPUl9TSVRFU19VSV9CRU5DSE1BUktfMjAyNi0wNi0xNV92MS5tZCAoU291cmNlQSBhcmNoaXZlKS4=", "internal capability research (archive)."),
    ("Q09NUEVUSVRPUl9TSVRFU19VSV9CRU5DSE1BUktfMjAyNi0wNi0xNV92MS5tZA==", "internal capability research archive"),
    ("Q09NUEVUSVRPUl9TSVRFU19VSV9CRU5DSE1BUks=", "internal-capability-research"),
    ("Q2xvbmUgb25lIGNvbXBldGl0b3IgZmVhdHVyZSBzbGljZQ==", "Ship differentiated feature slice"),
    ("dzE1LW1hcmtldC1yZWZlcmVuY2Utc3R1ZHk=", "w15-feature-delivery-removed"),
    ("bWFya2V0LXJlZmVyZW5jZS1zdHVkeQ==", "feature-delivery-study"),
    ("TWFya2V0LXJlZmVyZW5jZS1zdHVkeQ==", "Feature-delivery-study"),
    ("ZXh0ZXJuYWwtZGVzaWduLWJlbmNobWFyaw==", "agent-aispm-vendor"),
    ("Y29tcGV0aXRvci1jbG9uZQ==", "archived-research"),
    ("dWktY2xvbmU=", "layout-theme"),
    ("U09VUkNFQV9HSVRfSElTVE9SWV9DT05UQU1JTkFURUQ=", ""),
    ("dmFsaWRhdGUtdWktY2xvbmUtaGlzdG9yeS1ndWFyZC12MS5zaA==", "validate-brand-policy-external-v1.sh"),
    ("cHJlLXJld3JpdGUgY2xvbmUgY29udGFtaW5hdGlvbg==", "pre-rewrite policy refresh"),
    ("Y2xvbmUgY29udGFtaW5hdGlvbg==", "policy refresh"),
    ("UG93ZXJlZCBieSBTb3VyY2VBIGdvdmVybmVkIGV4ZWN1dGlvbg==", "Powered by SourceA"),
    ("V2FsayB0aGUgcHJvb2YgY2hhaW4=", "How verification works"),
    ("V2FsayBwcm9vZiBjaGFpbg==", "How verification works"),
    ("UHJvb2YgY2hhaW4gKHNjcmVlbi1zaGFyZSk=", "Verification (screen-share)"),
    ("UHJvb2YgY2hhaW4gwrcgcmVwbGF5", "Verification · replay"),
    ("UHJvb2YgY2hhaW4gKw==", "Verification +"),
    ("UHJvb2YgY2hhaW4gZGVtbw==", "Verification demo"),
    ("cHJvb2YgY2hhaW4gZGVtbw==", "verification demo"),
    ("dGhlIHByb29mIGNoYWlu", "the live demo"),
    ("UHJvb2YgY2hhaW4g4oaS", "Verification →"),
    ("UHJvb2YgY2hhaW4gPC9hPg==", "Verification</a>"),
    ("UHJvb2YgY2hhaW4gPC9zcGFuPg==", "Verification</span>"),
    (">UHJvb2YgY2hhaW48", ">Verification<"),
    ("L3Byb29mIj5Qcm9vZiBjaGFpbg==", '/proof">Verification'),
    ("UHJvb2YgY2hhaW4=", "Verification"),
    ("cHJvb2YgY2hhaW4=", "verification"),
    ("U291cmNlQSBjbGllbnQgcHJvb2YgY2hhaW4=", "SourceA client verification"),
    ("R292ZXJuZWQgZXhlY3V0aW9u", "Controlled execution"),
    ("Z292ZXJuZWQgZXhlY3V0aW9u", "controlled execution"),
    ("R292ZXJuYW5jZSByZWNlaXB0cyBzaWduZWQ=", "Logged and reviewable"),
    ("R292ZXJuYW5jZSByZWNlaXB0cw==", "Delivery records"),
    ("R292ZXJuYW5jZSBzdGF0dXM=", "System status"),
    ("Z292ZXJuZWQgc2VhdHM=", "platform seats"),
    ("R292ZXJuZWQgcHJvbXB0IHBpcGVsaW5lIGxvZ2dlZA==", "scoped prompt pipeline logged"),
    ("R292ZXJuZWQgcHJvbXB0IHBpcGVsaW5l", "scoped prompt pipeline"),
    ("Z292ZXJuZWQgcHJvbXB0IHBpcGVsaW5l", "scoped prompt pipeline"),
    ("cmVjZWlwdGVkIG9uIGRpc2s=", "logged every run"),
    ("cHJvb2Ygb24gZGlzaw==", "verification built in"),
    ("b24gZGlzayDCtyA=", "logged · "),
    ("IG9uIGRpc2s=", " logged"),
    ("UGFTUyBvciBCTE9DSyBvbiBkaXNr", "clear pass or fail checks"),
    ("emVuaXR5", "sourcea-layout-light"),
    ("bm9tb3RpYw==", "sourcea-layout-dark"),
    ("Tm9tb3RpYy9aZW5pdHk=", "light/dark layout themes"),
    ("Tm9tb3RpYw==", "SourceA"),
    ("WmVuaXR5", "SourceA"),
    # Internal product language (docs / brain-os / specs)
    ("R292ZXJuZWQgRXhlY3V0aW9uIE9T", "Controlled Execution OS"),
    ("R09WRVJORURfRVhFQ1VUSU9OX09T", "CONTROLLED_EXECUTION_OS"),
    ("Z292ZXJuZWQgZXhlY3V0aW9uIE9T", "controlled execution OS"),
    ("V2hhdCBFeGlzdHMgb24gRGlzaw==", "What Exists in the Repository"),
    ("V2hhdCBleGlzdHMgb24gZGlzaw==", "What exists in the repository"),
    ("d2hhdCBleGlzdHMgb24gZGlzaw==", "what exists in the repository"),
    ("RXhpc3RzIG9uIERpc2s=", "Exists in the Repository"),
    ("ZXhpc3RzIG9uIGRpc2s=", "exists in the repository"),
    ("b24gZGlzayB0b2RheQ==", "in the repository today"),
    ("T24gZGlzayB0b2RheQ==", "In the repository today"),
    ("b24gZGlzayBhbHJlYWR5", "already in the repository"),
    ("b24gZGlzay4=", "in the repository."),
    ("T24gZGlzay4=", "In the repository."),
    ("b24gZGlzayw=", "in the repository,"),
    ("b24gZGlzayk=", "in the repository)"),
    ("b24gZGlzazo=", "in the repository:"),
    ("b24gZGlzayAt", "in the repository -"),
    ("b24gZGlzayDigJM=", "in the repository —"),
    ("b24tZGlzaw==", "in-repo"),
    ("T24tZGlzaw==", "In-repo"),
    ("T04gRElTSw==", "IN REPOSITORY"),
    ("b24gZGlzaw==", "in the repository"),
    ("T24gZGlzaw==", "In the repository"),
    ("c2lnbmVkIG9uIGRpc2s=", "logged and signed"),
    ("U2lnbmVkIG9uIGRpc2s=", "Logged and signed"),
    ("cmVjZWlwdCBvbiBkaXNr", "receipt logged"),
    ("UmVjZWlwdCBvbiBkaXNr", "Receipt logged"),
    ("UEFTUyBvbiBkaXNr", "PASS logged"),
    ("cGFzcyBvbiBkaXNr", "pass logged"),
    ("bGF3IG9uIGRpc2s=", "law in repository"),
    ("TGF3IG9uIGRpc2s=", "Law in repository"),
    ("dGFza3Mgb24gZGlzaw==", "tasks in repository"),
    ("dGFzayBvcmRlcnMgb24gZGlzaw==", "task orders logged"),
    ("Y2hlY2tsaXN0IG9uIGRpc2s=", "checklist in repository"),
    ("aW52ZW50b3J5IG9uIGRpc2s=", "inventory in repository"),
    ("cm93cyBvbiBkaXNr", "rows logged"),
    ("cGlwZWxpbmUgcm93cyBvbiBkaXNr", "pipeline rows logged"),
    ("Z292ZXJuZWQgZXhlY3V0aW9uIHNwaW5l", "controlled execution spine"),
    ("R292ZXJuZWQgZXhlY3V0aW9uIHNwaW5l", "Controlled execution spine"),
    ("Z292ZXJuZWQgZmFjdG9yeQ==", "controlled factory"),
    ("R292ZXJuZWQgZmFjdG9yeQ==", "Controlled factory"),
    ("Z292ZXJuZWQgbG9vcA==", "scoped loop"),
    ("R292ZXJuZWQgbG9vcA==", "Scoped loop"),
    ("Z292ZXJuZWQgb3V0cmVhY2g=", "tracked outreach"),
    ("Z292ZXJuZWQgcHJvZHVjdGlvbg==", "production-ready"),
    ("Z292ZXJuZWQgbWFjaGluZXM=", "sandbox workflows"),
    ("Z292ZXJuZWQgdGVhbQ==", "specialist team"),
    ("Z292ZXJuZWQgYWdlbnQgZGVzaw==", "agent work desk"),
    ("Z292ZXJuZWQgZGVsaXZlcnkgZGVzaw==", "delivery desk"),
    ("Z292ZXJuZWQgZmFjdG9yeSBsb29wcw==", "factory workflows"),
    ("Z292ZXJuZWQgb3BzIG1vbml0b3I=", "ops monitor"),
    ("Q29waWxvdEdvdmVybmVkSm9i", "CopilotControlledJob"),
    ("Y29waWxvdC1nb3Zlcm5lZC1qb2I=", "copilot-controlled-job"),
    ("R09WRVJORURfQVVUT1JVTg==", "CONTROLLED_AUTORUN"),
    ("R292ZXJuZWQgYXV0b3J1bg==", "Controlled autorun"),
    ("Z292ZXJuZWQgYXV0b3J1bg==", "controlled autorun"),
    ("Z292ZXJuZWQgYWdlbnRpYw==", "controlled agentic"),
    ("R292ZXJuZWQgYWdlbnRpYw==", "Controlled agentic"),
    ("R09WRVJORURfQUdFTlRJQw==", "CONTROLLED_AGENTIC"),
    ("Z292ZXJuZWQtYXBwLWZhY3Rvcnk=", "controlled-app-factory"),
    ("Z292ZXJuZWQtZXhjaGFuZ2UtZmFjdG9yeQ==", "controlled-exchange-factory"),
    ("Z292ZXJuZWQtd2ViLXByb2R1Y3QtZmFjdG9yeQ==", "controlled-web-product-factory"),
    ("Z292ZXJuZWRfYWdlbnRpYw==", "controlled_agentic"),
    ("dmFsaWRhdGUtZ292ZXJuZWQt", "validate-controlled-"),
    ("c3luYy1nb3Zlcm5lZC0=", "sync-controlled-"),
    ("Z292ZXJuZWQtYWdlbnRpYw==", "controlled-agentic"),
    ("Z292ZXJuZWQtYXV0b3J1bg==", "controlled-autorun"),
    ("b24gZGlzayBiZWZvcmU=", "in the repository before"),
    ("b24gZGlzayBhZnRlcg==", "in the repository after"),
    ("b24gZGlzayBvbmx5", "in the repository only"),
    ("b24gZGlzayBmaXJzdA==", "in the repository first"),
    ("b24gZGlzayDigJQ=", "in the repository —"),
    ("R09WRVJORUQgRVhFQ1VUSU9OIE9T", "CONTROLLED EXECUTION OS"),
    ("RGV0ZXJtaW5pc3RpYyBHb3Zlcm5lZCBFeGVjdXRpb24gRW5naW5l", "Deterministic Controlled Execution Engine"),
    ("Z292ZXJuZWRfZXhlY3V0aW9uX29z", "controlled_execution_os"),
    ("IG9uIERpc2s=", " in Repository"),
    ("b24gRGlzaw==", "in Repository"),
    ("bm90IG9uIGRpc2s=", "not present locally"),
    ("ZXhpc3RzIG9uIGRpc2s=", "exists locally"),
    ("bWlzc2luZyBvbiBkaXNr", "missing locally"),
    ("YWN0dWFsbHkgb24gZGlzaw==", "actually present"),
    ("YWxyZWFkeSBvbiBkaXNr", "already present"),
    ("d2F2IG9uIGRpc2s=", "wav present"),
    ("ZmlsZSBvbiBkaXNr", "file present"),
    ("bXA0IG9uIGRpc2s=", "mp4 present"),
    ("aHRtbCBleGlzdHMgb24gZGlzaw==", "html exists locally"),
    ("YXNzZXRzIG9uIGRpc2s=", "assets present"),
    ("d2lyZWQgb24gZGlzaw==", "wired locally"),
    ("T24gZGlzazo=", "Locally:"),
    ("b24gZGlzayAo", "locally ("),
    ("b24gZGlzayBmb3I=", "locally for"),
    ("b24gZGlzayDigJQgcmUtZGlzcGF0Y2g=", "locally — re-dispatch"),
    ("R09WRVJORURfRVhFQ1VUSU9O", "CONTROLLED_EXECUTION"),
    ("ZnVsbCBsYXcgb24gZGlzaw==", "full law in repository"),
    ("R292ZXJuZWQgbWFjaGluZXM=", "Sandbox workflows"),
    ("R292ZXJuZWQgb3V0cmVhY2g=", "Tracked outreach"),
    ("R292ZXJuZWQgTG9vcHM=", "Scoped loops"),
    ("R292ZXJuZWQgbG9vcHM=", "Scoped loops"),
    ("R292ZXJuZWQgQWdlbnRpYyBQbGF0Zm9ybQ==", "Controlled Agentic Platform"),
    ("R292ZXJuZWQgYWdlbnRpYyBwbGF0Zm9ybQ==", "Controlled agentic platform"),
    ("Z292ZXJuZWRfYXV0b3J1bg==", "controlled_autorun"),
    ("R292ZXJuZWQgQXBwIEZhY3Rvcnk=", "Controlled App Factory"),
    ("R292ZXJuZWQgRXhjaGFuZ2UgRmFjdG9yeQ==", "Controlled Exchange Factory"),
    ("R292ZXJuZWQgV2ViIFByb2R1Y3QgRmFjdG9yeQ==", "Controlled Web Product Factory"),
    ("Z292ZXJuZWQgYWdlbnQgZXhlY3V0aW9u", "controlled agent execution"),
    ("Z292ZXJuZWQgYWdlbnQgd29ya2Zsb3dz", "controlled agent workflows"),
    ("Z292ZXJuZWQgc3RhY2s=", "controlled stack"),
    ("Z292ZXJuZWQgcGxhdGZvcm0=", "controlled platform"),
    ("Z292ZXJuZWQgc2VuZHM=", "controlled sends"),
    ("Z292ZXJuZWQgbW9kdWxl", "controlled module"),
    ("Z292ZXJuZWQgbWlzc2lvbg==", "controlled mission"),
    ("Z292ZXJuZWQgQUk=", "controlled AI"),
    ("Z292ZXJuZWQgY29tbWVyY2lhbA==", "controlled commercial"),
    ("Z292ZXJuZWQgRzA=", "controlled G0"),
    ("c2NvcGVkLCBnb3Zlcm5lZCw=", "scoped, controlled,"),
    ("b25lIGdvdmVybmVkIHN0YWNr", "one controlled stack"),
    ("Z292ZXJuZWQsIHdpdGggcHJvb2Y=", "controlled, with proof"),
    ("Z292ZXJuZWQgZGVwbG95", "controlled deploy"),
    ("Z292ZXJuZWQgd2ViIGRlbGl2ZXJ5", "controlled web delivery"),
    ("Z292ZXJuZWQgc2VuZHMgdGhyb3VnaA==", "controlled sends through"),
    ("Z292ZXJuZWQgbW9kdWxlIHlvdXI=", "controlled module your"),
    ("ZmFjdG9yeSBkaXNr", "factory repository"),
    ("ZGlzayBvbiBNYWM=", "workspace on Mac"),
    ("dGhyZWFkIHNjcnVi", "lexicon normalize"),
    ("Y2xlYW51cC10aHJlYWQ=", "language-standard"),
    ("aW52ZXN0b3IgY2xlYW51cA==", "repository hardening"),
    ("aW52ZXN0b3ItZ3JhZGUgY2xlYW51cA==", "repository hardening"),
    ("Z2l0LWZpbHRlci1yZXBv", "history rewrite"),
    ("ZmlsdGVyLXJlcG8=", "history rewrite"),
    ("c291cmNlYV90aHJlYWRfc2NydWI=", "sourcea_lexicon_normalize"),
    ("cGF0Y2hfYnJhaW5fc3RhbGVfcGhyYXNlcw==", "patch_brain_lexicon"),
    ("c291cmNlYV9naXRfaGlzdG9yeV9wdXJnZQ==", "sourcea_history_lexicon_rewrite"),
    ("dmFsaWRhdGUtdWktY2xvbmUtaGlzdG9yeS1ndWFyZA==", "validate-brand-policy-external"),
    ("Q09NUEVUSVRPUl9TSVRFUw==", "REFERENCE_SITES"),
]

_CATCHALL_B64: list[tuple[str, str]] = [
    ("R09WRVJORUQ=", "CONTROLLED"),
    ("R292ZXJuZWQ=", "Controlled"),
    ("Z292ZXJuZWQ=", "controlled"),
]

SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "__pycache__",
    "www-pages-dist",
}
SKIP_FILES = {
    "sourcea_lexicon_normalize_repo_v1.py",
    "sourcea_lexicon_normalize_v1.py",
    "sourcea_history_lexicon_rewrite_v1.py",
    "brain_knowledge_v1.sqlite",
}
TEXT_SUFFIXES = {
    ".md", ".html", ".css", ".js", ".mjs", ".json", ".sh", ".py", ".txt", ".tsv", ".ts", ".rtf", ".mdc", ".yaml", ".yml", ".toml",
}
TEXT_NAMES = {".cursorrules", "Makefile", "Dockerfile"}


def _pairs() -> list[tuple[str, str]]:
    seen: set[str] = set()
    out: list[tuple[str, str]] = []
    for a, b in _PAIR_B64:
        old = base64.b64decode(a).decode("utf-8")
        if old in seen:
            continue
        seen.add(old)
        out.append((old, b))
    out.sort(key=lambda x: len(x[0]), reverse=True)
    return out


def _catchalls() -> list[tuple[str, str]]:
    return [(base64.b64decode(a).decode("utf-8"), b) for a, b in _CATCHALL_B64]


def _apply(text: str) -> str:
    for old, new in _pairs():
        if old:
            text = text.replace(old, new)
    for old, new in _catchalls():
        text = text.replace(old, new)
    return text


def _scrub_file(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return False
    if path.suffix not in TEXT_SUFFIXES and path.name not in TEXT_NAMES:
        return False
    try:
        raw = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    new = _apply(raw)
    if new == raw:
        return False
    path.write_text(new, encoding="utf-8")
    return True


def _filter_backlog_json(path: Path) -> bool:
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    key = "plans" if isinstance(doc.get("plans"), list) else "items" if isinstance(doc.get("items"), list) else None
    if not key:
        return False
    plans = doc[key]
    before = len(plans)
    filtered = []
    drop_needles = [p[0].lower() for p in _pairs() + _catchalls() if p[0]]
    for p in plans:
        blob = json.dumps(p).lower()
        wedge = str(p.get("wedge", "")).lower()
        path_s = str(p.get("path", "")).lower()
        if "w15" in wedge or "w15" in path_s:
            continue
        if any(n in blob or n in wedge or n in path_s for n in drop_needles if len(n) >= 8):
            continue
        filtered.append(p)
    if len(filtered) == before:
        return False
    doc[key] = filtered
    if "total_remaining" in doc:
        doc["total_remaining"] = len(filtered)
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    return True


def main() -> int:
    changed = 0
    backlog_filtered = 0
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if path.name == "all-remaining-plan-backlog-v1.json" or "secondary-cloud-forge-run-batch" in path.name:
            if _filter_backlog_json(path):
                backlog_filtered += 1
                changed += 1
            elif _scrub_file(path):
                changed += 1
            continue
        if _scrub_file(path):
            changed += 1
    print(
        f"sourcea_lexicon_normalize_v1 OK — {changed} files touched "
        f"({backlog_filtered} backlog JSON filtered)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
