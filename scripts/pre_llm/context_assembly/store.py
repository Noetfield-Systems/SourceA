"""D15 SSOT — ~/.sina/llm_context_packet_v1.json"""
from __future__ import annotations

import json
import os
import tempfile
from pathlib import Path

from pre_llm.context_packet.schema import PACKET_SSOT_PATH, SCHEMA

ASSEMBLY_SCHEMA = "context-assembly-v1"


def load_snapshot() -> dict:
    if not PACKET_SSOT_PATH.is_file():
        return {}
    try:
        data = json.loads(PACKET_SSOT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def load_canonical() -> dict:
    snap = load_snapshot()
    latest = snap.get("latest") or {}
    if latest.get("schema") == SCHEMA:
        return latest
    return {}


def load_assembly_meta() -> dict:
    snap = load_snapshot()
    return snap.get("assembly") or {}


L1_TAIL_LIMITATIONS = [
    "L1 semi-auto only — does not auto-paste into Cursor (SINAAI_AUTO_PASTE_INCIDENT)",
    "Founder must Submit round manually; reducer does not invoke agent_loop",
    "Tail append only — never overwrites packet latest/builds SSOT",
    "Rule-based summary — not full D14 LLM compression yet",
]


def write_tail_section(*, entry: dict, max_entries: int = 24) -> dict:
    """Append L1 ingest-reducer entry to envelope tail — preserve latest/builds/assembly."""
    from datetime import datetime, timezone

    PACKET_SSOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    envelope = load_snapshot() if PACKET_SSOT_PATH.is_file() else {"schema": SCHEMA}
    envelope.setdefault("schema", SCHEMA)
    tail = envelope.get("tail") or {
        "schema": "l1-ingest-reducer-v1",
        "level": "L1",
        "auto_paste": False,
        "limitations": list(L1_TAIL_LIMITATIONS),
        "entries": [],
    }
    entries = list(tail.get("entries") or [])
    entries.append(entry)
    tail["entries"] = entries[-max_entries:]
    tail["updated_at"] = datetime.now(timezone.utc).isoformat()
    tail["auto_paste"] = False
    tail.setdefault("limitations", list(L1_TAIL_LIMITATIONS))
    envelope["tail"] = tail

    fd, tmp = tempfile.mkstemp(dir=str(PACKET_SSOT_PATH.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(envelope, fh, indent=2)
        os.replace(tmp, PACKET_SSOT_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
    return {
        "ok": True,
        "path": str(PACKET_SSOT_PATH),
        "tail_entries": len(tail["entries"]),
        "auto_paste": False,
    }


def write_canonical(*, packet: dict, assembly: dict, task_id: str = "default") -> None:
    PACKET_SSOT_PATH.parent.mkdir(parents=True, exist_ok=True)
    envelope = load_snapshot() if PACKET_SSOT_PATH.is_file() else {"schema": SCHEMA, "builds": {}}
    envelope["schema"] = SCHEMA
    envelope["generated_at"] = packet.get("generated_at")
    envelope["path"] = str(PACKET_SSOT_PATH)
    envelope["latest"] = packet
    envelope["assembly"] = assembly
    envelope.setdefault("builds", {})[task_id] = {"packet": packet, "assembly": assembly}

    fd, tmp = tempfile.mkstemp(dir=str(PACKET_SSOT_PATH.parent), suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as fh:
            json.dump(envelope, fh, indent=2)
        os.replace(tmp, PACKET_SSOT_PATH)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
