#!/usr/bin/env python3
"""Detect founder intent — RUN_TRACE vs NARRATE_ONLY vs ACTIVATE."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # SourceA root
SINA = Path.home() / ".sina"
RECEIPT = SINA / "brain-intent-gate-v1.json"
NARRATE_LOCK = SINA / "brain-narrate-mode-lock-v1.json"

# Watcher only — do NOT spawn
NARRATE_ONLY_PATTERNS = [
    r"narrate only",
    r"watch only",
    r"watcher mode",
    r"do not spawn",
    r"explain only",
    r"monitor without running",
]

ACTIVATE_PATTERNS = [
    r"^activate loop",
    r"^execute turn",
    r"^execute loop",
]

# Default: run the loop = trace gates + spawn if READY
RUN_TRACE_PATTERNS = [
    r"run the loop",
    r"run loop",
    r"start the loop",
    r"step-by-step",
    r"narrating each action",
    r"final answer",
    r"for workers",
    r"monitor",
]


def classify(message: str) -> str:
    low = (message or "").strip().lower()
    if any(re.search(p, low, re.I) for p in ACTIVATE_PATTERNS):
        return "ACTIVATE"
    if any(re.search(p, low, re.I) for p in NARRATE_ONLY_PATTERNS):
        return "NARRATE_ONLY"
    if any(re.search(p, low, re.I) for p in RUN_TRACE_PATTERNS):
        return "RUN_TRACE"
    return "OTHER"


def gate(*, message: str) -> dict:
    intent = classify(message)
    if intent == "NARRATE_ONLY":
        allowed = ["python3 scripts/brain_narrate_loop_v1.py"]
        mandatory = "python3 scripts/brain_narrate_loop_v1.py"
        note = "Watcher only — no spawn"
    elif intent == "RUN_TRACE":
        allowed = ["python3 scripts/brain_run_loop_trace_v1.py"]
        mandatory = "python3 scripts/brain_run_loop_trace_v1.py"
        note = "Run loop: trace gates (1-9) + spawn step 10 if READY; Brain reply <30s; loop continues on disk"
    elif intent == "ACTIVATE":
        allowed = ["python3 scripts/brain_run_loop_v1.py", "python3 scripts/brain_execute_turn_v1.py --yaml"]
        mandatory = "python3 scripts/brain_run_loop_v1.py"
        note = "Explicit spawn — headless agent"
    else:
        allowed = []
        mandatory = None
        note = "No Goal 1 loop intent"
    return {
        "status": "BRAIN_INTENT_GATE",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "intent": intent,
        "founder_message_preview": (message or "")[:200],
        "mandatory_command": mandatory,
        "allowed_commands": allowed,
        "note": note,
        "run_trace": "Default for run the loop — spawn when gates green",
    }


def set_narrate_lock() -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    NARRATE_LOCK.write_text(
        json.dumps({"active": True, "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")}, indent=2) + "\n",
        encoding="utf-8",
    )


def narrate_lock_active() -> bool:
    if not NARRATE_LOCK.is_file():
        return False
    try:
        return bool(json.loads(NARRATE_LOCK.read_text(encoding="utf-8")).get("active"))
    except (OSError, json.JSONDecodeError):
        return False


def clear_narrate_lock() -> None:
    NARRATE_LOCK.unlink(missing_ok=True)


def refuse_if_narrate_lock(caller: str) -> dict | None:
    if not narrate_lock_active():
        return None
    return {
        "ok": False,
        "error": "BRAIN_NARRATE_MODE",
        "caller": caller,
        "message": "Narrate-only lock active — use brain_run_loop_trace or clear lock",
        "law": "BRAIN_UNIFIED_RULES_LOCKED_v1.md",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--message", default="")
    p.add_argument("--stdin", action="store_true")
    p.add_argument("--write", action="store_true")
    p.add_argument("--set-narrate-lock", action="store_true")
    p.add_argument("--clear-narrate-lock", action="store_true")
    args = p.parse_args()
    if args.set_narrate_lock:
        set_narrate_lock()
        print(json.dumps({"ok": True, "narrate_lock": True}))
        return 0
    if args.clear_narrate_lock:
        clear_narrate_lock()
        print(json.dumps({"ok": True, "narrate_lock": False}))
        return 0
    msg = args.message
    if args.stdin:
        msg = sys.stdin.read()
    row = gate(message=msg)
    if args.write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
