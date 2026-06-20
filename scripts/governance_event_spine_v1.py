#!/usr/bin/env python3
"""G1 — append-only governance event spine with replay fields."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
SPINE_PATH = SINA / "governance-event-spine-v1.jsonl"
SCHEMA = "governance-event-spine-v1.1"
SCHEMA_LEGACY = "governance-event-spine-v1"
PROJECTION_VERSION = "hub-align-v1"

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


def _checksum(row: dict) -> str:
    body = {k: v for k, v in row.items() if k != "checksum"}
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _version_for_object(object_id: str) -> int:
    if not SPINE_PATH.is_file():
        return 1
    last = 0
    for line in SPINE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if o.get("object_id") == object_id:
            last = max(last, int(o.get("version") or 0))
    return last + 1


def append_event(
    *,
    event_type: str,
    object_id: str,
    object_kind: str,
    agent_id: str = "system",
    parent_event_id: str = "",
    correlation_id: str = "",
    payload: dict | None = None,
    projection_targets: list[str] | None = None,
    gate: str = "",
    proof: str = "",
    version: int | None = None,
    law_id: str = "",
    skill_id: str = "",
    validator_set: list[str] | None = None,
    affected_objects: list[str] | None = None,
    projection_version: str = "",
    status: str = "committed",
) -> dict:
    if event_type not in EVENT_TYPES:
        return {"ok": False, "error": f"invalid event_type: {event_type}"}
    if object_kind not in OBJECT_KINDS:
        return {"ok": False, "error": f"invalid object_kind: {object_kind}"}
    ver = version if version is not None else _version_for_object(object_id)
    cid = correlation_id or str(uuid.uuid4())
    eid = f"GEV-{uuid.uuid4().hex[:12]}"
    replay_pointer = f"{event_type}:{object_id}:{ver}"
    vset = list(dict.fromkeys(validator_set or ([] if not proof else [proof] if proof.endswith(".sh") else [])))
    row = {
        "schema": SCHEMA,
        "event_id": eid,
        "parent_event_id": parent_event_id or None,
        "correlation_id": cid,
        "at": _now(),
        "agent_id": agent_id,
        "event_type": event_type,
        "object_id": object_id,
        "object_kind": object_kind,
        "version": ver,
        "law_id": law_id or None,
        "skill_id": skill_id or None,
        "validator_set": vset,
        "affected_objects": affected_objects or [],
        "replay_pointer": replay_pointer,
        "replay_key": replay_pointer,
        "projection_version": projection_version or PROJECTION_VERSION,
        "status": status,
        "payload": payload or {},
        "projection_targets": projection_targets or [],
        "gate": gate or None,
        "proof": proof or None,
    }
    row["checksum"] = _checksum(row)
    SINA.mkdir(parents=True, exist_ok=True)
    with SPINE_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return {"ok": True, "event": row, "path": str(SPINE_PATH)}


def read_all_rows() -> list[dict]:
    if not SPINE_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in SPINE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def find_by_replay_pointer(replay_pointer: str) -> dict | None:
    for row in reversed(read_all_rows()):
        ptr = row.get("replay_pointer") or row.get("replay_key")
        if ptr == replay_pointer:
            return row
    return None


def find_by_event_id(event_id: str) -> dict | None:
    for row in reversed(read_all_rows()):
        if row.get("event_id") == event_id:
            return row
    return None


def find_last(*, event_type: str = "", status: str = "") -> dict | None:
    rows = read_all_rows()
    for row in reversed(rows):
        if event_type and row.get("event_type") != event_type:
            continue
        if status and row.get("status") != status:
            continue
        ok, _ = validate_row(row)
        if not ok:
            continue
        return row
    return None


def object_history(*, object_id: str, max_version: int | None = None) -> list[dict]:
    out: list[dict] = []
    for row in read_all_rows():
        if row.get("object_id") != object_id:
            continue
        ver = int(row.get("version") or 0)
        if max_version is not None and ver > max_version:
            continue
        out.append(row)
    return out


def tail(*, n: int = 20, event_type: str = "") -> list[dict]:
    if not SPINE_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in SPINE_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            o = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event_type and o.get("event_type") != event_type:
            continue
        rows.append(o)
    return rows[-n:]


def replay_candidates(*, event_type: str = "WORKER_ROUND", limit: int = 10) -> list[dict]:
    """G4-ready: list recent rows with replay_key for recovery."""
    return tail(n=limit * 3, event_type=event_type)[-limit:]


def validate_row(row: dict) -> tuple[bool, str]:
    schema = row.get("schema")
    if schema not in (SCHEMA, SCHEMA_LEGACY):
        return False, "bad schema"
    base = (
        "event_id",
        "correlation_id",
        "at",
        "agent_id",
        "event_type",
        "object_id",
        "object_kind",
        "version",
        "checksum",
    )
    for f in base:
        if not row.get(f):
            return False, f"missing {f}"
    if not (row.get("replay_pointer") or row.get("replay_key")):
        return False, "missing replay_pointer"
    if schema == SCHEMA:
        for f in ("validator_set", "affected_objects", "projection_version", "status"):
            if f not in row:
                return False, f"missing {f}"
    if row.get("event_type") not in EVENT_TYPES:
        return False, "bad event_type"
    exp = row.get("checksum")
    row_copy = dict(row)
    chk = _checksum(row_copy)
    if exp != chk:
        return False, "checksum mismatch"
    return True, "ok"


def spine_payload() -> dict:
    rows = tail(n=50)
    types: dict[str, int] = {}
    for r in rows:
        t = r.get("event_type") or "?"
        types[t] = types.get(t, 0) + 1
    return {
        "ok": True,
        "schema": SCHEMA,
        "path": str(SPINE_PATH),
        "exists": SPINE_PATH.is_file(),
        "row_count_estimate": len(rows),
        "recent_types": types,
        "recent": rows[-8:],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Governance event spine G1")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--tail", type=int, default=0)
    ap.add_argument("--replay", action="store_true")
    ap.add_argument("--append-probe", action="store_true", help="validator probe row")
    ap.add_argument("--event-type", default="")
    ap.add_argument("--object-id", default="GOV_EVENT_SPINE")
    ap.add_argument("--agent-id", default="maintainer")
    args = ap.parse_args()

    if args.append_probe:
        res = append_event(
            event_type="VALIDATOR_PASS",
            object_id=args.object_id,
            object_kind="system",
            agent_id=args.agent_id,
            payload={"probe": True},
            projection_targets=["catalog"],
            proof="validate-governance-event-spine-v1.sh",
        )
        print(json.dumps(res, indent=2))
        return 0 if res.get("ok") else 1

    if args.replay:
        print(json.dumps(replay_candidates(), indent=2))
        return 0

    if args.tail:
        print(json.dumps(tail(n=args.tail, event_type=args.event_type or ""), indent=2))
        return 0

    print(json.dumps(spine_payload(), indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
