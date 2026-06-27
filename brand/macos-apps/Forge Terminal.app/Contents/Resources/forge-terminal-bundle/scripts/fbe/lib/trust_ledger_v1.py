"""FBE Trust Ledger — append-only execution event chain."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
LEDGER_PATH = SINA / "fbe-trust-ledger-v1.jsonl"
SCHEMA = "fbe-trust-ledger-v1"

EVENT_TYPES = frozenset(
    {
        "JOB_QUEUED",
        "POLICY_CHECKED",
        "KERNEL_STARTED",
        "NODE_EXECUTED",
        "JOB_COMPLETED",
        "RECEIPT_FEDERATED",
        "LEDGER_SIGNED",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _checksum(row: dict[str, Any]) -> str:
    body = {k: v for k, v in row.items() if k != "checksum"}
    raw = json.dumps(body, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def _last_event_id(job_id: str) -> str:
    if not LEDGER_PATH.is_file():
        return ""
    last = ""
    for line in LEDGER_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("job_id") == job_id:
            last = str(row.get("event_id") or last)
    return last


def append_event(
    *,
    event_type: str,
    job_id: str,
    factory_id: str = "",
    policy_pack: str = "",
    kernel_hash: str = "",
    parent_event_id: str = "",
    payload: dict[str, Any] | None = None,
    bridge_spine: bool = True,
) -> dict[str, Any]:
    if event_type not in EVENT_TYPES:
        return {"ok": False, "error": f"invalid_event_type:{event_type}"}

    parent = parent_event_id or _last_event_id(job_id)
    eid = f"FBE-{uuid.uuid4().hex[:12]}"
    row: dict[str, Any] = {
        "schema": SCHEMA,
        "event_id": eid,
        "parent_event_id": parent or None,
        "event_type": event_type,
        "job_id": job_id,
        "factory_id": factory_id or None,
        "policy_pack": policy_pack or None,
        "kernel_hash": kernel_hash or None,
        "at": _now(),
        "payload": payload or {},
    }
    row["checksum"] = _checksum(row)
    SINA.mkdir(parents=True, exist_ok=True)
    with LEDGER_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")

    spine_row: dict[str, Any] = {"ok": False, "skipped": True}
    if bridge_spine and event_type == "LEDGER_SIGNED":
        try:
            import sys
            from pathlib import Path as P

            root = P(__file__).resolve().parents[3]
            sys.path.insert(0, str(root / "scripts"))
            from governance_event_spine_v1 import append_event as spine_append  # noqa: WPS433

            spine_row = spine_append(
                event_type="FBE_JOB_SIGNED",
                object_id=job_id,
                object_kind="system",
                agent_id="fbe_trust_ledger",
                parent_event_id=parent or "",
                payload={
                    "factory_id": factory_id,
                    "policy_pack": policy_pack,
                    "kernel_hash": kernel_hash,
                    "ledger_event_id": eid,
                },
                proof="fbe-trust-ledger-v1",
            )
        except Exception as exc:
            spine_row = {"ok": False, "error": str(exc)}

    return {"ok": True, "event": row, "path": str(LEDGER_PATH), "spine": spine_row}


def events_for_job(job_id: str) -> list[dict[str, Any]]:
    if not LEDGER_PATH.is_file():
        return []
    out: list[dict[str, Any]] = []
    for line in LEDGER_PATH.read_text(encoding="utf-8", errors="replace").splitlines():
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if row.get("job_id") == job_id:
            out.append(row)
    return out


def ledger_payload(*, job_id: str = "") -> dict[str, Any]:
    if job_id:
        events = events_for_job(job_id)
        return {
            "ok": True,
            "schema": "fbe-ledger-status-v1",
            "job_id": job_id,
            "event_count": len(events),
            "events": events,
        }
    if not LEDGER_PATH.is_file():
        return {"ok": True, "schema": "fbe-ledger-status-v1", "event_count": 0, "events": []}
    lines = [ln for ln in LEDGER_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return {
        "ok": True,
        "schema": "fbe-ledger-status-v1",
        "event_count": len(lines),
        "tail": [json.loads(ln) for ln in lines[-5:]] if lines else [],
    }
