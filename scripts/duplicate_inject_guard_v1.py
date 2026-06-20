#!/usr/bin/env python3
"""Block duplicate Goal 1 injects — turn-bind + 90s cooldown + immediate lock.

Law: brain-os/laws/NO_DUPLICATE_INJECT_LOCKED_v1.md
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
INJECT_LOCK_JSON = Path.home() / ".sina" / "goal1-inject-lock-v1.json"
POINTER_JSON = Path.home() / ".sina" / "next-execution-pointer-v1.json"
TURN_BIND_JSON = Path.home() / ".sina" / "goal1-worker-turn-bind-v1.json"
INBOX_JSON = Path.home() / ".sina" / "worker-prompt-inbox-v1.json"
EVENT_LOG = Path.home() / ".sina" / "goal1-duplicate-inject-v1.jsonl"
COOLDOWN_SEC = 90


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_ts(ts: str) -> datetime | None:
    try:
        return datetime.strptime((ts or "").strip(), "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _age_sec(ts: str) -> float | None:
    dt = _parse_ts(ts)
    if not dt:
        return None
    return (datetime.now(timezone.utc) - dt).total_seconds()


def _log_event(row: dict) -> None:
    try:
        EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with EVENT_LOG.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps({**row, "at": _now()}) + "\n")
    except OSError:
        pass


def load_pointer_sa() -> str:
    if not POINTER_JSON.is_file():
        return ""
    try:
        row = json.loads(POINTER_JSON.read_text(encoding="utf-8"))
        return str(row.get("next_sa") or "").lower()
    except (OSError, json.JSONDecodeError):
        return ""


def load_inject_lock() -> dict:
    if not INJECT_LOCK_JSON.is_file():
        return {}
    try:
        return json.loads(INJECT_LOCK_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def clear_inject_lock() -> dict:
    """Validator/E2E reset — drop cooldown lock so same sa can re-deliver."""
    try:
        INJECT_LOCK_JSON.unlink(missing_ok=True)
    except OSError:
        pass
    return {"ok": True}


def load_turn_bind() -> dict:
    if not TURN_BIND_JSON.is_file():
        return {}
    try:
        return json.loads(TURN_BIND_JSON.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def inbox_pending_meta() -> dict:
    if not INBOX_JSON.is_file():
        return {}
    try:
        row = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
        if not row.get("pending"):
            return {}
        return row.get("meta") or {}
    except (OSError, json.JSONDecodeError):
        return {}


def _same_turn(a: dict, b: dict) -> bool:
    return (
        str(a.get("sa_id") or "").lower() == str(b.get("sa_id") or "").lower()
        and str(a.get("queue_role") or "") == str(b.get("queue_role") or "")
        and int(a.get("queue_pos") or 0) == int(b.get("queue_pos") or 0)
    )


def _same_sa_id(a: dict, b: dict) -> bool:
    return str(a.get("sa_id") or "").lower() == str(b.get("sa_id") or "").lower()


def _worker_turn_open_for_sa(sa: str) -> dict:
    path = Path.home() / ".sina" / "worker_turn_state_v1.json"
    if not path.is_file():
        return {}
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if row.get("status") == "open" and str(row.get("sa_id") or "").lower() == sa:
        return row
    return {}


def check_skip_inject(*, meta: dict, source: str = "") -> dict:
    """Return skip=True when inject would duplicate an unconsumed turn (ASF: before any prompt fires)."""
    sa = str(meta.get("sa_id") or "").lower()
    if not sa.startswith("sa-"):
        return {"ok": True, "skip": False, "reason": "no_sa_probe"}

    pointer_sa = load_pointer_sa()
    turn_bind = load_turn_bind()
    pending_meta = inbox_pending_meta()
    lock = load_inject_lock()
    bind_sa = str(turn_bind.get("sa_id") or "").lower()

    # ASF gate 2: same sa_id already in Cursor queue (turn-bind matches this turn + still active)
    if bind_sa == sa and _same_turn(turn_bind, meta):
        open_turn = _worker_turn_open_for_sa(sa)
        if open_turn or pending_meta:
            row = {
                "ok": True,
                "skip": True,
                "reason": "SA_ALREADY_IN_CURSOR_QUEUE_TURN_BIND",
                "sa_id": sa,
                "turn_bind": turn_bind,
                "worker_turn": open_turn or None,
                "pending_meta": pending_meta or None,
                "source": source,
            }
            _log_event({**row, "event": "INJECT_BLOCK"})
            return row

    if pending_meta and _same_turn(pending_meta, meta):
        row = {
            "ok": True,
            "skip": True,
            "reason": "INBOX_ALREADY_PENDING_SAME_TURN",
            "sa_id": sa,
            "source": source,
            "pending_meta": pending_meta,
        }
        _log_event({**row, "event": "INJECT_SKIP"})
        return row

    # Any unconsumed INBOX blocks new inject (prevents Cursor 18× run-inbox queue).
    if pending_meta:
        row = {
            "ok": True,
            "skip": True,
            "reason": "INBOX_ALREADY_PENDING",
            "sa_id": sa,
            "pending_sa": pending_meta.get("sa_id"),
            "source": source,
        }
        _log_event({**row, "event": "INJECT_BLOCK"})
        return row

    if pending_meta and _same_sa_id(pending_meta, meta) and bind_sa == sa:
        row = {
            "ok": True,
            "skip": True,
            "reason": "TURN_BIND_MATCHES_POINTER_ALREADY_QUEUED",
            "sa_id": sa,
            "pointer_sa": pointer_sa,
            "turn_bind": turn_bind,
            "source": source,
        }
        _log_event({**row, "event": "INJECT_SKIP"})
        return row

    # ASF gate 1: COOLDOWN_SAME_SA_ID removed — role advance (CHECK→ACT→VERIFY) allowed within 90s.
    lock_age = _age_sec(str(lock.get("at") or ""))
    if lock_age is not None and lock_age < COOLDOWN_SEC and _same_turn(lock, meta):
        row = {
            "ok": True,
            "skip": True,
            "reason": "COOLDOWN_SAME_TURN",
            "sa_id": sa,
            "cooldown_sec": COOLDOWN_SEC,
            "age_sec": round(lock_age, 1),
            "lock": lock,
            "source": source,
        }
        _log_event({**row, "event": "INJECT_SKIP"})
        return row

    return {"ok": True, "skip": False, "sa_id": sa, "pointer_sa": pointer_sa}


def acquire_inject_lock(*, meta: dict, source: str = "", prompt: str = "") -> dict:
    """Write inject lock + turn-bind BEFORE inbox paste or agent call."""
    sa = str(meta.get("sa_id") or "").lower()
    row = {
        "schema": "goal1-inject-lock-v1",
        "sa_id": sa,
        "queue_role": meta.get("queue_role"),
        "queue_pos": meta.get("queue_pos"),
        "queue_total": meta.get("queue_total"),
        "source": source,
        "at": _now(),
        "law": "NO_DUPLICATE_INJECT_LOCKED_v1.md",
    }
    INJECT_LOCK_JSON.parent.mkdir(parents=True, exist_ok=True)
    INJECT_LOCK_JSON.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import write_turn_bind  # noqa: WPS433

    bind = write_turn_bind(meta=meta, prompt=prompt)
    out = {"ok": True, "lock": row, "turn_bind": bind}
    _log_event({**out, "event": "INJECT_LOCK_ACQUIRED", "sa_id": sa, "source": source})
    return out


def preflight_inject(*, meta: dict, source: str = "", prompt: str = "") -> dict:
    """Check skip; on proceed acquire lock immediately (before delivery)."""
    chk = check_skip_inject(meta=meta, source=source)
    if chk.get("skip"):
        return {"ok": False, "blocked": True, "action": "SKIP_INJECT", **chk}
    lock = acquire_inject_lock(meta=meta, source=source, prompt=prompt)
    return {"ok": True, "blocked": False, "action": "PROCEED", "check": chk, **lock}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Duplicate inject guard")
    p.add_argument("--sa", required=True)
    p.add_argument("--role", default="check")
    p.add_argument("--pos", type=int, default=1)
    p.add_argument("--total", type=int, default=30)
    p.add_argument("--source", default="cli")
    p.add_argument("--check-only", action="store_true")
    args = p.parse_args()
    meta = {
        "sa_id": args.sa,
        "queue_role": args.role,
        "queue_pos": args.pos,
        "queue_total": args.total,
    }
    if args.check_only:
        print(json.dumps(check_skip_inject(meta=meta, source=args.source), indent=2))
    else:
        print(json.dumps(preflight_inject(meta=meta, source=args.source), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
