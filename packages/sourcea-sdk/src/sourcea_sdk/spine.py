"""Portable spine append + replay — extracted from governance_event_spine_v1."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sourcea_sdk.portable_paths import spine_path

SCHEMA = "governance-event-spine-v1.1"
EVENT_TYPES = frozenset(
    {
        "FOUNDER_PICK",
        "FOUNDER_SIGNAL",
        "WORKER_ROUND",
        "LAW_TOUCHED",
        "PROPAGATION",
        "VALIDATOR_PASS",
        "EXTERNAL_CRITIC_INGEST",
        "RECOVERY_FOUND",
        "IMPACT_SCAN",
        "AGENT_SESSION_GATE",
        "FBE_JOB_SIGNED",
    }
)
OBJECT_KINDS = frozenset({"law", "task", "founder_request", "pick", "system"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _checksum(row: dict[str, Any]) -> str:
    body = {k: v for k, v in row.items() if k != "checksum"}
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _version_for_object(path: Path, object_id: str) -> int:
    if not path.is_file():
        return 1
    last = 0
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("object_id") == object_id:
            last = max(last, int(row.get("version") or 0))
    return last + 1


def verify_spine_row(row: dict[str, Any]) -> tuple[bool, str]:
    if row.get("schema") not in (SCHEMA, "governance-event-spine-v1"):
        return False, "bad schema"
    for field in ("event_id", "event_type", "object_id", "object_kind", "version", "checksum"):
        if not row.get(field):
            return False, f"missing {field}"
    if row.get("event_type") not in EVENT_TYPES:
        return False, "bad event_type"
    if row.get("checksum") != _checksum(dict(row)):
        return False, "checksum mismatch"
    return True, "ok"


def append_spine_event(
    *,
    event_type: str,
    object_id: str,
    object_kind: str = "system",
    agent_id: str = "developer",
    payload: dict[str, Any] | None = None,
    cwd: Path | None = None,
) -> dict[str, Any]:
    if event_type not in EVENT_TYPES:
        return {"ok": False, "error": f"invalid event_type: {event_type}"}
    if object_kind not in OBJECT_KINDS:
        return {"ok": False, "error": f"invalid object_kind: {object_kind}"}
    path = spine_path(cwd)
    ver = _version_for_object(path, object_id)
    eid = f"GEV-{uuid.uuid4().hex[:12]}"
    replay_pointer = f"{event_type}:{object_id}:{ver}"
    row = {
        "schema": SCHEMA,
        "event_id": eid,
        "parent_event_id": None,
        "correlation_id": str(uuid.uuid4()),
        "at": _now(),
        "agent_id": agent_id,
        "event_type": event_type,
        "object_id": object_id,
        "object_kind": object_kind,
        "version": ver,
        "law_id": None,
        "skill_id": None,
        "validator_set": ["validate-sourcea-sdk-v1.sh"],
        "affected_objects": [],
        "replay_pointer": replay_pointer,
        "replay_key": replay_pointer,
        "projection_version": "sdk-portable-v1",
        "status": "committed",
        "payload": payload or {},
        "projection_targets": [],
        "gate": None,
        "proof": None,
    }
    row["checksum"] = _checksum(row)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "event": row, "path": str(path)}


def tail_spine(*, n: int = 5, cwd: Path | None = None) -> list[dict[str, Any]]:
    path = spine_path(cwd)
    if not path.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-n:]
