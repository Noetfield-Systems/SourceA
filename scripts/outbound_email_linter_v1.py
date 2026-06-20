#!/usr/bin/env python3
"""OEGCC Checker — deterministic outbound email linter (step 1).

Law: docs/SOURCEA_OUTBOUND_EMAIL_GENERATOR_CHECKER_CONTROLLER_LOOP_LOCKED_v1.md
SSOT: data/factory-email-translation-v1.json · data/outbound-factory-salvage-spec-v1.json
Receipt: ~/.sina/outbound-email-linter-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
TRANSLATION = ROOT / "data" / "factory-email-translation-v1.json"
SALVAGE = ROOT / "data" / "outbound-factory-salvage-spec-v1.json"
RECEIPT = SINA / "outbound-email-linter-receipt-v1.json"

WORD_SOFT_LIMIT = 100
WORD_HARD_LIMIT_DEFAULT = 140


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _body_for_lint(body: str) -> str:
    pre = body.split("Reply **stop**")[0] if "Reply **stop**" in body else body
    lines = pre.strip().splitlines()
    if lines and re.match(r"^subject\s*:", lines[0], re.I):
        lines = lines[1:]
    while lines and not lines[0].strip():
        lines = lines[1:]
    return "\n".join(lines).strip()


def _word_count(text: str) -> int:
    return len(re.findall(r"\b[\w']+\b", text))


def _word_limits(salvage: dict) -> tuple[int, int]:
    hard = WORD_HARD_LIMIT_DEFAULT
    for stage in salvage.get("four_human_stages") or []:
        if stage.get("name") == "Compose" and stage.get("email"):
            try:
                hard = int(stage.get("word_max") or hard)
            except (TypeError, ValueError):
                pass
            break
    return WORD_SOFT_LIMIT, hard


def _failure_to_repair_line(row: dict) -> str:
    fid = str(row.get("id") or "")
    if fid == "word_count":
        return (
            f"- Word count {row.get('got')}, limit is {row.get('limit')}. "
            f"{row.get('hint', 'Cut filler; keep the question.')}"
        )
    if fid == "word_count_soft":
        return (
            f"- Word count {row.get('got')}, soft target is {row.get('limit')}. "
            f"{row.get('hint', 'Trim to under 100 words.')}"
        )
    if fid == "banned_opener":
        return (
            f"- Banned opener detected: \"{row.get('match')}\". "
            f"{row.get('hint', 'Delete that phrase and start on the tension.')}"
        )
    if fid == "forbidden_one":
        term = row.get("match") or row.get("term") or "term"
        hint = row.get("hint") or "Remove or translate to plain language."
        return f"- Forbidden term: \"{term}\". {hint}"
    if fid == "lane_forbidden":
        return f"- Lane forbidden phrase: \"{row.get('match')}\". {row.get('hint', 'Remove phrase.')}"
    if fid.startswith("salvage_pattern"):
        return f"- Pattern fail: {row.get('pattern')}. {row.get('hint', '')}"
    return f"- {fid}: {row.get('hint') or row.get('match') or 'fix required'}"


def lint_email(
    body: str,
    *,
    subject: str = "",
    lane: str = "",
    region: str = "canada",
    trans: dict | None = None,
    salvage: dict | None = None,
) -> dict:
    """Deterministic OEGCC checker — structured failures for controller repair."""
    sys.path.insert(0, str(SCRIPTS))
    from validate_email_translation_v1 import (  # noqa: WPS433
        check_lane_forbidden,
        check_regional_vocabulary,
    )

    trans = trans or _read_json(TRANSLATION)
    salvage = salvage or _read_json(SALVAGE)
    soft_limit, hard_limit = _word_limits(salvage)
    text = _body_for_lint(body)
    low = text.lower()
    words = _word_count(text)

    failures: list[dict] = []
    warnings: list[dict] = []

    if words > hard_limit:
        failures.append(
            {
                "id": "word_count",
                "severity": "fail",
                "limit": hard_limit,
                "got": words,
                "hint": f"Cut ~{words - hard_limit} words; remove second explanatory sentence, not the question.",
            }
        )
    elif words > soft_limit:
        warnings.append(
            {
                "id": "word_count_soft",
                "severity": "warn",
                "limit": soft_limit,
                "got": words,
                "hint": "OEGCC soft target is 100 words — trim before send.",
            }
        )

    for opener in trans.get("hard_fail_openers") or []:
        if low.lstrip().startswith(str(opener).lower()):
            failures.append(
                {
                    "id": "banned_opener",
                    "severity": "fail",
                    "match": opener,
                    "hint": "Delete that exact phrase and start on the tension instead.",
                }
            )
            break

    translate = trans.get("translate") or {}
    glossary = trans.get("human_primitive_glossary") or {}
    for term in trans.get("forbidden_in_email_one") or []:
        if term.lower() in low:
            suggest = translate.get(term) or glossary.get(term)
            hint = f"use '{suggest}'" if suggest else "Remove architecture noun."
            failures.append(
                {
                    "id": "forbidden_one",
                    "severity": "fail",
                    "match": term,
                    "hint": hint,
                }
            )

    if lane:
        lane_row = check_lane_forbidden(body, lane, trans)
        for hit in lane_row.get("hits") or []:
            failures.append(
                {
                    "id": "lane_forbidden",
                    "severity": "fail",
                    "match": hit,
                    "lane": lane,
                    "hint": "Remove lane-specific forbidden phrase.",
                }
            )

    regional = check_regional_vocabulary(body, region, trans)
    for issue in regional.get("issues") or []:
        failures.append(
            {
                "id": "regional_vocabulary",
                "severity": "fail",
                "match": issue,
                "hint": "; ".join(regional.get("routing_messages") or [])[:120] or "Fix regional term routing.",
            }
        )

    if re.search(r"\bwe've been spending time with teams\b", low):
        failures.append(
            {
                "id": "salvage_pattern",
                "severity": "fail",
                "pattern": "generic_skeleton_weve_been_spending_time_with_teams",
                "hint": "Replace generic skeleton with recipient-specific tension.",
            }
        )

    repair_lines = [_failure_to_repair_line(f) for f in failures]
    ok = not failures

    return {
        "schema": "outbound-email-linter-v1",
        "at": _now(),
        "ok": ok,
        "subject": subject,
        "lane": lane or None,
        "region": region,
        "word_count": words,
        "word_soft_limit": soft_limit,
        "word_hard_limit": hard_limit,
        "failures": failures,
        "warnings": warnings,
        "repair_lines": repair_lines,
        "law": "docs/SOURCEA_OUTBOUND_EMAIL_GENERATOR_CHECKER_CONTROLLER_LOOP_LOCKED_v1.md",
        "line": (
            f"outbound-linter · PASS · {words}w"
            if ok and not warnings
            else (
                f"outbound-linter · PASS · {words}w · warn={len(warnings)}"
                if ok
                else f"outbound-linter · BLOCK · {failures[0].get('id')} · {words}w"
            )
        ),
    }


def hard_fail_strings(body: str, *, lane: str = "", trans: dict | None = None) -> list[str]:
    """Legacy string list for icp_output_compiler integration."""
    row = lint_email(body, lane=lane, trans=trans)
    out: list[str] = []
    for f in row.get("failures") or []:
        fid = str(f.get("id") or "")
        if fid == "forbidden_one":
            out.append(f"forbidden_one:{f.get('match')}")
        elif fid == "banned_opener":
            out.append(f"hard_fail_opener:{f.get('match')}")
        elif fid == "lane_forbidden":
            out.append(f"lane_forbidden:{f.get('match')}")
        elif fid == "word_count":
            out.append(f"word_count_over:{f.get('got')}>{f.get('limit')}")
        else:
            out.append(f"{fid}:{f.get('match') or f.get('pattern') or '?'}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description="OEGCC outbound email linter")
    ap.add_argument("--body-file", type=Path)
    ap.add_argument("--stdin", action="store_true")
    ap.add_argument("--subject", default="")
    ap.add_argument("--lane", default="")
    ap.add_argument("--region", default="canada")
    ap.add_argument("--write-receipt", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    body = ""
    if args.stdin:
        body = sys.stdin.read()
    elif args.body_file and args.body_file.is_file():
        body = args.body_file.read_text(encoding="utf-8")
    else:
        print("FAIL: provide --body-file or --stdin", file=sys.stderr)
        return 2

    row = lint_email(body, subject=args.subject, lane=args.lane, region=args.region)
    if args.write_receipt:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or ("PASS" if row.get("ok") else "FAIL"))
        for line in row.get("repair_lines") or []:
            print(line)
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
