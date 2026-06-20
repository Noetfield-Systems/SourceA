#!/usr/bin/env python3
"""U029 — one product line max (at most one product paragraph).

Law: data/outbound-factory-100-upgrade-plan-v1.json · U029
Acceptance: two product paragraphs = fail
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPILE_DIR = ROOT / "data" / "icp-compile"

_BRAND_PARA = re.compile(r"\b(noetfield|trustfield|sourcea)\b", re.I)


def pre_signoff_body(text: str) -> str:
    return text.split("Reply **stop**")[0] if "Reply **stop**" in text else text


def _skip_block(block: str) -> bool:
    t = block.strip()
    if not t:
        return True
    if t.startswith("http"):
        return True
    if re.match(r"^hi\b", t, re.I):
        return True
    if re.match(r"^if (relevant|useful)", t, re.I):
        return True
    if re.match(r"^sina\b", t, re.I):
        return True
    if "powered by sourcea" in t.lower():
        return True
    if "@" in t and re.search(r"\.(com|ca)\b", t, re.I):
        return True
    return False


def product_paragraphs(text: str) -> list[str]:
    pre = pre_signoff_body(text)
    blocks = [b.strip() for b in re.split(r"\n\s*\n", pre) if b.strip()]
    out: list[str] = []
    for block in blocks:
        if _skip_block(block):
            continue
        if _BRAND_PARA.search(block):
            out.append(block)
    return out


def check_one_product_line(text: str) -> dict:
    paras = product_paragraphs(text)
    issues: list[str] = []
    if len(paras) > 1:
        issues.append("two_product_paragraphs")
    return {
        "ok": not issues,
        "issues": issues,
        "product_paragraph_count": len(paras),
        "upgrade": "U029",
    }


def validate_one_product_line_acceptance() -> dict:
    """U029 acceptance — two product paragraphs = fail."""
    two_product_fail = check_one_product_line(
        "Hi Chris —\n\n"
        "Board pressure on mortgage copilot decisions six months later.\n\n"
        "Noetfield replays copilot steps under audit pressure — one line product.\n\n"
        "TrustField also offers compliance replay for examiner questions.\n\n"
        "Curious if that maps to your timeline?"
    )
    one_product_pass = check_one_product_line(
        "Hi Chris —\n\n"
        "Board pressure on mortgage copilot decisions six months later.\n\n"
        "Noetfield replays copilot steps under audit pressure — one line product.\n\n"
        "Curious if that maps to your timeline?"
    )
    stub_rows: list[dict] = []
    for name in ("fundmore-approved-v1.txt", "ocree-approved-v1.txt", "sourcea-factory-approved-v1.txt"):
        path = COMPILE_DIR / name
        body = path.read_text(encoding="utf-8") if path.is_file() else ""
        row = check_one_product_line(body)
        row["path"] = str(path.relative_to(ROOT))
        stub_rows.append(row)
    acceptance_ok = (
        not two_product_fail.get("ok")
        and "two_product_paragraphs" in (two_product_fail.get("issues") or [])
        and (two_product_fail.get("product_paragraph_count") or 0) >= 2
        and one_product_pass.get("ok")
        and all(r.get("ok") for r in stub_rows)
    )
    return {
        "ok": acceptance_ok,
        "two_product_paragraphs": two_product_fail,
        "one_product_paragraph": one_product_pass,
        "approved_bodies": stub_rows,
        "acceptance": "Two product paragraphs = fail",
        "upgrade": "U029",
        "check": "python3 scripts/icp_one_product_line_gate_v1.py --check-acceptance --json",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="ICP one product line gate (U029)")
    ap.add_argument("--check-acceptance", action="store_true")
    ap.add_argument("--body", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.check_acceptance or not args.body:
        row = validate_one_product_line_acceptance()
    else:
        row = check_one_product_line(args.body)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print("check_one_product_line:", "PASS" if row.get("ok") else row.get("issues"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
