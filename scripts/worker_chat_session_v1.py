#!/usr/bin/env python3
"""Dedicated SourceA Worker Cursor chat session — agent --resume target."""
from __future__ import annotations

import json
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

MARKER = Path.home() / ".sina" / "worker-chat-marker-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def resolve_agent_bin() -> str:
    """Hub subprocesses often lack ~/.local/bin on PATH — resolve explicitly."""
    home = Path.home()
    for candidate in (
        shutil.which("agent"),
        str(home / ".local/bin/agent"),
        shutil.which("cursor"),
        str(home / ".local/bin/cursor"),
    ):
        if candidate and Path(candidate).is_file():
            return candidate
    return "agent"


def _agent_bin() -> str:
    return resolve_agent_bin()


def load_worker_chat_id() -> str | None:
    if not MARKER.is_file():
        return None
    try:
        row = json.loads(MARKER.read_text(encoding="utf-8"))
        cid = str(row.get("conversation_id") or "").strip()
        return cid or None
    except (OSError, json.JSONDecodeError):
        return None


def ensure_worker_chat_id(*, create_if_missing: bool = True) -> dict:
    """Return Worker chat id for `agent --resume` (messages land in that Cursor chat)."""
    cid = load_worker_chat_id()
    if cid:
        return {"ok": True, "conversation_id": cid, "source": "marker", "marker": str(MARKER)}

    if not create_if_missing:
        return {"ok": False, "error": "WORKER_CHAT_UNMARKED", "hint": "Open SourceA Worker chat in Cursor"}

    proc = subprocess.run(
        [_agent_bin(), "create-chat"],
        capture_output=True,
        text=True,
        timeout=60,
    )
    cid = (proc.stdout or "").strip()
    if proc.returncode != 0 or not cid:
        err = (proc.stderr or proc.stdout or "create-chat failed").strip()
        return {"ok": False, "error": err}

    MARKER.parent.mkdir(parents=True, exist_ok=True)
    MARKER.write_text(
        json.dumps(
            {
                "conversation_id": cid,
                "created_at": _now(),
                "source": "agent create-chat",
                "law": "SourceA Worker dedicated chat — agent --resume target",
                "founder_note": "Replace id: worker_inject_lib.py --mark-worker-chat <your-worker-chat-id>",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"ok": True, "conversation_id": cid, "source": "created", "marker": str(MARKER)}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Worker Cursor chat session id")
    p.add_argument("--json", action="store_true")
    p.add_argument("--ensure", action="store_true")
    args = p.parse_args()
    row = ensure_worker_chat_id() if args.ensure else {"conversation_id": load_worker_chat_id()}
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("conversation_id") or row.get("error"))
    return 0 if row.get("ok") or row.get("conversation_id") else 1


if __name__ == "__main__":
    raise SystemExit(main())
