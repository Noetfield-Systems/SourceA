#!/usr/bin/env python3
"""OEGCC Generator — fixed system prompt + repair injection assembly.

Does not call an LLM. Emits messages for Worker/Brain or external generator.
Law: docs/SOURCEA_OUTBOUND_EMAIL_GENERATOR_CHECKER_CONTROLLER_LOOP_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "outbound-email-oegcc-v1.json"

GENERATOR_SYSTEM = """You write a single cold email. Your only goal is to earn a thoughtful
human reply, not to explain a product.

INPUTS: a research profile and ONE chosen tension. Use only these.

HARD RULES (your output will be rejected automatically if broken):
- Under 100 words.
- No banned openers: "I came across", "I noticed", "Hope you're well",
  "We're building", "Our platform", "I wanted to reach out".
- No product name, features, pricing, architecture, or disclaimers.
- Lead with the insight/tension. End with one genuine question.
- Translate any technical term into plain language before using it.

Output ONLY the subject line and body. No commentary."""


def build_initial_user_prompt(*, research_profile: str, tension: str) -> str:
    return (
        "RESEARCH PROFILE:\n"
        f"{research_profile.strip()}\n\n"
        "CHOSEN TENSION (one only):\n"
        f"{tension.strip()}\n\n"
        "Write subject line and body."
    )


def build_repair_user_prompt(*, draft: str, lint_row: dict) -> str:
    failures_block = "\n".join(lint_row.get("repair_lines") or [])
    if not failures_block.strip():
        failures_block = "- (no structured failures — trim and fix obvious rule breaks)"
    return (
        "Your previous draft was rejected. Fix ONLY the listed failures.\n"
        "Keep everything that is not mentioned — do not rewrite from scratch.\n\n"
        "PREVIOUS DRAFT:\n"
        f"{draft.strip()}\n\n"
        "FAILURES (each must be resolved):\n"
        f"{failures_block}\n\n"
        "Return the corrected subject and body only."
    )


def build_messages(
    *,
    research_profile: str,
    tension: str,
    draft: str = "",
    lint_row: dict | None = None,
) -> list[dict]:
    if draft and lint_row and not lint_row.get("ok"):
        return [
            {"role": "system", "content": GENERATOR_SYSTEM},
            {"role": "user", "content": build_repair_user_prompt(draft=draft, lint_row=lint_row)},
        ]
    return [
        {"role": "system", "content": GENERATOR_SYSTEM},
        {"role": "user", "content": build_initial_user_prompt(research_profile=research_profile, tension=tension)},
    ]


def main() -> int:
    ap = argparse.ArgumentParser(description="OEGCC generator prompt assembly")
    ap.add_argument("--research", default="")
    ap.add_argument("--tension", default="")
    ap.add_argument("--draft-file", type=Path)
    ap.add_argument("--lint-json", type=Path, help="Prior lint result JSON for repair prompt")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    lint_row: dict = {}
    draft = ""
    if args.draft_file and args.draft_file.is_file():
        draft = args.draft_file.read_text(encoding="utf-8")
    if args.lint_json and args.lint_json.is_file():
        lint_row = json.loads(args.lint_json.read_text(encoding="utf-8"))

    messages = build_messages(
        research_profile=args.research or "(profile)",
        tension=args.tension or "(tension)",
        draft=draft,
        lint_row=lint_row or None,
    )
    row = {
        "schema": "outbound-email-generator-v1",
        "mode": "repair" if draft and lint_row else "initial",
        "system": GENERATOR_SYSTEM,
        "messages": messages,
        "ssot": str(SSOT.relative_to(ROOT)),
    }
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        for m in messages:
            print(f"=== {m['role'].upper()} ===")
            print(m["content"])
            print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
