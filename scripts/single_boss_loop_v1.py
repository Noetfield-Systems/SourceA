#!/usr/bin/env python3
"""ONE boss loop at a time — overnight OR sidecar OR worker batch, never two."""
from __future__ import annotations

import json
import os
import signal
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
LOCK = SINA / "single-boss-loop-v1.json"
OVERNIGHT_PID = SINA / "overnight-3engine-v1.pid"
SIDECAR_PID = SINA / "sidecar-engines-watch-v1.pid"

OTHER_PATTERNS = {
    "overnight": ("start-sidecar-engines-watch", "goal1_worker_batch_loop_v1.py", "goal1_auto_loop"),
    "sidecar": ("start-overnight-3engine-v1.sh", "autorun_dispatcher_v1.py", "goal1_worker_batch_loop_v1.py"),
    "worker_batch": ("start-overnight-3engine-v1.sh", "autorun_dispatcher_v1.py", "start-sidecar-engines-watch"),
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read() -> dict:
    if not LOCK.is_file():
        return {}
    try:
        return json.loads(LOCK.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _kill_pattern(pattern: str) -> list[int]:
    proc = subprocess.run(["pgrep", "-f", pattern], capture_output=True, text=True)
    me = os.getpid()
    killed: list[int] = []
    for line in (proc.stdout or "").splitlines():
        if not line.strip().isdigit():
            continue
        pid = int(line.strip())
        if pid == me:
            continue
        try:
            os.kill(pid, signal.SIGTERM)
            killed.append(pid)
        except OSError:
            pass
    return killed


def kill_competing_loops(*, mode: str) -> list[int]:
    killed: list[int] = []
    for pat in OTHER_PATTERNS.get(mode, ()):
        killed.extend(_kill_pattern(pat))
    if killed:
        time.sleep(0.5)
    for pf in (SIDECAR_PID, OVERNIGHT_PID):
        try:
            if pf.is_file() and mode != "overnight" and pf == OVERNIGHT_PID:
                continue
            if pf.is_file() and mode != "sidecar" and pf == SIDECAR_PID:
                pf.unlink(missing_ok=True)
        except OSError:
            pass
    return sorted(set(killed))


def claim(*, mode: str, pid: int | None = None, kill_others: bool = True) -> dict:
    cur = _read()
    holder = cur.get("mode")
    holder_pid = int(cur.get("pid") or 0)
    if holder and holder != mode and holder_pid and _pid_alive(holder_pid):
        if not kill_others:
            return {"ok": False, "reason": "boss_loop_held", "holder": cur}
        kill_competing_loops(mode=mode)

    killed = kill_competing_loops(mode=mode) if kill_others else []
    row = {
        "schema": "single-boss-loop-v1",
        "mode": mode,
        "pid": pid or os.getpid(),
        "claimed_at": _now(),
        "killed_pids": killed,
    }
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "claimed": row}


def check_exclusive(*, mode: str) -> dict:
    cur = _read()
    holder = cur.get("mode")
    holder_pid = int(cur.get("pid") or 0)
    if holder and holder != mode and holder_pid and _pid_alive(holder_pid):
        return {"ok": False, "reason": "other_boss_loop_active", "holder": cur}
    return {"ok": True, "mode": mode}


def release(*, mode: str) -> dict:
    cur = _read()
    if cur.get("mode") == mode:
        LOCK.unlink(missing_ok=True)
    return {"ok": True, "released": mode}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=("claim", "check", "release", "status", "kill-others"))
    p.add_argument("--mode", default="overnight")
    p.add_argument("--pid", type=int, default=0)
    p.add_argument("--no-kill", action="store_true")
    args = p.parse_args()

    if args.cmd == "status":
        print(json.dumps({"lock": _read()}, indent=2))
        return 0
    if args.cmd == "claim":
        print(json.dumps(claim(mode=args.mode, pid=args.pid or None, kill_others=not args.no_kill), indent=2))
        return 0
    if args.cmd == "check":
        row = check_exclusive(mode=args.mode)
        print(json.dumps(row, indent=2))
        return 0 if row.get("ok") else 1
    if args.cmd == "release":
        print(json.dumps(release(mode=args.mode), indent=2))
        return 0
    print(json.dumps({"killed": kill_competing_loops(mode=args.mode)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
