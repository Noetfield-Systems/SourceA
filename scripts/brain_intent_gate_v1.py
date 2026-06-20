#!/usr/bin/env python3
"""Detect founder intent — routes Brain away from executor/E2E traps (INCIDENT-026)."""
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

# INCIDENT-026 class — Brain must NOT run fast ladder (executor trap)
AUDIT_CHEAP_E2E_PATTERNS = [
    r"check everything",
    r"check e2e",
    r"full e2e",
    r"e2e sweep",
    r"validate everything",
    r"is factory green",
    r"everything e2e",
    r"from scratch and fix",
]


def classify(message: str) -> str:
    low = (message or "").strip().lower()
    if any(re.search(p, low, re.I) for p in AUDIT_CHEAP_E2E_PATTERNS):
        return "AUDIT_CHEAP_E2E"
    if any(re.search(p, low, re.I) for p in ACTIVATE_PATTERNS):
        return "ACTIVATE"
    if any(re.search(p, low, re.I) for p in NARRATE_ONLY_PATTERNS):
        return "NARRATE_ONLY"
    if any(re.search(p, low, re.I) for p in RUN_TRACE_PATTERNS):
        return "RUN_TRACE"
    return "OTHER"


CHEAP_E2E_ALLOWED = [
    "bash scripts/brain-session-start.sh",
    "python3 scripts/brain_session_guard_v1.py --write --json",
    "python3 scripts/factory_idle_gate_v1.py --json",
    "bash scripts/validate-sourcea-e2e-preflight-v1.sh",
    "SINA_FCB_FAST=1 python3 scripts/find_critical_bugs.py",
    "python3 scripts/brain_validate_goal1_v1.py --write-receipt",
]

CHEAP_E2E_FORBIDDEN = [
    "validate-e2e-fast-ladder-v1.sh",
    "validate-sourcea-e2e-standard-v1.sh",
    "validate-sourcea-e2e-full-v1.sh",
    "build-sina-command-panel.py",
]


def _pivot_slice(message: str, *, write_route: bool = False) -> dict:
    if not (message or "").strip():
        return {}
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from founder_pivot_router_v1 import route_founder_pivot  # noqa: WPS433

        return route_founder_pivot(
            message,
            source="brain_intent_gate",
            run_machines=False,
            write=write_route,
        )
    except Exception as exc:
        return {"matched": False, "error": str(exc)}


def gate(*, message: str, *, write_pivot: bool = False) -> dict:
    intent = classify(message)
    pivot = _pivot_slice(message, write_route=write_pivot)
    if pivot.get("matched"):
        intent = "FOUNDER_PIVOT"
    if intent == "AUDIT_CHEAP_E2E":
        allowed = list(CHEAP_E2E_ALLOWED)
        mandatory = "python3 scripts/brain_session_guard_v1.py --write --json"
        note = (
            "AUDIT_CHEAP_E2E — Brain routes only. Max 90s. "
            "If not idle: preflight + fcb FAST → STOP → Worker inbox. "
            "Never fast ladder in Brain (INCIDENT-026 rule collision fix)."
        )
        return {
            "status": "BRAIN_INTENT_GATE",
            "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "intent": intent,
            "lane": "brain",
            "input_class": "ASF order",
            "founder_message_preview": (message or "")[:200],
            "mandatory_command": mandatory,
            "allowed_commands": allowed,
            "forbidden_commands": list(CHEAP_E2E_FORBIDDEN),
            "max_shell_seconds": 90,
            "max_reply_seconds": 30,
            "delegate_ladder_to": "sourcea_worker",
            "law": "BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md",
            "incident": "SINA_BRAIN_E2E_RETRY_STORM_INCIDENT_026_LOCKED_v1.md",
            "note": note,
            "rule_collision_resolved": (
                "ASF audit order + agent-loop executor + smart-judgment heal "
                "→ cheap proof only in Brain; ladder on Worker when idle."
            ),
        }
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
    elif intent == "FOUNDER_PIVOT":
        allowed = [
            "bash scripts/brain-session-start.sh",
            "python3 scripts/founder_pivot_router_v1.py --json",
            "python3 scripts/founder_input_cascade_v1.py --json",
        ]
        mandatory = "python3 scripts/founder_pivot_router_v1.py --json"
        note = (
            "FOUNDER_PIVOT — disk route_pack locked · read founder-pivot-routing-receipt · "
            "founder does not repeat · quote inject_line + one tap"
        )
    else:
        allowed = [
            "bash scripts/brain-session-start.sh",
            "python3 scripts/brain_session_guard_v1.py --write --json",
        ]
        mandatory = "bash scripts/brain-session-start.sh"
        note = "Normal Brain — route only; no E2E ladder (§4 BRAIN_UNIFIED)"
    row = {
        "status": "BRAIN_INTENT_GATE",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "intent": intent,
        "lane": "brain",
        "founder_message_preview": (message or "")[:200],
        "mandatory_command": mandatory,
        "allowed_commands": allowed,
        "forbidden_commands": list(CHEAP_E2E_FORBIDDEN),
        "max_shell_seconds": 90,
        "note": note,
        "run_trace": "Default for run the loop — spawn when gates green",
    }
    if pivot.get("matched"):
        row["founder_pivot"] = {
            "pivot_id": pivot.get("pivot_id"),
            "pivot_label": pivot.get("pivot_label"),
            "inject_line": pivot.get("inject_line"),
            "work_template": pivot.get("work_template"),
            "founder_one_tap": pivot.get("founder_one_tap"),
            "receipt": str(SINA / "founder-pivot-routing-receipt-v1.json"),
        }
    return row


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
    row = gate(message=msg, write_pivot=args.write)
    if args.write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
