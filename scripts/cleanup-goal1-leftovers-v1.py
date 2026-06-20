#!/usr/bin/env python3
"""Kill Goal 1 / overnight / API / CLI leftovers — zero orphan processes.

Law: brain-os/laws/BRAIN_NO_LEFTOVER_PROCESS_LOCKED_v1.md
Brain: end every turn with `python3 scripts/cleanup-goal1-leftovers-v1.py --json`
Hub: Actions → Stop Goal 1 executor (stop_goal1_auto_run_v1.py) calls this.
"""
from __future__ import annotations

import json
import os
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
ROOT = Path(__file__).resolve().parents[1]

# Long-running or orphaned children Brain/overnight leaves behind
LEFTOVER_PATTERNS = (
    "validate-sourcea-e2e-full-v1.sh",
    "audit_backend_e2e.py",
    "start-overnight-3engine-v1.sh",
    "autorun_dispatcher_v1.py",
    "claude_api_agent_v1.py",
    "claude_code_agent_v1.py",
    "goal1_worker_batch_loop_v1.py",
    "goal1_auto_run_deliver_v1.py",
    "goal1_auto_loop_v1.py",
    "goal1_auto_run_v1.py",
    "goal1_run_loop",
    "brain_execute_turn_v1.py",
    "start_goal1_worker_turn_v1.py",
    "start-sidecar-engines-watch",
    "agent -p -f",
    "agent.*INBOX TURN",
    "SourceA Worker",
    "claude -p You are SourceA Worker",
)

PID_FILES = (
    SINA / "overnight-3engine-v1.pid",
    SINA / "sidecar-engines-watch-v1.pid",
)

LOCK_FILES = (
    SINA / "single-boss-loop-v1.json",
    SINA / "brain-executor-lock-v1.json",
    SINA / "goal1-worker-batch-lock-v1.json",
    SINA / "goal1-auto-run-lock-v1.json",
    SINA / "goal1-auto-loop-lock-v1.json",
    SINA / "goal1-inject-lock-v1.json",
    SINA / "goal1-worker-turn-bind-v1.json",
)

KILL_FLAG = SINA / "auto-run-disabled-v1.flag"
API_OFF_FLAG = SINA / "api-disabled-v1.flag"
CLI_OFF_FLAG = SINA / "cli-disabled-v1.flag"
MANUAL_WORKER_FLAG = SINA / "worker-manual-only-v1.flag"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pids_for_pattern(pattern: str) -> list[int]:
    proc = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
    out: list[int] = []
    me = os.getpid()
    for line in (proc.stdout or "").splitlines():
        if line.strip().isdigit():
            pid = int(line.strip())
            if pid != me:
                out.append(pid)
    return out


def _kill_tree(pids: list[int]) -> list[int]:
    killed: list[int] = []
    for pid in pids:
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append(pid)
        except OSError:
            pass
    if killed:
        time.sleep(0.6)
    for pid in list(killed):
        try:
            os.kill(pid, 0)
            os.kill(pid, signal.SIGKILL)
        except OSError:
            pass
    return killed


def _protected_validation_pids() -> set[int]:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "factory_validation_lock_v1",
        ROOT / "scripts" / "factory_validation_lock_v1.py",
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod.protected_validation_pids()


def cleanup(*, set_kill_flag: bool = True, reset_orchestrator: bool = True) -> dict:
    protected = _protected_validation_pids()
    all_pids: set[int] = set()
    labels: list[str] = []
    skipped: list[str] = []
    for pat in LEFTOVER_PATTERNS:
        for pid in _pids_for_pattern(pat):
            if pid in protected:
                skipped.append(f"{pat}:{pid}")
                continue
            all_pids.add(pid)
            labels.append(f"{pat}:{pid}")

    killed = _kill_tree(sorted(all_pids))

    for pf in PID_FILES:
        pf.unlink(missing_ok=True)
    for lf in LOCK_FILES:
        lf.unlink(missing_ok=True)

    if set_kill_flag:
        KILL_FLAG.parent.mkdir(parents=True, exist_ok=True)
        KILL_FLAG.touch()
        API_OFF_FLAG.touch()
        CLI_OFF_FLAG.touch()
        MANUAL_WORKER_FLAG.unlink(missing_ok=True)

    orch_reset = None
    if reset_orchestrator:
        try:
            proc = subprocess.run(
                [sys.executable, str(ROOT / "scripts/healthy-drain-orchestrator-v1.py"), "reset"],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=str(ROOT),
            )
            orch_reset = proc.returncode == 0
        except (OSError, subprocess.TimeoutExpired):
            orch_reset = False

    remaining: list[int] = []
    for pat in LEFTOVER_PATTERNS:
        for pid in _pids_for_pattern(pat):
            if pid not in protected:
                remaining.append(pid)
    remaining = sorted(set(remaining))

    return {
        "ok": len(remaining) == 0,
        "schema": "cleanup-goal1-leftovers-v1",
        "at": _now(),
        "killed_count": len(killed),
        "killed_sample": labels[:40],
        "skipped_protected": skipped[:40],
        "protected_pids": sorted(protected)[:40],
        "remaining_count": len(remaining),
        "remaining_pids": remaining[:20],
        "kill_flag": set_kill_flag and KILL_FLAG.is_file(),
        "orchestrator_reset": orch_reset,
        "message": (
            "CLEAN — no leftovers"
            if not remaining
            else f"WARNING — {len(remaining)} process(es) still running"
        ),
    }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Kill Goal1/overnight/API/CLI leftovers")
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-kill-flag", action="store_true", help="Kill procs only; do not touch kill flag")
    p.add_argument("--no-orchestrator-reset", action="store_true")
    args = p.parse_args()
    row = cleanup(
        set_kill_flag=not args.no_kill_flag,
        reset_orchestrator=not args.no_orchestrator_reset,
    )
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
