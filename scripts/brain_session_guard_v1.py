#!/usr/bin/env python3
"""Brain session guard — forbid long E2E shells; emit founder next action logged.

Brain chat must NOT run validate-sourcea-e2e-full / standard (6+ min).
Factory proof is already logged; Brain routes Worker INBOX only.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
OUT = Path.home() / ".sina" / "brain-current-action-v1.json"
INTENT_RECEIPT = Path.home() / ".sina" / "brain-intent-gate-v1.json"

FORBIDDEN = (
    "validate-sourcea-e2e-full-v1.sh",
    "validate-sourcea-e2e-standard-v1.sh",
    "validate-e2e-fast-ladder-v1.sh",  # Worker/maintainer only — idle gate required (INCIDENT-026)
    "build-sina-command-panel.py",  # strict build in Brain chat — Worker/build lane only
)

FORBIDDEN_RECURSION = (
    "validate-live-prompt-feed-e2e-v1.sh",
    "live-prompt-lane-score-v1.py",
    "live_prompt_lane_audit_v1.py",
    "cross-plan-readiness-v1.py",
)

FORBIDDEN_PATTERNS = (
    "&&",  # chained validators in one Brain shell — INCIDENT-026
)

MAX_BRAIN_SHELL_SEC = 90
MAX_BRAIN_REPLY_SEC = 30
INCIDENT_026 = "brain-os/incidents/SINA_BRAIN_E2E_RETRY_STORM_INCIDENT_026_LOCKED_v1.md"
E2E_CHECKLIST = Path.home() / ".sina/brain/E2E_EXECUTOR_CHECKLIST_LOCKED_v1.md"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_json(cmd: list[str]) -> dict:
    try:
        raw = subprocess.check_output(cmd, cwd=str(ROOT), text=True, stderr=subprocess.DEVNULL)
        return json.loads(raw)
    except (subprocess.CalledProcessError, json.JSONDecodeError, FileNotFoundError):
        return {}


def _load_intent() -> dict:
    if not INTENT_RECEIPT.is_file():
        return {}
    try:
        return json.loads(INTENT_RECEIPT.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_guard() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from factory_validation_lock_v1 import status as lock_status, sweep_stale_lock  # noqa: E402

    sweep_stale_lock()
    lock = lock_status()
    intent = _load_intent()
    idle = _run_json([sys.executable, str(SCRIPTS / "factory_idle_gate_v1.py"), "--json"])
    brain = _run_json([sys.executable, str(SCRIPTS / "brain_validate_goal1_v1.py"), "--json"])
    inbox = brain.get("inbox") or {}
    orch = brain.get("orchestrator") or {}
    chain = brain.get("chain") or {}

    factory_locked = bool(lock.get("locked"))
    inbox_pending = bool(inbox.get("pending"))
    sa_id = str(inbox.get("sa_id") or orch.get("expected_sa") or "")
    brain_ok = bool(brain.get("ok"))

    idle_ok = bool(idle.get("idle"))
    idle_blockers = idle.get("blockers") or []

    if factory_locked:
        next_action = "WAIT — factory E2E lock held; do not start another shell"
        founder_click = "Wait for E2E to finish or sweep lock"
    elif inbox_pending and sa_id:
        next_action = f"WORKER — RUN INBOX on {sa_id} (Brain: preflight only — NO ladder)"
        founder_click = "▶ RUN INBOX in SourceA Worker chat"
    elif str(intent.get("intent") or "") == "AUDIT_CHEAP_E2E" and not idle_ok:
        next_action = "AUDIT_CHEAP — BLOCKED · preflight + fcb FAST only · NO ladder"
        founder_click = "SourceA Worker → run inbox once · Brain must STOP"
    elif not idle_ok:
        next_action = f"BLOCKED — factory not idle: {idle_blockers[0] if idle_blockers else 'see factory_idle_gate'}"
        founder_click = "Worker run inbox once · then Refresh hub"
    elif str(intent.get("intent") or "") == "AUDIT_CHEAP_E2E":
        next_action = "AUDIT_CHEAP — preflight + fcb FAST · delegate ladder to Worker"
        founder_click = "Brain STOP after cheap proof · Worker for idle ladder"
    elif brain_ok:
        next_action = "BRAIN — route/deliver; cheap proof only (preflight + fcb FAST)"
        founder_click = "Refresh hub · check factory-now.line"
    else:
        next_action = "BRAIN — read brain-goal1-validation-v1.json; fix chain FAIL only"
        founder_click = "Refresh hub · read validation receipt"

    return {
        "schema": "brain-current-action-v1",
        "at": _now(),
        "brain_ok": brain_ok,
        "factory_lock": lock.get("lock") if factory_locked else None,
        "chain": chain,
        "inbox": inbox,
        "forbidden_in_brain_chat": list(FORBIDDEN) + list(FORBIDDEN_RECURSION),
        "forbidden_patterns": list(FORBIDDEN_PATTERNS),
        "max_shell_seconds": MAX_BRAIN_SHELL_SEC,
        "max_reply_seconds": MAX_BRAIN_REPLY_SEC,
        "factory_idle": idle,
        "brain_intent": intent,
        "e2e_checklist": str(E2E_CHECKLIST),
        "allowed_brain_shells": [
            "bash scripts/brain-session-start.sh",
            "python3 scripts/brain_fast_startup_v1.py",
            "bash scripts/validate-sourcea-e2e-preflight-v1.sh",
            "SINA_FCB_FAST=1 python3 scripts/find_critical_bugs.py",
            "python3 scripts/factory_idle_gate_v1.py --json",
            "python3 scripts/brain_validate_goal1_v1.py --write-receipt",
            "bash scripts/validate-closeout-receipt-only-v1.sh",
        ],
        "forbidden_brain_e2e": (
            "Never validate-e2e-fast-ladder in Brain chat. "
            "Max 1 ladder per Worker turn with --require-idle only."
        ),
        "receipt_read_closeouts": [
            "python3 scripts/live-prompt-worker-closeout-v1.py --json",
            "python3 scripts/cross-plan-readiness-v1.py --fast --json",
        ],
        "conduct_reminder": (
            "INCIDENT-026: implement → receipt → reply <30s → STOP. "
            "Never chain validators. Never Await >90s. Closeout reads receipts only."
        ),
        "incident_026": INCIDENT_026,
        "next_action": next_action,
        "founder_click": founder_click,
        "law": "BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md",
        "note": (
            "activate READY/WAIT means Worker handoff pending — not Brain stuck. "
            "Cancel any Brain chat shell waiting >90s on E2E."
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Brain session guard")
    p.add_argument("--json", action="store_true")
    p.add_argument("--write", action="store_true")
    args = p.parse_args()
    row = build_guard()
    if args.write:
        OUT.parent.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"next_action: {row.get('next_action')}")
        print(f"founder_click: {row.get('founder_click')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
