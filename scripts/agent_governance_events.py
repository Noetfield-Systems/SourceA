#!/usr/bin/env python3
"""Append-only governance trace — workspace select, loop, reviews."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

EVENTS_PATH = Path.home() / ".sina" / "agent-governance-events.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def log_governance_event(
    event: str,
    *,
    workspace_id: str | None = None,
    detail: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict:
    from governance_event_kind_v1 import normalize_kind  # noqa: WPS433

    kind = normalize_kind({"event": event}) or event
    row = {
        "at": _now(),
        "kind": kind,
        "event": event,
        "workspace_id": workspace_id,
        "detail": (detail or "")[:2000],
    }
    if extra:
        row.update(extra)
        if "kind" in extra:
            row["kind"] = normalize_kind(row) or extra["kind"]
        if "event" not in extra:
            row["event"] = event
    EVENTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")
    try:
        EVENTS_PATH.chmod(0o600)
    except OSError:
        pass
    return {"ok": True, "logged": event, "kind": kind}


def tail_events(*, workspace_id: str | None = None, limit: int = 50) -> list[dict]:
    from governance_event_kind_v1 import normalize_row  # noqa: WPS433

    if not EVENTS_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in EVENTS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(normalize_row(json.loads(line)))
        except json.JSONDecodeError:
            continue
    if workspace_id:
        rows = [r for r in rows if r.get("workspace_id") == workspace_id]
    return rows[-limit:]


def governance_trace_payload(workspace_id: str | None = None, limit: int = 3) -> dict:
    events = tail_events(workspace_id=workspace_id, limit=limit if workspace_id else 20)
    if workspace_id:
        events = events[-limit:]
    return {
        "ok": True,
        "path": str(EVENTS_PATH),
        "events": events,
        "count": len(events),
    }
