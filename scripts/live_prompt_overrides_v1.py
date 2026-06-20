#!/usr/bin/env python3
"""Founder optional overrides for live ongoing prompts — never blocks delivery gate."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

SINA = Path.home() / ".sina"
OVERRIDES = SINA / "live-prompt-overrides-v1.json"
SCHEMA = "live-prompt-overrides-v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load() -> dict:
    if not OVERRIDES.is_file():
        return {
            "schema": SCHEMA,
            "edits": {},
            "quarantine": [],
            "excluded": [],
            "founder_confirmed_at": None,
            "updated_at": None,
        }
    try:
        return json.loads(OVERRIDES.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": SCHEMA, "edits": {}, "quarantine": [], "excluded": []}


def _save(data: dict) -> dict:
    data["schema"] = SCHEMA
    data["updated_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    OVERRIDES.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return data


def _rebuild_live() -> None:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from live_ongoing_prompts_v1 import rebuild  # noqa: WPS433

    rebuild(write=True)


def handle_action(body: dict) -> dict:
    action = (body.get("action") or "status").strip().lower()
    st = _load()

    if action == "status":
        return {"ok": True, "overrides": st}

    if action == "edit":
        pos = body.get("queue_pos")
        if pos is None:
            return {"ok": False, "error": "queue_pos required"}
        key = str(int(pos))
        edits = st.setdefault("edits", {})
        edits[key] = {
            "instruction": (body.get("instruction") or "")[:8000],
            "title": (body.get("title") or "")[:200],
            "at": _now(),
        }
        _save(st)
        _rebuild_live()
        return {"ok": True, "message": f"Edit saved for pos {key}", "overrides": st}

    if action == "quarantine":
        pos = body.get("queue_pos")
        if pos is None:
            return {"ok": False, "error": "queue_pos required"}
        q = st.setdefault("quarantine", [])
        ipos = int(pos)
        if ipos not in q:
            q.append(ipos)
        _save(st)
        _rebuild_live()
        return {"ok": True, "message": f"Quarantined pos {ipos}", "overrides": st}

    if action == "delete":
        pos = body.get("queue_pos")
        if pos is None:
            return {"ok": False, "error": "queue_pos required"}
        ex = st.setdefault("excluded", [])
        ipos = int(pos)
        if ipos not in ex:
            ex.append(ipos)
        _save(st)
        _rebuild_live()
        return {"ok": True, "message": f"Excluded pos {ipos} from live slice", "overrides": st}

    if action == "confirm":
        st["founder_confirmed_at"] = _now()
        _save(st)
        _rebuild_live()
        return {"ok": True, "message": "Optional confirm stamp — does not gate delivery", "overrides": st}

    if action == "clear_confirm":
        st["founder_confirmed_at"] = None
        _save(st)
        _rebuild_live()
        return {"ok": True, "overrides": st}

    return {"ok": False, "error": f"unknown action: {action}"}


def payload() -> dict:
    import sys
    from pathlib import Path

    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
    from live_ongoing_prompts_v1 import payload as live_payload  # noqa: WPS433

    return {
        "ok": True,
        "live_ongoing_prompts": live_payload(),
        "overrides": _load(),
    }
