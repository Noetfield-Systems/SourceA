#!/usr/bin/env python3
"""Brain Core Executor — Goal 1 turn (one at a time).

Brain IS the executor for Goal 1 loop control:
  deliver INBOX (if needed) → agent CLI turn → broker → YAML back to Brain

NOT Worker chat paste. NOT fake fast_loop. ONE turn per invocation (no 9min shell hang).

Law: BRAIN_CORE_EXECUTOR_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LOCK_PATH = Path.home() / ".sina" / "brain-executor-lock-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def _pid_alive(pid: int) -> bool:
    try:
        import os

        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _read_lock() -> dict:
    if not LOCK_PATH.is_file():
        return {}
    try:
        return json.loads(LOCK_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def acquire_executor_lock() -> dict:
    """One Brain executor at a time — prevents Hub+Brain double-run hang."""
    row = _read_lock()
    pid = row.get("pid")
    if pid and _pid_alive(int(pid)):
        return {
            "ok": False,
            "error": "BRAIN_EXECUTOR_BUSY",
            "busy_pid": pid,
            "since": row.get("at"),
            "hint": "Wait for current turn or Hub → Stop Goal 1 executor",
        }
    LOCK_PATH.parent.mkdir(parents=True, exist_ok=True)
    LOCK_PATH.write_text(
        json.dumps({"pid": os.getpid(), "at": _now(), "script": "brain_execute_turn_v1.py"}, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"ok": True}


def release_executor_lock() -> None:
    row = _read_lock()
    if row.get("pid") == os.getpid():
        LOCK_PATH.unlink(missing_ok=True)


def executor_lock_status() -> dict:
    row = _read_lock()
    pid = row.get("pid")
    busy = bool(pid and _pid_alive(int(pid)))
    return {"busy": busy, "pid": pid if busy else None, "since": row.get("at"), "script": row.get("script")}


def execute_one_turn(*, deliver_first: bool = True, timeout_sec: int = 1800) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import inbox_status  # noqa: WPS433

    inbox = inbox_status()
    if deliver_first and not inbox.get("pending"):
        from worker_drain_lib import healthy_drain_paste  # noqa: WPS433

        d = healthy_drain_paste()
        if not d.get("ok"):
            return {"ok": False, "step": "deliver", "error": d}

    start = _load_module("start", SCRIPTS / "start_goal1_worker_turn_v1.py")
    turn = start.run_turn(dry_run=False, timeout_sec=timeout_sec)
    if not turn.get("ok"):
        return {"ok": False, "step": "agent_turn", "result": turn}

    broker = _load_module("broker", SCRIPTS / "goal1_lane_broker.py")
    poll = broker.brain_poll(as_yaml=False)

    bval = _load_module("bval", SCRIPTS / "brain_validate_goal1_v1.py")
    validation = bval.validate_goal1()
    validation_path = Path.home() / ".sina" / "brain-goal1-validation-v1.json"
    validation_path.write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")

    ack = None
    if (poll.get("broker") or {}).get("state") == "awaiting_brain_ack" or poll.get("brain_inbox_pending_ack"):
        ack = broker.brain_ack(note="brain_core_executor")

    return {
        "ok": True,
        "status": "BRAIN_EXECUTOR_TURN_COMPLETE",
        "at": _now(),
        "turn": {
            "sa_id": turn.get("sa_id"),
            "queue_role": turn.get("queue_role"),
            "broker": turn.get("broker"),
        },
        "poll": poll,
        "validation": validation,
        "ack": ack is not None,
        "founder_action": "Batch log AGENT DONE — hub auto-syncs",
    }


def execute_loop(*, max_turns: int = 1, timeout_sec: int = 1800) -> dict:
    """Max 5 turns per call — Brain chat must not run 25 in one shell."""
    cap = min(max(1, max_turns), 5)
    rows = []
    for i in range(cap):
        row = execute_one_turn(deliver_first=(i == 0), timeout_sec=timeout_sec)
        rows.append(row)
        if not row.get("ok"):
            break
        poll = row.get("poll") or {}
        if not (poll.get("inbox") or {}).get("pending") and poll.get("action") == "idle_or_deliver":
            break
    return {
        "ok": all(r.get("ok") for r in rows),
        "status": "BRAIN_EXECUTOR_LOOP",
        "turns_run": len(rows),
        "turns": rows,
    }


def to_yaml_report(result: dict) -> str:
    lines = [f"status: {result.get('status', 'BRAIN_EXECUTOR')}", f"at: {_now()}", f"ok: {result.get('ok')}"]
    if result.get("turn"):
        t = result["turn"]
        lines.append(f"sa_id: {t.get('sa_id')}")
        lines.append(f"broker_ok: {(t.get('broker') or {}).get('ok')}")
    if result.get("poll"):
        p = result["poll"]
        ib = p.get("inbox") or {}
        lines.append(f"inbox_pending: {ib.get('pending')}")
        lines.append(f"next_sa: {ib.get('sa_id')}")
        lines.append(f"queue: {ib.get('queue')}")
    lines.append(f"action: {result.get('founder_action', 'execute turn')}")
    val = result.get("validation") or {}
    if val:
        ch = val.get("chain") or {}
        lines.append("validation:")
        lines.append(f"  inject: {ch.get('inject')}")
        lines.append(f"  validate: {ch.get('validate')}")
        lines.append(f"  activate: {ch.get('activate')}")
        lines.append(f"  sync: {ch.get('sync')}")
        wr = val.get("worker_report") or {}
        lines.append(f"  worker_sa: {wr.get('sa_focus')}")
        lines.append(f"  spine: {(wr.get('validate') or {}).get('spine')}")
    return "\n".join(lines)


def main() -> int:
    p = argparse.ArgumentParser(description="Brain Core Executor — Goal 1")
    p.add_argument("--loop", type=int, default=1, metavar="N", help="Turns (max 5)")
    p.add_argument("--yaml", action="store_true")
    p.add_argument("--timeout", type=int, default=1800)
    p.add_argument("--status", action="store_true", help="Print lock status only")
    args = p.parse_args()

    if args.status:
        print(json.dumps(executor_lock_status(), indent=2))
        return 0

    sys.path.insert(0, str(SCRIPTS))
    from brain_intent_gate_v1 import refuse_if_narrate_lock  # noqa: WPS433

    blocked = refuse_if_narrate_lock("brain_execute_turn_v1.py")
    if blocked:
        print(json.dumps(blocked, indent=2))
        return 1

    batch_lock_path = Path.home() / ".sina" / "goal1-worker-batch-lock-v1.json"
    if batch_lock_path.is_file():
        try:
            row = json.loads(batch_lock_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            row = {}
        pid = row.get("pid")
        if pid and _pid_alive(int(pid)):
            busy = {"ok": False, "error": "WORKER_BATCH_RUNNING", "busy_pid": pid, "hint": "Hub batch active — use Stop not brain_execute"}
            print(json.dumps(busy, indent=2) if not args.yaml else f"status: WORKER_BATCH_RUNNING\npid: {pid}")
            return 2

    lock = acquire_executor_lock()
    if not lock.get("ok"):
        if args.yaml:
            print(f"status: BRAIN_EXECUTOR_BUSY\nerror: {lock.get('error')}\npid: {lock.get('busy_pid')}")
        else:
            print(json.dumps(lock, indent=2))
        return 2

    try:
        if args.loop <= 1:
            result = execute_one_turn(timeout_sec=args.timeout)
        else:
            result = execute_loop(max_turns=args.loop, timeout_sec=args.timeout)
    finally:
        release_executor_lock()

    if args.yaml:
        print(to_yaml_report(result))
    else:
        print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
