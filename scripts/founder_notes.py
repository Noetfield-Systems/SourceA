#!/usr/bin/env python3
"""Founder notes for Sina Command — UI feedback without screenshots."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path

NOTES_PATH = Path.home() / ".sina" / "founder-notes.json"


def _load() -> dict:
    if not NOTES_PATH.is_file():
        return {"notes": [], "updated_at": None}
    return json.loads(NOTES_PATH.read_text(encoding="utf-8"))


def _save(data: dict) -> None:
    NOTES_PATH.parent.mkdir(parents=True, exist_ok=True)
    data["updated_at"] = datetime.now(timezone.utc).isoformat()
    NOTES_PATH.write_text(json.dumps(data, indent=2), encoding="utf-8")
    try:
        NOTES_PATH.chmod(0o600)
    except OSError:
        pass


def list_notes(limit: int = 80) -> list[dict]:
    rows = _load().get("notes") or []
    rows.sort(key=lambda x: x.get("created_at") or "", reverse=True)
    return rows[:limit]


def add_note(text: str, category: str = "update", status: str = "open") -> dict:
    text = (text or "").strip()
    if not text:
        return {"ok": False, "error": "note text required"}
    cat = category if category in ("update", "fix", "idea", "question") else "update"
    st = status if status in ("open", "done") else "open"
    data = _load()
    note = {
        "id": str(uuid.uuid4())[:8],
        "text": text[:4000],
        "category": cat,
        "status": st,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    data.setdefault("notes", []).insert(0, note)
    _save(data)
    return {"ok": True, "note": note}


def set_note_status(note_id: str, status: str) -> dict:
    data = _load()
    for n in data.get("notes") or []:
        if n.get("id") == note_id:
            n["status"] = "done" if status == "done" else "open"
            _save(data)
            return {"ok": True, "note": n}
    return {"ok": False, "error": "note not found"}
