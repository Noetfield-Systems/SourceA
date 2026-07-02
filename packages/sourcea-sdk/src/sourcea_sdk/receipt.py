"""Receipt sign + verify — portable governance chain."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from sourcea_sdk.portable_paths import latest_receipt_path, receipts_dir

RECEIPT_SCHEMA = "sourcea-sdk-receipt-v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _checksum(body: dict[str, Any]) -> str:
    payload = {k: v for k, v in body.items() if k != "receipt_checksum"}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def sign_receipt(
    *,
    intent: dict[str, Any] | None = None,
    outcome: str = "PASS",
    agent_id: str = "developer",
    object_id: str = "",
    bind_spine: bool = False,
    spine_event: dict[str, Any] | None = None,
    cwd: Path | None = None,
) -> dict[str, Any]:
    intent_body = dict(intent or {})
    oid = object_id or str(intent_body.get("object_id") or intent_body.get("intent_id") or "object")
    receipt = {
        "schema": RECEIPT_SCHEMA,
        "receipt_id": f"REC-{uuid.uuid4().hex[:12]}",
        "at": _now(),
        "agent_id": agent_id,
        "object_id": oid,
        "outcome": outcome,
        "intent": intent_body,
        "bind_spine": bind_spine,
        "spine_event_id": (spine_event or {}).get("event", {}).get("event_id") if spine_event else None,
        "spine_checksum": (spine_event or {}).get("event", {}).get("checksum") if spine_event else None,
    }
    receipt["receipt_checksum"] = _checksum(receipt)

    out_dir = receipts_dir(cwd)
    out_dir.mkdir(parents=True, exist_ok=True)
    latest = latest_receipt_path(cwd)
    latest.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    archive = out_dir / f"{receipt['receipt_id']}.json"
    archive.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


def verify_receipt(receipt: dict[str, Any]) -> tuple[bool, str]:
    if receipt.get("schema") != RECEIPT_SCHEMA:
        return False, "bad schema"
    exp = receipt.get("receipt_checksum")
    if not exp:
        return False, "missing receipt_checksum"
    got = _checksum(receipt)
    if exp != got:
        return False, "checksum mismatch"
    return True, "ok"


def load_latest_receipt(cwd: Path | None = None) -> dict[str, Any] | None:
    path = latest_receipt_path(cwd)
    if not path.is_file():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
