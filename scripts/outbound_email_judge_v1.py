#!/usr/bin/env python3
"""OEGCC advisory judge — heuristic reply-worthiness (never ship authority).

Separate from deterministic linter pass/fail. Does not call an LLM.
Law: docs/SOURCEA_OUTBOUND_EMAIL_GENERATOR_CHECKER_CONTROLLER_LOOP_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "outbound-email-judge-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def judge_draft(body: str, *, lint_row: dict | None = None) -> dict:
    """Advisory only — linter pass does not imply high reply-worthiness."""
    text = body.strip()
    low = text.lower()
    words = len(re.findall(r"\b[\w']+\b", text))
    has_question = "?" in text
    banned_openers = (
        "i came across",
        "i noticed",
        "hope you're well",
        "we're building",
        "our platform",
        "i wanted to reach out",
    )
    opener_penalty = any(low.startswith(op) for op in banned_openers)
    product_terms = ("trustfield", "noetfield", "platform", "pricing", "demo link")
    product_penalty = any(t in low for t in product_terms)
    lint_fail = bool(lint_row and not lint_row.get("ok"))

    score = 70
    notes: list[str] = []
    if words > 100:
        score -= 15
        notes.append("long")
    elif words < 40:
        score -= 5
        notes.append("thin")
    if not has_question:
        score -= 20
        notes.append("no_question")
    if opener_penalty:
        score -= 25
        notes.append("banned_opener")
    if product_penalty:
        score -= 20
        notes.append("product_pitch")
    if lint_fail:
        score -= 30
        notes.append("lint_fail")

    score = max(0, min(100, score))
    band = "high" if score >= 75 else "medium" if score >= 50 else "low"
    return {
        "schema": "outbound-email-judge-v1",
        "advisory_only": True,
        "never_ship_authority": True,
        "score": score,
        "band": band,
        "notes": notes,
        "line": f"oegcc-judge · advisory · {band} · score={score} · never_auto_send",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="OEGCC advisory judge (heuristic)")
    ap.add_argument("--body-file", type=Path, required=True)
    ap.add_argument("--lint-json", type=Path)
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    body = args.body_file.read_text(encoding="utf-8") if args.body_file.is_file() else ""
    lint_row: dict = {}
    if args.lint_json and args.lint_json.is_file():
        lint_row = json.loads(args.lint_json.read_text(encoding="utf-8"))

    row = judge_draft(body, lint_row=lint_row)
    row["at"] = _now()
    if args.write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
