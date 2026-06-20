#!/usr/bin/env python3
"""Gather every Brain rule source from disk — unified inventory for ASF."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRAIN_OS = ROOT / "brain-os"

BRAIN_CURSOR_RULES = [
    ".cursor/rules/000-cross-lane-edit-forbidden.mdc",
    ".cursor/rules/000-brain-unified.mdc",
    ".cursor/rules/000-entry-gate.mdc",
    ".cursor/rules/agent-disk-live-wire-first.mdc",
    ".cursor/rules/agent-memory-mirror.mdc",
    ".cursor/rules/agent-daily-duty-card.mdc",
    ".cursor/rules/agent-loop.mdc",
    ".cursor/rules/000-workspace-lock.mdc",
    ".cursor/rules/sina-governance-entry.mdc",
    ".cursor/rules/agent-smart-judgment.mdc",
    ".cursor/rules/sina-command-readonly.mdc",
]

DELETED_SICK_RULES = [
    ".cursor/rules/000-brain-narrate-only.mdc",
    ".cursor/rules/brain-not-worker.mdc",
    ".cursor/rules/goal1-loop-activation.mdc",
    "os/chat-handoffs/BRAIN_RUN_LOOP_SIMPLE_LOCKED_v1.md",
    "os/chat-handoffs/BRAIN_NARRATE_NOT_EXECUTE_LOCKED_v1.md",
    "os/chat-handoffs/BRAIN_TIMING_ENFORCEMENT_LOCKED_v1.md",
]

BRAIN_LOCKED_DOCS = [
    "brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md",
    "brain-os/contract/BRAIN_HEAL_PROMPT_LOCKED_v1.md",
    "brain-os/contract/MANDATORY_BRAIN_CHAT_LOCKED_v1.md",
    "brain-os/law/BRAIN_RULES_AUTHORITY_INDEX_LOCKED_v1.md",
    "brain-os/contract/BRAIN_CORE_EXECUTOR_LOCKED_v1.md",
    "brain-os/law/enforcement/BRAIN_DISK_BEFORE_CHAT_SESSION_LOOP_LOCKED_v1.md",
    "brain-os/law/enforcement/GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md",
    "brain-os/law/enforcement/GOAL1_EXECUTION_SOLUTION_LOCKED_v1.md",
    "brain-os/law/enforcement/BRAIN_ENFORCEMENT_AUDIT_PROMPT_LOCKED_v1.md",
    "brain-os/incidents/SINA_BRAIN_WORKER_LANE_CROSS_INCIDENT_LOCKED_v1.md",
    "brain-os/incidents/SINA_CROSS_LANE_EDIT_FORBIDDEN_INCIDENT_LOCKED_v1.md",
    "brain-os/law/enforcement/AGENT_VERBS_SAVE_WORK_EDIT_LOCKED_v1.md",
    "brain-os/law/SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md",
    "brain-os/incidents/SINA_GOAL1_LOOP_UNVALIDATED_PROOF_INCIDENT_LOCKED_v1.md",
    "brain-os/law/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md",
    "brain-os/INDEX_LOCKED_v1.md",
]

BRAIN_SCRIPTS = [
    "scripts/brain-session-start.sh",
    "scripts/brain_run_loop_trace_v1.py",
    "scripts/brain_narrate_loop_v1.py",
    "scripts/brain_intent_gate_v1.py",
    "scripts/brain_gather_rules_v1.py",
    "scripts/brain_run_loop_v1.py",
    "scripts/brain_execute_turn_v1.py",
    "scripts/brain_validate_goal1_v1.py",
    "scripts/cursor_entry_gate.py",
    "scripts/brain_os_paths.py",
]


def _row(path: str) -> dict:
    p = ROOT / path
    if not p.is_file():
        return {"path": path, "exists": False}
    st = p.stat()
    return {
        "path": path,
        "exists": True,
        "bytes": st.st_size,
        "mtime": datetime.fromtimestamp(st.st_mtime, tz=timezone.utc).isoformat(),
    }


def gather() -> dict:
    deleted_still_present = [p for p in DELETED_SICK_RULES if (ROOT / p).is_file()]
    return {
        "status": "BRAIN_RULES_GATHER",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "brain_os_root": str(BRAIN_OS),
        "ssot": "brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md",
        "index": "brain-os/INDEX_LOCKED_v1.md",
        "cursor_ssot": ".cursor/rules/000-brain-unified.mdc",
        "heal_prompt": "brain-os/contract/BRAIN_HEAL_PROMPT_LOCKED_v1.md",
        "deleted_sick_rules": DELETED_SICK_RULES,
        "deleted_sick_still_on_disk": deleted_still_present,
        "healthy": len(deleted_still_present) == 0,
        "cursor_rules_active": [_row(p) for p in BRAIN_CURSOR_RULES],
        "locked_docs": [_row(p) for p in BRAIN_LOCKED_DOCS],
        "scripts": [_row(p) for p in BRAIN_SCRIPTS],
        "decision_tree": {
            "run_trace": "brain_run_loop_trace_v1.py",
            "narrate_only": "brain_narrate_loop_v1.py",
            "spawn": "brain_run_loop_v1.py / brain_execute_turn_v1.py",
            "refuse": "BRAIN_REFUSE_WORKER_PROMPT",
            "session": "brain-session-start.sh",
        },
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out = gather()
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"status: {out['status']}")
        print(f"healthy: {out['healthy']}")
        print(f"ssot: {out['ssot']}")
        if out["deleted_sick_still_on_disk"]:
            print(f"WARN sick still present: {out['deleted_sick_still_on_disk']}")
    return 1 if not out["healthy"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
