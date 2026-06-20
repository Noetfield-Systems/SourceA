#!/usr/bin/env python3
"""Advance healthy-queue-30 after Worker STOP."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from healthy_queue_ssot_lib import healthy_queue_path, healthy_queue_state_path  # noqa: E402

STATE = Path.home() / ".sina/healthy-queue-state-v1.json"


def _queue_path() -> Path:
    return healthy_queue_path()


def _read_state() -> int:
    path = healthy_queue_state_path()
    if path.is_file():
        try:
            return int(json.loads(path.read_text()).get("next_pos") or 1)
        except Exception:
            pass
    return 1


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def advance(*, skip_sa_slice: bool = False, fast: bool | None = None) -> dict:
    import os

    if fast is None:
        fast = os.environ.get("SINA_BROKER_FAST", "").strip().lower() in ("1", "true", "yes") or os.environ.get(
            "SINA_COMMERCIAL_LOOP", ""
        ).strip().lower() in ("1", "true", "yes")
    queue = json.loads(_queue_path().read_text(encoding="utf-8"))
    items = queue.get("queue") or []
    n = len(items)
    pos = _read_state()
    if pos < 1 or pos > n:
        pos = 1

    completed = pos
    nxt = pos + 1
    skipped = 0
    if skip_sa_slice and items:
        item = items[pos - 1]
        sa = item.get("sa_id")
        role = item.get("queue_role")
        # After CHECK on blocked sa: jump past ACT+VERIFY for same sa_id.
        while nxt <= n:
            nxt_item = items[nxt - 1]
            if nxt_item.get("sa_id") != sa:
                break
            skipped += 1
            nxt += 1
        if nxt > n:
            nxt = 1

    out = {
        "next_pos": nxt,
        "last_advanced_at": _now(),
        "last_completed_pos": completed,
        "skip_sa_slice": skip_sa_slice,
        "skipped_positions": skipped,
    }
    if skip_sa_slice:
        out["blocked_sa"] = items[completed - 1].get("sa_id") if items else None
        out["blocked_from_role"] = role
    payload = json.dumps(out, indent=2) + "\n"
    # Write to BOTH repo (primary) and ~/.sina/ (legacy dashboard compat)
    state_repo = healthy_queue_state_path()
    state_repo.parent.mkdir(parents=True, exist_ok=True)
    state_repo.write_text(payload, encoding="utf-8")
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(payload, encoding="utf-8")
    except Exception:
        pass  # non-fatal if ~/.sina/ not writable
    brain_sync: dict = {"ok": True, "skipped": "commercial_fast"} if fast else {}
    if not fast:
        try:
            from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

            brain_sync = sync_brain_snapshot(mode="light", caller="advance-healthy-queue")
        except Exception as exc:
            brain_sync = {"ok": False, "error": str(exc)}
    live_rebuild: dict = {"ok": True, "skipped": "commercial_fast"} if fast else {}
    if not fast:
        try:
            from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

            live_rebuild = rebuild(write=True, preview=False)
        except Exception as exc:
            live_rebuild = {"ok": False, "error": str(exc)}
    return {
        "ok": True,
        "completed_pos": completed,
        "next_pos": nxt,
        "queue_total": n,
        "brain_sync": brain_sync,
        "live_ongoing_rebuild": live_rebuild,
        **out,
    }


def set_pos(pos: int, *, reason: str = "manual") -> dict:
    queue = json.loads(_queue_path().read_text(encoding="utf-8"))
    items = queue.get("queue") or []
    n = len(items)
    if pos < 1 or pos > n:
        return {"ok": False, "error": f"pos_out_of_range: {pos} (1..{n})"}
    out = {
        "next_pos": pos,
        "last_advanced_at": _now(),
        "last_completed_pos": max(0, pos - 1),
        "skip_sa_slice": False,
        "skipped_positions": 0,
        "set_pos_reason": reason,
    }
    payload = json.dumps(out, indent=2) + "\n"
    state_repo = healthy_queue_state_path()
    state_repo.parent.mkdir(parents=True, exist_ok=True)
    state_repo.write_text(payload, encoding="utf-8")
    try:
        STATE.parent.mkdir(parents=True, exist_ok=True)
        STATE.write_text(payload, encoding="utf-8")
    except Exception:
        pass
    item = items[pos - 1] if items else {}
    brain_sync: dict = {}
    try:
        from brain_sync_lib_v1 import sync_brain_snapshot  # noqa: WPS433

        brain_sync = sync_brain_snapshot(mode="light", caller="advance-set-pos")
    except Exception as exc:
        brain_sync = {"ok": False, "error": str(exc)}
    live_rebuild: dict = {}
    try:
        from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

        live_rebuild = rebuild(write=True, preview=False)
    except Exception as exc:
        live_rebuild = {"ok": False, "error": str(exc)}
    return {
        "ok": True,
        "next_pos": pos,
        "queue_total": n,
        "sa_id": item.get("sa_id"),
        "queue_role": item.get("queue_role"),
        "brain_sync": brain_sync,
        "live_ongoing_rebuild": live_rebuild,
        **out,
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--skip-sa-slice",
        action="store_true",
        help="After CHECK on commercial blocker — skip ACT+VERIFY for same sa",
    )
    p.add_argument("--fast", action="store_true", help="Skip brain_sync + live pack rebuild (Worker loop)")
    p.add_argument("--set-pos", type=int, default=0, help="Fast-forward queue pointer (skip done turns)")
    p.add_argument("--reason", default="manual")
    args = p.parse_args()
    if args.set_pos:
        print(json.dumps(set_pos(args.set_pos, reason=args.reason)))
    else:
        print(json.dumps(advance(skip_sa_slice=args.skip_sa_slice, fast=args.fast)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
