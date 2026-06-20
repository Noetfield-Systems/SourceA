"""Minimal event fabric — pub/sub over ~/.sina/events_v1.jsonl."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVENT_LOG = Path.home() / ".sina" / "events_v1.jsonl"
SCHEMA = "event-bus-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def publish(*, topic: str, payload: dict[str, Any], source: str = "hub") -> dict[str, Any]:
    row = {
        "schema": SCHEMA,
        "at": _now(),
        "topic": topic,
        "source": source,
        "payload": payload,
    }
    EVENT_LOG.parent.mkdir(parents=True, exist_ok=True)
    with EVENT_LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "published": row}


def tail(*, topic: str | None = None, n: int = 20) -> list[dict]:
    if not EVENT_LOG.is_file():
        return []
    lines = EVENT_LOG.read_text(encoding="utf-8").strip().splitlines()
    out: list[dict] = []
    for line in lines[-n * 3 :]:
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if topic and row.get("topic") != topic:
            continue
        out.append(row)
    return out[-n:]


def event_bus_payload() -> dict[str, Any]:
    recent = tail(n=12)
    topics = sorted({r.get("topic") for r in recent if r.get("topic")})
    return {
        "ok": True,
        "schema": SCHEMA,
        "path": str(EVENT_LOG),
        "topic_count": len(topics),
        "recent_topics": topics,
        "recent": recent,
        "api": "/api/event-bus-v1",
        "consumers": ["feedback_loop", "governance_drift", "gate_receipts"],
    }
