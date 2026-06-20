#!/usr/bin/env python3
"""Bind hygiene for healthy-pack autodrain — queue cursor == inbox meta == turn_bind."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
sys.path.insert(0, str(SCRIPTS))

from healthy_queue_ssot_lib import (  # noqa: E402
    healthy_queue_path,
    healthy_queue_state_path,
    queue_items,
)

TURN_BIND = SINA / "goal1-worker-turn-bind-v1.json"
INJECT_LOCK = SINA / "goal1-inject-lock-v1.json"
ACTIVE_SNAPSHOT = SINA / "goal1-active-turn-snapshot-v1.json"
INBOX_JSON = SINA / "worker-prompt-inbox-v1.json"


def clear_stale_turn_bind() -> None:
    for p in (TURN_BIND, INJECT_LOCK, ACTIVE_SNAPSHOT):
        try:
            p.unlink()
        except FileNotFoundError:
            pass


def queue_cursor_item() -> tuple[int, dict | None]:
    try:
        from healthy_queue_ssot_lib import first_open_queue_pos, load_healthy_queue, queue_items  # noqa: WPS433

        _, q = load_healthy_queue()
        items = queue_items(q)
        pos = first_open_queue_pos()
        if pos > len(items) or not items:
            return pos, None
        return pos, items[pos - 1]
    except (OSError, json.JSONDecodeError, IndexError, ValueError, ImportError):
        return 1, None


def bind_status() -> dict:
    pos, item = queue_cursor_item()
    queue_sa = str((item or {}).get("sa_id") or "")
    inbox_sa = ""
    bind_sa = ""
    pending = False
    if INBOX_JSON.is_file():
        try:
            data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
            pending = bool(data.get("pending"))
            inbox_sa = str((data.get("meta") or {}).get("sa_id") or data.get("sa_id") or "")
        except (OSError, json.JSONDecodeError):
            pass
    if TURN_BIND.is_file():
        try:
            bind_sa = str(json.loads(TURN_BIND.read_text(encoding="utf-8")).get("sa_id") or "")
        except (OSError, json.JSONDecodeError):
            pass
    # Cleared INBOX: canonical head is queue cursor — stale pack-tail meta ignored.
    if not pending and queue_sa:
        inbox_sa = queue_sa
    match = bool(queue_sa and queue_sa == inbox_sa == bind_sa) if bind_sa else bool(
        queue_sa and queue_sa == inbox_sa
    )
    queue_exhausted = False
    try:
        from healthy_queue_ssot_lib import load_healthy_queue  # noqa: WPS433

        _, qrow = load_healthy_queue()
        queue_exhausted = bool(qrow.get("queue_exhausted")) or not queue_items(qrow)
    except (OSError, json.JSONDecodeError, ImportError):
        queue_exhausted = not queue_sa
    if queue_exhausted and not pending and not bind_sa and not inbox_sa:
        match = True
    return {
        "ok": match,
        "queue_pos": pos,
        "queue_sa": queue_sa,
        "inbox_sa": inbox_sa,
        "bind_sa": bind_sa,
        "match": match,
        "inbox_pending": pending,
    }


def heal_bind_mismatch(*, force_deliver: bool = True) -> dict:
    """Align inbox meta + turn_bind to queue cursor SA."""
    clear_stale_turn_bind()
    pos, item = queue_cursor_item()
    if not item:
        return {"ok": False, "error": "queue_cursor_empty", "queue_pos": pos}

    from worker_inject_lib import heal_inbox_meta, write_turn_bind  # noqa: WPS433

    sa_id = str(item.get("sa_id") or "")
    role = str(item.get("queue_role") or "")
    try:
        q = json.loads(healthy_queue_path().read_text(encoding="utf-8"))
        total = len(queue_items(q))
    except (OSError, json.JSONDecodeError):
        total = 30

    meta = {
        "sa_id": sa_id,
        "queue_role": role,
        "queue_pos": pos,
        "queue_total": total,
        "phase": item.get("phase"),
        "upgrade_id": str(item.get("upgrade_id") or ""),
    }
    prompt = f"[GOAL1_HEALTHY_DRAIN {pos}/{total}] sa={sa_id} role={role}"

    if INBOX_JSON.is_file():
        try:
            data = json.loads(INBOX_JSON.read_text(encoding="utf-8"))
            data["meta"] = heal_inbox_meta(data.get("meta") or {}, data.get("prompt") or prompt)
            if not data["meta"].get("sa_id"):
                data["meta"] = meta
            else:
                data["meta"]["sa_id"] = sa_id
                data["meta"]["queue_role"] = role
                data["meta"]["queue_pos"] = pos
                data["meta"]["queue_total"] = total
            INBOX_JSON.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        except (OSError, json.JSONDecodeError):
            pass

    bind = write_turn_bind(meta=meta, prompt=prompt)
    deliver: dict = {}
    if force_deliver:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "healthy-drain-orchestrator-v1.py"), "deliver", "--force"],
            capture_output=True,
            text=True,
            cwd=str(ROOT),
            timeout=90,
        )
        try:
            deliver = json.loads(proc.stdout.strip())
        except json.JSONDecodeError:
            deliver = {"ok": proc.returncode == 0, "raw": (proc.stdout or "")[:500]}

    status = bind_status()
    return {
        "ok": status.get("match") or status.get("queue_sa") == sa_id,
        "healed_sa": sa_id,
        "queue_pos": pos,
        "bind": bind,
        "deliver": deliver,
        "status": status,
    }


def sync_active_now() -> dict:
    from active_now_v1 import sync_active_now_from_queue_head  # noqa: WPS433

    return sync_active_now_from_queue_head()
