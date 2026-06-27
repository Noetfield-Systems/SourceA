#!/usr/bin/env python3
"""Verify Brain reply positioning — forbidden phrases + lead-price guard."""
from __future__ import annotations

import argparse
import json
import re
import sys

FORBIDDEN = [
    re.compile(r"\bopenrouter\b", re.I),
    re.compile(r"\bsk-[a-z0-9_-]{8,}", re.I),
    re.compile(r":13020|:13027|:8780|:8781"),
    re.compile(r"\bcom\.sourcea\.", re.I),
    re.compile(r"\bPASS/BLOCK\b"),
]

PRICE_LEAD = re.compile(r"\$\d{2,}|(?:^|\s)(?:1500|5000|6000|8000)(?:\s|$)")


def is_pricing_question(message: str) -> bool:
    return bool(re.search(r"\b(price|pricing|cost|how much|tier|\$)\b", message, re.I))


def verify_reply(reply: str, *, message: str = "", intent: str = "core") -> dict:
    text = (reply or "").strip()
    failures: list[str] = []
    if not text:
        failures.append("empty_reply")
    for pat in FORBIDDEN:
        if pat.search(text):
            failures.append(f"forbidden:{pat.pattern}")
    lower = text.lower()
    if not is_pricing_question(message) and intent not in ("buyer",):
        lead = lower[:100]
        if PRICE_LEAD.search(lead) and "forge terminal" not in lead:
            failures.append("lead_price")
    return {"ok": not failures, "failures": failures, "reply_preview": text[:200]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--reply", default="")
    parser.add_argument("--message", default="")
    parser.add_argument("--intent", default="core")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    if args.reply:
        result = verify_reply(args.reply, message=args.message, intent=args.intent)
    else:
        try:
            row = json.load(sys.stdin)
        except json.JSONDecodeError as exc:
            print(json.dumps({"ok": False, "error": str(exc)}))
            return 1
        result = verify_reply(
            str(row.get("reply") or ""),
            message=str(row.get("message") or ""),
            intent=str((row.get("retrieval") or {}).get("intent") or "core"),
        )

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print("OK" if result["ok"] else "FAIL", result.get("failures"))
    return 0 if result["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
