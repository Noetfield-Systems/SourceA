#!/usr/bin/env python3
"""Founder chat gate — Worker must read ASF message before INBOX pickup (INCIDENT-031+)."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPTS))

from worker_asf_directive_latch_v1 import read_latch  # noqa: E402

RUN_INBOX_EXACT = frozenset(
    {
        "run inbox",
        "continue",
        "continue drain",
        "pickup",
        "go",
        "execute inbox",
    }
)

PLAN_PHRASES = (
    "give me your plan",
    "give me the plan",
    "give me a plan",
    "your plan",
    "just the plan",
    "plan only",
    "no help",
    "don't help",
    "do not help",
    "stop helping",
    "read my order",
    "read my chat",
    "listen to me",
)

QUESTION_START = re.compile(r"^(what|why|how|are you|update your task|what are)", re.I)


def classify_founder_chat(text: str) -> str:
    t = (text or "").strip()
    if not t:
        return "EMPTY"
    low = t.lower()
    if low in RUN_INBOX_EXACT or low.startswith("run inbox"):
        return "RUN_INBOX"
    if any(p in low for p in PLAN_PHRASES):
        return "PLAN_ONLY"
    if QUESTION_START.search(t):
        return "FOUNDER_QUESTION"
    if "?" in t:
        return "FOUNDER_QUESTION"
    if len(t) > 12:
        return "FOUNDER_ORDER"
    return "RUN_INBOX"


def should_defer_inbox(*, founder_message: str = "") -> dict:
    lat = read_latch()
    msg_class = classify_founder_chat(founder_message)

    if lat.get("plan_only"):
        if msg_class == "RUN_INBOX":
            return {"defer": False, "reason": "founder_resumed_inbox", "class": msg_class}
        return {
            "defer": True,
            "reason": "plan_only_latch",
            "class": msg_class,
            "hint": "Answer founder with PLAN bullets only — no implement, no queue rebuild talk. Say 'run inbox' when ready.",
        }

    if msg_class in {"PLAN_ONLY", "FOUNDER_QUESTION", "FOUNDER_ORDER"}:
        return {
            "defer": True,
            "reason": "founder_chat_first",
            "class": msg_class,
            "hint": "Read founder message verbatim first. PLAN_ONLY = bullets only, zero help/implement. Then 'run inbox' to resume queue.",
        }

    return {"defer": False, "reason": "inbox_ok", "class": msg_class}


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser()
    ap.add_argument("--text", default="", help="Founder latest message")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = should_defer_inbox(founder_message=args.text)
    if args.json or True:
        print(json.dumps(row, indent=2))
    return 0 if not row.get("defer") else 2


if __name__ == "__main__":
    raise SystemExit(main())
