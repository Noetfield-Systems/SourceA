#!/usr/bin/env python3
"""Kill stuck Goal 1 / brain_run_loop processes older than max_age_sec.

Law: brain-os/laws/NO_DUPLICATE_INJECT_LOCKED_v1.md (watchdog section)
"""
from __future__ import annotations

import json
import os
import re
import signal
import subprocess
from datetime import datetime, timezone
from pathlib import Path

LOG_PATH = Path.home() / ".sina" / "goal1-stuck-watchdog-v1.jsonl"
PROGRESS_PATH = Path.home() / ".sina" / "goal1-turn-progress-v1.json"
BATCH_LOCK = Path.home() / ".sina" / "goal1-worker-batch-lock-v1.json"
DEFAULT_MAX_AGE_SEC = 300

STUCK_MARKERS = (
    "goal1_worker_batch_loop_v1.py",
    "start_goal1_worker_turn_v1.py",
    "goal1_run_loop_v1.py",
    "goal1_brain_loop_driver.py",
    "brain_run_loop",
    "auto_run_worker_batch_v1.py",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with LOG_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _parse_etime(etime: str) -> int | None:
    """Parse ps etime to seconds."""
    etime = (etime or "").strip()
    if not etime:
        return None
    if re.match(r"^\d+:\d{2}$", etime):
        m, s = etime.split(":")
        return int(m) * 60 + int(s)
    if re.match(r"^\d+:\d{2}:\d{2}$", etime):
        h, m, s = etime.split(":")
        return int(h) * 3600 + int(m) * 60 + int(s)
    if "-" in etime:
        day_part, rest = etime.split("-", 1)
        try:
            days = int(day_part)
        except ValueError:
            return None
        if rest.count(":") == 2:
            h, m, s = rest.split(":")
            return days * 86400 + int(h) * 3600 + int(m) * 60 + int(s)
        if rest.count(":") == 1:
            m, s = rest.split(":")
            return days * 86400 + int(m) * 60 + int(s)
    return None


def _list_processes() -> list[dict]:
    proc = subprocess.run(
        ["ps", "-axo", "pid=,etime=,command="],
        capture_output=True,
        text=True,
        timeout=15,
    )
    rows: list[dict] = []
    for line in (proc.stdout or "").splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split(None, 2)
        if len(parts) < 3:
            continue
        pid_s, etime, cmd = parts[0], parts[1], parts[2]
        try:
            pid = int(pid_s)
        except ValueError:
            continue
        age = _parse_etime(etime)
        rows.append({"pid": pid, "etime": etime, "age_sec": age, "command": cmd})
    return rows


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _kill_pid(pid: int) -> dict:
    try:
        os.kill(pid, signal.SIGTERM)
        return {"pid": pid, "signal": "SIGTERM", "ok": True}
    except OSError as exc:
        return {"pid": pid, "ok": False, "error": str(exc)}


def _clear_stale_batch_lock(killed_pids: list[int]) -> dict:
    if not BATCH_LOCK.is_file():
        return {"cleared": False}
    try:
        row = json.loads(BATCH_LOCK.read_text(encoding="utf-8"))
        pid = int(row.get("pid") or 0)
        if pid in killed_pids or (pid and not _pid_alive(pid)):
            BATCH_LOCK.unlink(missing_ok=True)
            return {"cleared": True, "pid": pid}
    except (OSError, json.JSONDecodeError, ValueError, TypeError):
        BATCH_LOCK.unlink(missing_ok=True)
        return {"cleared": True, "reason": "corrupt_lock"}
    return {"cleared": False}


def _reset_stale_progress() -> dict:
    if not PROGRESS_PATH.is_file():
        return {"reset": False}
    try:
        row = json.loads(PROGRESS_PATH.read_text(encoding="utf-8"))
        if row.get("status") != "RUNNING":
            return {"reset": False}
        row["status"] = "STUCK_KILLED"
        row["stuck_killed_at"] = _now()
        PROGRESS_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        return {"reset": True, "sa_id": row.get("sa_id")}
    except (OSError, json.JSONDecodeError):
        return {"reset": False}


def run_watchdog(*, max_age_sec: int = DEFAULT_MAX_AGE_SEC, caller: str = "watchdog") -> dict:
    """Find and kill stuck goal1 processes; log STUCK events."""
    killed: list[dict] = []
    candidates: list[dict] = []
    for row in _list_processes():
        cmd = row.get("command") or ""
        if not any(m in cmd for m in STUCK_MARKERS):
            continue
        age = row.get("age_sec")
        if age is None or age < max_age_sec:
            continue
        if row["pid"] == os.getpid():
            continue
        candidates.append(row)

    for row in candidates:
        result = _kill_pid(row["pid"])
        event = {
            "event": "STUCK_PROCESS_KILLED",
            "caller": caller,
            "pid": row["pid"],
            "age_sec": row.get("age_sec"),
            "etime": row.get("etime"),
            "command": row.get("command"),
            "kill": result,
            "max_age_sec": max_age_sec,
        }
        _log(event)
        if result.get("ok"):
            killed.append(event)

    lock_clear = _clear_stale_batch_lock([k["pid"] for k in killed])
    progress_reset = _reset_stale_progress() if killed else {"reset": False}

    out = {
        "ok": True,
        "caller": caller,
        "max_age_sec": max_age_sec,
        "candidates": len(candidates),
        "killed": len(killed),
        "events": killed,
        "batch_lock": lock_clear,
        "progress": progress_reset,
        "retry_hint": "autorun will retry turn on next poll" if killed else None,
    }
    if killed:
        _log({"event": "STUCK_WATCHDOG_SUMMARY", **out})
    return out


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Goal 1 stuck process watchdog")
    p.add_argument("--max-age-sec", type=int, default=DEFAULT_MAX_AGE_SEC)
    p.add_argument("--caller", default="cli")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = run_watchdog(max_age_sec=args.max_age_sec, caller=args.caller)
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
