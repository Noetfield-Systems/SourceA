#!/usr/bin/env python3
"""Factory validation mutex — serialize full E2E, goal1 E2E, strict build.

Prevents overlapping queue/shell churn (CIR-E2E race class).
Lock: ~/.sina/factory-validation-lock-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

LOCK = Path.home() / ".sina" / "factory-validation-lock-v1.json"
DEFAULT_TTL_SEC = 7200
PROTECTED_HOLDERS = frozenset({"full_e2e", "goal1_e2e"})

GOAL1_LOCKS = (
    Path.home() / ".sina" / "goal1-auto-run-lock-v1.json",
    Path.home() / ".sina" / "goal1-auto-loop-lock-v1.json",
    Path.home() / ".sina" / "goal1-worker-batch-lock-v1.json",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def _load() -> dict | None:
    if not LOCK.is_file():
        return None
    try:
        row = json.loads(LOCK.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def _goal1_busy() -> dict | None:
    for path in GOAL1_LOCKS:
        if not path.is_file():
            continue
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
            pid = int(row.get("pid") or 0)
            if pid and _pid_alive(pid):
                return {"holder": path.name, "pid": pid, "since": row.get("at"), "path": str(path)}
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            continue
    return None


def _stale(row: dict, ttl_sec: int) -> bool:
    pid = int(row.get("pid") or 0)
    if pid and not _pid_alive(pid):
        return True
    started = str(row.get("started_at") or row.get("at") or "")
    if not started:
        return False
    try:
        dt = datetime.fromisoformat(started.replace("Z", "+00:00"))
        age = (datetime.now(timezone.utc) - dt).total_seconds()
        return age > ttl_sec
    except ValueError:
        return False


def _write(row: dict) -> None:
    LOCK.parent.mkdir(parents=True, exist_ok=True)
    LOCK.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def sweep_stale_lock() -> dict:
    """Remove lock file when holder PID is dead or TTL exceeded."""
    row = _load()
    if not row:
        return {"ok": True, "swept": False, "reason": "no_lock"}
    ttl = int(row.get("ttl_sec") or DEFAULT_TTL_SEC)
    if not _stale(row, ttl):
        return {"ok": True, "swept": False, "reason": "lock_live", "holder": row.get("holder")}
    try:
        LOCK.unlink(missing_ok=True)
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
    return {
        "ok": True,
        "swept": True,
        "holder": row.get("holder"),
        "pid": row.get("pid"),
    }


def status() -> dict:
    sweep_stale_lock()
    row = _load()
    g1 = _goal1_busy()
    out: dict = {"ok": True, "locked": False, "lock_path": str(LOCK)}
    if row:
        out["locked"] = bool(row.get("holder")) and not _stale(row, int(row.get("ttl_sec") or DEFAULT_TTL_SEC))
        out["lock"] = row
        if _stale(row, int(row.get("ttl_sec") or DEFAULT_TTL_SEC)):
            out["locked"] = False
            out["stale"] = True
    if g1:
        out["goal1_busy"] = g1
    return out


def acquire(*, holder: str, pid: int | None = None, ttl_sec: int = DEFAULT_TTL_SEC) -> dict:
    holder = holder.strip()
    if not holder:
        return {"ok": False, "error": "holder required"}
    pid = pid or os.getpid()
    sweep_stale_lock()
    existing = _load()
    if existing and not _stale(existing, ttl_sec):
        ex_pid = int(existing.get("pid") or 0)
        ex_holder = str(existing.get("holder") or "")
        if ex_pid and _pid_alive(ex_pid) and ex_holder != holder:
            return {
                "ok": False,
                "error": "FACTORY_VALIDATION_LOCKED",
                "blocked_by": ex_holder,
                "blocked_pid": ex_pid,
                "since": existing.get("started_at") or existing.get("at"),
            }
    g1 = _goal1_busy()
    if g1 and holder in ("full_e2e", "goal1_e2e"):
        return {"ok": False, "error": "GOAL1_EXECUTOR_BUSY", **g1}
    row = {
        "schema": "factory-validation-lock-v1",
        "holder": holder,
        "pid": pid,
        "started_at": _now(),
        "ttl_sec": ttl_sec,
    }
    _write(row)
    return {"ok": True, "acquired": True, "holder": holder, "pid": pid}


def release(*, holder: str | None = None, pid: int | None = None) -> dict:
    row = _load()
    if not row:
        return {"ok": True, "released": False, "reason": "no_lock"}
    cur_pid = int(row.get("pid") or 0)
    cur_holder = str(row.get("holder") or "")
    pid = pid or os.getpid()
    if holder and cur_holder != holder:
        return {"ok": True, "released": False, "reason": "holder_mismatch", "lock_holder": cur_holder}
    if cur_pid and cur_pid != pid:
        return {"ok": True, "released": False, "reason": "pid_mismatch", "lock_pid": cur_pid}
    try:
        LOCK.unlink(missing_ok=True)
    except OSError as exc:
        return {"ok": False, "error": str(exc)}
    return {"ok": True, "released": True, "holder": cur_holder}


def _descendant_pids(root: int) -> set[int]:
    """All child PIDs under root (recursive) — protects E2E strict-build children."""
    out: set[int] = set()
    proc = subprocess.run(
        ["pgrep", "-P", str(root)],
        capture_output=True,
        text=True,
    )
    for line in (proc.stdout or "").splitlines():
        if not line.strip().isdigit():
            continue
        child = int(line.strip())
        if child in out:
            continue
        out.add(child)
        out.update(_descendant_pids(child))
    return out


def protected_validation_pids() -> set[int]:
    """PIDs that must not be SIGTERM'd by worker_stuck_recovery / cleanup leftovers."""
    sweep_stale_lock()
    row = _load()
    if not row:
        return set()
    ttl = int(row.get("ttl_sec") or DEFAULT_TTL_SEC)
    if _stale(row, ttl):
        return set()
    holder = str(row.get("holder") or "")
    if holder not in PROTECTED_HOLDERS:
        return set()
    root = int(row.get("pid") or 0)
    if not root or not _pid_alive(root):
        return set()
    protected = {root}
    protected.update(_descendant_pids(root))
    return protected


def is_pid_protected(pid: int) -> bool:
    return int(pid) in protected_validation_pids()


def assert_clear(*, for_holder: str) -> dict:
    """Refuse goal1_e2e / overlapping runs when factory or goal1 executor is busy."""
    sweep_stale_lock()
    st = status()
    if st.get("locked") and st.get("lock"):
        lock = st["lock"]
        if str(lock.get("holder")) != for_holder:
            return {
                "ok": False,
                "error": "FACTORY_VALIDATION_LOCKED",
                "blocked_by": lock.get("holder"),
                "blocked_pid": lock.get("pid"),
            }
    if for_holder == "goal1_e2e":
        g1 = _goal1_busy()
        if g1:
            return {"ok": False, "error": "GOAL1_EXECUTOR_BUSY", **g1}
        row = _load()
        if row and not _stale(row, int(row.get("ttl_sec") or DEFAULT_TTL_SEC)):
            ex_holder = str(row.get("holder") or "")
            if ex_holder == "full_e2e":
                return {
                    "ok": False,
                    "error": "FULL_E2E_IN_PROGRESS",
                    "blocked_by": ex_holder,
                    "blocked_pid": row.get("pid"),
                }
    return {"ok": True, "clear": True, "for": for_holder}


def main() -> int:
    p = argparse.ArgumentParser(description="Factory validation lock")
    p.add_argument("cmd", choices=("acquire", "release", "status", "assert-clear", "sweep"))
    p.add_argument("--holder", default="")
    p.add_argument("--for", dest="for_holder", default="")
    p.add_argument("--pid", type=int, default=0)
    p.add_argument("--ttl", type=int, default=DEFAULT_TTL_SEC)
    p.add_argument("--json", action="store_true")
    args = p.parse_args()

    if args.cmd == "acquire":
        row = acquire(holder=args.holder, pid=args.pid or None, ttl_sec=args.ttl)
    elif args.cmd == "release":
        row = release(holder=args.holder or None, pid=args.pid or None)
    elif args.cmd == "status":
        row = status()
    elif args.cmd == "sweep":
        row = sweep_stale_lock()
    else:
        row = assert_clear(for_holder=args.for_holder or args.holder)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
