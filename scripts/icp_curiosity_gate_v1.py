#!/usr/bin/env python3
"""U028 — curiosity question must be last before link block.

Law: data/outbound-factory-100-upgrade-plan-v1.json · U028
Acceptance: question after sign-off or link intro = fail
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILE_DIR = ROOT / "data" / "icp-compile"

_LINK_MARKERS = (
    re.compile(r"https?://", re.I),
    re.compile(r"^\s*if relevant", re.I | re.M),
    re.compile(r"^\s*if useful", re.I | re.M),
    re.compile(r"^\s*sina kazemnezhad", re.I | re.M),
)
SIGNOFF_MARK = "Reply **stop**"


def pre_signoff_body(text: str) -> str:
    return text.split(SIGNOFF_MARK)[0] if SIGNOFF_MARK in text else text


def post_signoff_body(text: str) -> str:
    if SIGNOFF_MARK not in text:
        return ""
    return text.split(SIGNOFF_MARK, 1)[1]


def link_block_index(text: str) -> int:
    pre = pre_signoff_body(text)
    hits: list[int] = []
    for pat in _LINK_MARKERS:
        m = pat.search(pre)
        if m:
            hits.append(m.start())
    return min(hits) if hits else len(pre)


def check_curiosity_before_link(text: str) -> dict:
    pre = pre_signoff_body(text)
    post = post_signoff_body(text)
    idx = link_block_index(text)
    narrative = pre[:idx]
    tail = pre[idx:]
    issues: list[str] = []
    if "?" not in narrative:
        issues.append("no_question_before_link")
    if "?" in tail:
        issues.append("question_after_link_or_signoff")
    if "?" in post:
        issues.append("question_after_signoff")
    lines = [ln.strip() for ln in narrative.splitlines() if ln.strip()]
    q_idx = [i for i, ln in enumerate(lines) if "?" in ln]
    if q_idx and q_idx[-1] < len(lines) - 1:
        issues.append("content_after_curiosity_question")
    return {"ok": not issues, "issues": issues, "upgrade": "U028"}


def validate_curiosity_gate_acceptance() -> dict:
    """U028 acceptance — question after sign-off = fail."""
    after_signoff_fail = check_curiosity_before_link(
        "Curious if this fits?\n\n"
        f"{SIGNOFF_MARK} — no further messages.\n\n"
        "Would a short replay help?"
    )
    after_link_fail = check_curiosity_before_link(
        "Opening line.\n\n"
        "If relevant — link:\n\nhttps://example.com/pilot/\n\n"
        "Still worth a look?"
    )
    stub_rows: list[dict] = []
    for name in ("fundmore-approved-v1.txt", "ocree-approved-v1.txt", "sourcea-factory-approved-v1.txt"):
        path = COMPILE_DIR / name
        body = path.read_text(encoding="utf-8") if path.is_file() else ""
        row = check_curiosity_before_link(body)
        row["path"] = str(path.relative_to(ROOT))
        stub_rows.append(row)
    acceptance_ok = (
        not after_signoff_fail.get("ok")
        and "question_after_signoff" in (after_signoff_fail.get("issues") or [])
        and not after_link_fail.get("ok")
        and all(r.get("ok") for r in stub_rows)
    )
    return {
        "ok": acceptance_ok,
        "after_signoff": after_signoff_fail,
        "after_link": after_link_fail,
        "approved_bodies": stub_rows,
        "acceptance": "Question after sign-off = fail",
        "upgrade": "U028",
        "check": "python3 scripts/icp_curiosity_gate_v1.py --check-acceptance --json",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="ICP curiosity gate — question last before link (U028)")
    ap.add_argument("--check-acceptance", action="store_true")
    ap.add_argument("--body", default="", help="Raw body text to check")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.check_acceptance:
        row = validate_curiosity_gate_acceptance()
    elif args.body:
        row = check_curiosity_before_link(args.body)
    else:
        row = validate_curiosity_gate_acceptance()

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print("check_curiosity:", "PASS" if row.get("ok") else row.get("issues") or row.get("after_signoff"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
