#!/usr/bin/env python3
"""Overnight zero-spam guard — one (sa, role, pos) per registry advance.

Blocks:
  - duplicate CHECK/ACT on same queue slot without registry progress
  - parallel dispatcher ticks (single-flight lock)
"""
from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

GUARD_STATE = Path.home() / ".sina" / "overnight-turn-guard-v1.json"
GUARD_LOG = Path.home() / ".sina" / "overnight-turn-guard-v1.jsonl"
DISPATCH_LOCK = Path.home() / ".sina" / "dispatcher-active-v1.lock"

COOLDOWN_SEC = 300
LOCK_MAX_AGE_SEC = 900

API_ROLES = frozenset({"check", "verify", "audit", "review", "test", "validate", "read", "assess"})
CLI_ROLES = frozenset({"act", "implement", "build", "fix", "patch", "create", "write", "exec"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    GUARD_LOG.parent.mkdir(parents=True, exist_ok=True)
    with GUARD_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _load_state() -> dict:
    if not GUARD_STATE.is_file():
        return {}
    try:
        return json.loads(GUARD_STATE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _save_state(st: dict) -> None:
    st["updated_at"] = _now()
    GUARD_STATE.parent.mkdir(parents=True, exist_ok=True)
    GUARD_STATE.write_text(json.dumps(st, indent=2) + "\n", encoding="utf-8")


def _pid_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except OSError:
        return False


def registry_done_count() -> int:
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from healthy_queue_ssot_lib import REGISTRY_PATH  # noqa: WPS433

    if not REGISTRY_PATH.is_file():
        return 0
    try:
        reg = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        return sum(1 for p in reg.get("plans") or [] if p.get("status") == "done")
    except (OSError, json.JSONDecodeError):
        return 0


def is_cli_act_role(role: str) -> bool:
    """CLI bills only on ACT/implement — never check/verify."""
    r = (role or "").lower().strip()
    if any(x in r for x in ("check", "verify", "audit", "review", "validate", "read", "assess")):
        return False
    return any(x in r for x in ("act", "implement", "build", "fix", "patch", "create", "write", "exec"))


def role_engine(role: str) -> str:
    """CHECK/verify → API (Haiku). ACT/implement → CLI (Sonnet)."""
    return "CLI" if is_cli_act_role(role) else "API"


def acquire_dispatch_lock(*, caller: str = "autorun_dispatcher") -> dict:
    """Single-flight: only one dispatcher turn at a time."""
    if DISPATCH_LOCK.is_file():
        try:
            row = json.loads(DISPATCH_LOCK.read_text(encoding="utf-8"))
            pid = int(row.get("pid") or 0)
            started = float(row.get("started_epoch") or 0)
            age = time.time() - started if started else 9999
            if pid and _pid_alive(pid) and age < LOCK_MAX_AGE_SEC:
                return {
                    "ok": False,
                    "skip": True,
                    "reason": "dispatch_lock_held",
                    "holder_pid": pid,
                    "age_sec": int(age),
                }
        except (OSError, json.JSONDecodeError, ValueError):
            pass
    payload = {
        "pid": os.getpid(),
        "caller": caller,
        "started_at": _now(),
        "started_epoch": time.time(),
    }
    DISPATCH_LOCK.parent.mkdir(parents=True, exist_ok=True)
    DISPATCH_LOCK.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "locked": True, "pid": os.getpid()}


def release_dispatch_lock() -> None:
    try:
        if DISPATCH_LOCK.is_file():
            row = json.loads(DISPATCH_LOCK.read_text(encoding="utf-8"))
            if int(row.get("pid") or 0) == os.getpid():
                DISPATCH_LOCK.unlink()
    except (OSError, json.JSONDecodeError, ValueError):
        try:
            DISPATCH_LOCK.unlink(missing_ok=True)
        except OSError:
            pass


def check_duplicate_turn(*, sa_id: str, role: str, pos: int) -> dict:
    """Block repeat spend on same queue slot until registry_done advances."""
    key = f"{sa_id}|{(role or '').lower().strip()}|{pos}"
    done = registry_done_count()
    st = _load_state()
    last = st.get("last_turn") or {}
    last_key = last.get("key") or ""
    last_done = int(last.get("registry_done") or -1)
    last_at = float(last.get("epoch") or 0)
    age = time.time() - last_at if last_at else 9999

    if last_key == key and last_done == done and age < COOLDOWN_SEC:
        out = {
            "ok": False,
            "skip": True,
            "reason": "duplicate_turn_no_registry_advance",
            "sa_id": sa_id,
            "role": role,
            "pos": pos,
            "registry_done": done,
            "cooldown_sec": COOLDOWN_SEC,
            "age_sec": int(age),
        }
        _log({"event": "DUPLICATE_BLOCKED", **out})
        return out
    return {"ok": True, "skip": False, "key": key, "registry_done": done}


def record_turn(
    *,
    sa_id: str,
    role: str,
    pos: int,
    engine: str,
    ok: bool,
    cost_usd: float = 0.0,
    status: str = "",
) -> dict:
    key = f"{sa_id}|{(role or '').lower().strip()}|{pos}"
    done = registry_done_count()
    st = _load_state()
    st["last_turn"] = {
        "key": key,
        "sa_id": sa_id,
        "role": role,
        "pos": pos,
        "engine": engine,
        "ok": ok,
        "status": status,
        "cost_usd": cost_usd,
        "registry_done": done,
        "epoch": time.time(),
        "at": _now(),
    }
    _save_state(st)
    _log({"event": "TURN_RECORDED", **st["last_turn"]})
    return {"ok": True, "recorded": st["last_turn"]}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Overnight turn guard")
    p.add_argument("cmd", choices=("check", "record", "status"))
    p.add_argument("--sa-id", default="")
    p.add_argument("--role", default="")
    p.add_argument("--pos", type=int, default=0)
    p.add_argument("--engine", default="")
    p.add_argument("--ok", action="store_true")
    p.add_argument("--cost", type=float, default=0.0)
    p.add_argument("--status", default="")
    args = p.parse_args()

    if args.cmd == "status":
        print(json.dumps({"state": _load_state(), "registry_done": registry_done_count()}, indent=2))
        return 0
    if args.cmd == "check":
        print(json.dumps(check_duplicate_turn(sa_id=args.sa_id, role=args.role, pos=args.pos), indent=2))
        return 0
    print(
        json.dumps(
            record_turn(
                sa_id=args.sa_id,
                role=args.role,
                pos=args.pos,
                engine=args.engine,
                ok=args.ok,
                cost_usd=args.cost,
                status=args.status,
            ),
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
