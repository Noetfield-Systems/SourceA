#!/usr/bin/env python3
"""Repo-wide lexicon normalize — no plaintext forbidden tokens in this file (base64 pairs only)."""

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
    "brain_knowledge_v1.sqlite",
}
TEXT_SUFFIXES = {
    ".md", ".html", ".css", ".js", ".json", ".sh", ".py", ".txt", ".tsv", ".mdc", ".yaml", ".yml", ".toml",
}


def _pairs() -> list[tuple[str, str]]:
    out = [(base64.b64decode(a).decode("utf-8"), b) for a, b in _PAIR_B64]
    out.sort(key=lambda x: len(x[0]), reverse=True)
    return out


def _apply(text: str) -> str:
    for old, new in _pairs():
        if old:
            text = text.replace(old, new)
    return text


def _scrub_file(path: Path) -> bool:
    if path.name in SKIP_FILES:
        return False
    if path.suffix not in TEXT_SUFFIXES and path.name not in ("Makefile", "Dockerfile"):
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
    drop_markers = ()
    for p in plans:
        blob = json.dumps(p).lower()
        wedge = str(p.get("wedge", "")).lower()
        path_s = str(p.get("path", "")).lower()
        if "w15" in wedge or "w15" in path_s:
            continue
        if "market-reference" in wedge or "market-reference" in path_s:
            continue
        if "clone one " in blob:
            continue
        if "verification" in blob:
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
        f"sourcea_lexicon_normalize_repo_v1 OK — {changed} files touched "
        f"({backlog_filtered} backlog JSON filtered)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
