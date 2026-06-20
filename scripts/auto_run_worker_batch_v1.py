#!/usr/bin/env python3
"""Fully automatic Goal 1 worker batch — no Hub taps.

Triggers batch when hub is up, queue has work, and no batch is running.
Law: brain-os/laws/AUTO_RUN_FULLY_AUTOMATIC_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
LOCK_PATH = Path.home() / ".sina" / "goal1-worker-batch-lock-v1.json"
STATE_PATH = Path.home() / ".sina" / "auto-run-worker-batch-v1.json"
LOG_PATH = Path.home() / ".sina" / "auto-run-worker-batch-runs.jsonl"
HUB_HEALTH = "http://127.0.0.1:13020/health"
DEFAULT_BATCH_SIZE = 5
DEFAULT_MAX_BATCHES = 6
POLL_SEC = 30


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _save_state(row: dict) -> None:
    STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def hub_healthy() -> bool:
    try:
        with urllib.request.urlopen(HUB_HEALTH, timeout=3) as resp:
            body = json.loads(resp.read().decode("utf-8"))
            return bool(body.get("ok"))
    except (urllib.error.URLError, OSError, json.JSONDecodeError, TimeoutError):
        return False


def batch_busy() -> dict:
    if not LOCK_PATH.is_file():
        return {"busy": False}
    try:
        row = json.loads(LOCK_PATH.read_text(encoding="utf-8"))
        pid = int(row.get("pid") or 0)
        if pid and _pid_alive(pid):
            return {"busy": True, "pid": pid, "since": row.get("at")}
        LOCK_PATH.unlink(missing_ok=True)
        return {"busy": False, "cleared_stale": True}
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        return {"busy": False}


def _broker_state() -> dict:
    path = Path.home() / ".sina" / "goal1-lane-broker-v1.json"
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _queue_remaining() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from worker_drain_lib import healthy_queue_status  # noqa: WPS433

    st = healthy_queue_status()
    if not st.get("ok"):
        return {"ok": False, "error": st.get("error")}
    pos = int(st.get("queue_pos") or 1)
    total = int(st.get("queue_total") or 30)
    return {
        "ok": True,
        "pos": pos,
        "total": total,
        "remaining": max(0, total - pos + 1),
        "sa_id": st.get("sa_id"),
        "queue_role": st.get("queue_role"),
    }


def _autorun_disabled() -> bool:
    if os.environ.get("SINA_AUTORUN_DISABLED", "").strip().lower() in ("1", "true", "yes"):
        return True
    flag = Path.home() / ".sina" / "auto-run-disabled-v1.flag"
    return flag.is_file()


def _clear_checkpoint_pause() -> dict:
    st = _broker_state()
    if st.get("status") != "checkpoint_pending":
        return {"ok": True, "skipped": True}
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "goal1_lane_broker.py"), "brain-checkpoint-ack", "--note", "autorun"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=60,
    )
    return {"ok": proc.returncode == 0, "stdout": (proc.stdout or "")[-500:]}


def _orchestrator_status() -> str:
    orch_path = Path.home() / ".sina" / "healthy-drain-orchestrator-v1.json"
    if not orch_path.is_file():
        return ""
    try:
        return json.loads(orch_path.read_text(encoding="utf-8")).get("status") or ""
    except (OSError, json.JSONDecodeError):
        return ""


def _inbox_pending() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import inbox_status  # noqa: WPS433

    inbox = inbox_status()
    if inbox.get("pending"):
        return {"pending": True, "inbox": inbox}
    return {"pending": False}


def run_stuck_watchdog(*, caller: str = "autorun") -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from goal1_stuck_watchdog_v1 import run_watchdog  # noqa: WPS433

    return run_watchdog(max_age_sec=300, caller=caller)


def should_start_batch(*, caller: str = "autorun") -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import check_autorun_allowed  # noqa: WPS433

    an = check_autorun_allowed(caller=f"{caller}:should_start")
    if not an.get("ok"):
        return {**an, "action": "skip", "reason": an.get("reason", "ACTIVE_NOW_AUTORUN_OFF")}

    if _autorun_disabled():
        return {"ok": False, "action": "skip", "reason": "AUTORUN_DISABLED"}

    sys.path.insert(0, str(SCRIPTS))
    from agent_cancel_guard_v1 import agent_cancel_active, agent_cancel_skip, write_cancel_receipt  # noqa: WPS433

    if agent_cancel_active():
        write_cancel_receipt(caller=f"{caller}:should_start")
        return agent_cancel_skip(caller=f"{caller}:should_start")

    # In API mode, hub is optional — batches run headlessly without it
    api_mode = bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())
    if not api_mode and not hub_healthy():
        return {"ok": False, "action": "wait", "reason": "HUB_DOWN"}

    stuck = run_stuck_watchdog(caller=f"{caller}_preflight")
    if stuck.get("killed"):
        _log({"event": "stuck_watchdog_killed", "stuck": stuck, "caller": caller})

    busy = batch_busy()
    if busy.get("busy"):
        return {"ok": False, "action": "skip", "reason": "WORKER_BATCH_BUSY", **busy}

    inbox_gate = _inbox_pending()
    if inbox_gate.get("pending"):
        return {
            "ok": False,
            "action": "skip",
            "reason": "INBOX_PENDING",
            "inbox_sa": (inbox_gate.get("inbox") or {}).get("sa_id"),
        }

    orch_status = _orchestrator_status()
    if orch_status == "awaiting_worker":
        return {"ok": False, "action": "skip", "reason": "AWAITING_WORKER"}

    # API mode: skip ALL Cursor/window checks — no UI required
    api_mode = bool(os.environ.get("ANTHROPIC_API_KEY", "").strip())
    if not api_mode:
        sys.path.insert(0, str(SCRIPTS))
        from cursor_window_preflight_v1 import run_worker_chat_preflight  # noqa: WPS433

        preflight = run_worker_chat_preflight(caller=caller, sleep_sec=1.0)
        if not preflight.get("ok"):
            return {"ok": False, "action": "wait", "reason": "CURSOR_PREFLIGHT", "preflight": preflight}

        from prompt_feasibility_gate import check_session  # noqa: WPS433

        feas = check_session(role="worker")
        if feas.get("action") == "STOP_INJECT":
            return {"ok": False, "action": "wait", "reason": "FEASIBILITY_BLOCKED", "feasibility": feas}

    q = _queue_remaining()
    if not q.get("ok"):
        return {"ok": False, "action": "wait", "reason": "NO_QUEUE", **q}
    if int(q.get("remaining") or 0) <= 0:
        return {"ok": False, "action": "done", "reason": "QUEUE_COMPLETE", **q}

    from duplicate_inject_guard_v1 import check_skip_inject  # noqa: WPS433

    skip = check_skip_inject(
        meta={
            "sa_id": q.get("sa_id"),
            "queue_pos": q.get("pos"),
            "queue_total": q.get("total"),
            "queue_role": q.get("queue_role"),
        },
        source=caller,
    )
    if skip.get("skip"):
        return {"ok": False, "action": "skip", "reason": skip.get("reason"), "duplicate_guard": skip}

    orch_status = _orchestrator_status()
    if orch_status == "stopped":
        return {"ok": False, "action": "wait", "reason": "ORCHESTRATOR_STOPPED"}

    broker = _broker_state()
    if broker.get("status") == "checkpoint_pending":
        ack = _clear_checkpoint_pause()
        if not ack.get("ok"):
            return {"ok": False, "action": "wait", "reason": "CHECKPOINT_ACK_FAILED", **ack}

    # ACQUIRE INJECT LOCK before returning start — prevents duplicate spawns
    from duplicate_inject_guard_v1 import acquire_inject_lock  # noqa: WPS433
    acquire_inject_lock(
        meta={
            "sa_id": q.get("sa_id"),
            "queue_pos": q.get("pos"),
            "queue_total": q.get("total"),
            "queue_role": q.get("queue_role"),
        },
        source=caller,
    )

    return {"ok": True, "action": "start", "queue": q, "caller": caller}


def spawn_batch(
    *,
    batch_size: int = DEFAULT_BATCH_SIZE,
    max_batches: int = DEFAULT_MAX_BATCHES,
    caller: str = "autorun",
) -> dict:
    from factory_spawn_gate_v1 import drain_spawn_allowed  # noqa: WPS433

    spawn_gate = drain_spawn_allowed(caller="auto_run_worker_batch", require_bind=False)
    if not spawn_gate.get("ok"):
        return {"ok": False, "spawned": False, "gate": spawn_gate}
    gate = should_start_batch(caller=caller)
    if not gate.get("ok") or gate.get("action") != "start":
        return {"ok": False, "spawned": False, "gate": gate}

    env = {
        **os.environ,
        "SINA_WORKER_CHAT_RESUME_INJECT": "1",
        "SINA_AUTORUN_ENABLED": "1",
    }
    log_out = Path.home() / ".sina" / "goal1-worker-batch-latest.log"
    log_out.parent.mkdir(parents=True, exist_ok=True)
    with log_out.open("a", encoding="utf-8") as logfh:
        logfh.write(f"[{_now()}] AUTORUN spawn caller={caller}\n")
        proc = subprocess.Popen(
            [
                sys.executable,
                str(SCRIPTS / "goal1_worker_batch_loop_v1.py"),
                "--batch-size",
                str(batch_size),
                "--max-batches",
                str(max_batches),
            ],
            cwd=str(ROOT),
            stdout=logfh,
            stderr=subprocess.STDOUT,
            env=env,
            start_new_session=True,
        )
    row = {
        "ok": True,
        "spawned": True,
        "pid": proc.pid,
        "batch_size": batch_size,
        "max_batches": max_batches,
        "caller": caller,
        "gate": gate,
    }
    _log(row)
    _save_state({"last_spawn": row, "updated_at": _now()})
    return row


def schedule_after_batch(result: dict | None) -> None:
    """Called when a batch ends — kick autorun daemon to start next batch."""
    _log({"event": "batch_finished", "result_status": (result or {}).get("status")})
    _save_state(
        {
            "last_batch_result": result or {},
            "schedule_kick_at": _now(),
            "updated_at": _now(),
        }
    )
    uid = os.getuid()
    plist = Path.home() / "Library/LaunchAgents/com.sourcea.autorun-worker.plist"
    label = "com.sourcea.autorun-worker"
    subprocess.run(
        ["launchctl", "kickstart", "-k", f"gui/{uid}/{label}"],
        capture_output=True,
        timeout=15,
        check=False,
    )
    # Also try immediate spawn if idle (no wait for daemon poll).
    time.sleep(2.0)
    spawn_batch(caller="after_batch")


def run_daemon(*, poll_sec: int = POLL_SEC) -> int:
    _save_state({"mode": "daemon", "started_at": _now(), "poll_sec": poll_sec})
    while True:
        if not _autorun_disabled():
            run_stuck_watchdog(caller="daemon_poll")
            row = spawn_batch(caller="daemon_poll")
            if not row.get("spawned"):
                _save_state({"last_poll": row, "updated_at": _now()})
        time.sleep(max(10, poll_sec))


def main() -> int:
    p = argparse.ArgumentParser(description="Automatic Goal 1 worker batch (no Hub taps)")
    p.add_argument("--daemon", action="store_true", help="Poll and spawn batches (launchd)")
    p.add_argument("--once", action="store_true", help="Single evaluate+spawn")
    p.add_argument("--poll-sec", type=int, default=POLL_SEC)
    p.add_argument("--batch-size", type=int, default=DEFAULT_BATCH_SIZE)
    p.add_argument("--max-batches", type=int, default=DEFAULT_MAX_BATCHES)
    p.add_argument("--status", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.status:
        out = {
            "hub_healthy": hub_healthy(),
            "batch": batch_busy(),
            "should": should_start_batch(),
            "state_path": str(STATE_PATH),
            "disabled": _autorun_disabled(),
        }
        if args.json:
            print(json.dumps(out, indent=2))
        else:
            print(json.dumps(out, indent=2))
        return 0

    if args.daemon:
        return run_daemon(poll_sec=args.poll_sec)

    row = spawn_batch(batch_size=args.batch_size, max_batches=args.max_batches, caller="cli_once" if args.once else "autorun")
    if args.json or not args.once:
        print(json.dumps(row, indent=2))
    return 0 if row.get("spawned") else 1


if __name__ == "__main__":
    raise SystemExit(main())
