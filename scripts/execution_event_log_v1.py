#!/usr/bin/env python3
"""Append-only execution events — contract: brain-os/system/EVENT_CONTRACT.yaml"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

EVENTS_DIR = Path.home() / ".sina" / "events"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _day_path() -> Path:
    day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    return EVENTS_DIR / f"{day}.jsonl"


def ensure_daily_events_file(*, actor: str = "execution_event_log_v1") -> dict:
    """Create today's append-only event log if missing (Section 8 Tier-2)."""
    path = _day_path()
    if path.is_file() and path.stat().st_size > 0:
        return {"ok": True, "created": False, "path": str(path)}
    row = append_event(
        event="SESSION_BOOTSTRAP",
        actor=actor,
        data={"reason": "ensure_daily_events_file"},
    )
    return {"ok": True, "created": True, "path": str(path), "row": row}


def append_event(
    *,
    event: str,
    actor: str,
    trace_id: str = "",
    data: dict | None = None,
) -> dict:
    row = {
        "at": _now(),
        "event": event,
        "actor": actor,
        "trace_id": trace_id or None,
        "data": data or {},
    }
    path = _day_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--event", required=True)
    p.add_argument("--actor", required=True)
    p.add_argument("--trace-id", default="")
    p.add_argument("--data", default="{}")
    args = p.parse_args()
    data = json.loads(args.data)
    row = append_event(event=args.event, actor=args.actor, trace_id=args.trace_id, data=data)
    print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
