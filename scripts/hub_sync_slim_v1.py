#!/usr/bin/env python3
"""Slim hub-sync payload — no build_payload on request thread (Track 2 L3)."""
from __future__ import annotations

import json
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHELL = ROOT / "agent-control-panel" / "command-data-shell.json"
GEN = Path.home() / ".sina" / "hub-shell-generation-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _atomic_write(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    tmp.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def read_shell_generation_id() -> int:
    try:
        if SHELL.is_file():
            gid = json.loads(SHELL.read_text(encoding="utf-8")).get("generation_id")
            if gid is not None:
                return int(gid)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        pass
    try:
        if GEN.is_file():
            return int(json.loads(GEN.read_text(encoding="utf-8")).get("generation_id") or 0)
    except (OSError, json.JSONDecodeError, TypeError, ValueError):
        pass
    return 0


def bump_shell_generation_id() -> int:
    gid = read_shell_generation_id() + 1
    _atomic_write(GEN, {"schema": "hub-shell-generation-v1", "generation_id": gid, "at": _now()})
    if SHELL.is_file():
        try:
            row = json.loads(SHELL.read_text(encoding="utf-8"))
            row["generation_id"] = gid
            _atomic_write(SHELL, row)
        except (OSError, json.JSONDecodeError):
            pass
    return gid


def ensure_shell_generation_id(*, default: int = 1) -> int:
    gid = read_shell_generation_id()
    if gid > 0:
        return gid
    gid = default
    _atomic_write(GEN, {"schema": "hub-shell-generation-v1", "generation_id": gid, "at": _now()})
    if SHELL.is_file():
        try:
            row = json.loads(SHELL.read_text(encoding="utf-8"))
            row["generation_id"] = gid
            _atomic_write(SHELL, row)
        except (OSError, json.JSONDecodeError):
            pass
    return gid


def read_shell_disk() -> dict:
    if not SHELL.is_file():
        return {}
    try:
        return json.loads(SHELL.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


_HUB_SYNC_CACHE: dict = {"at": 0.0, "payload": None, "queue_pos": None}
_HUB_SYNC_TTL_SEC = 2.0


def hub_sync_payload() -> dict:
    """Flat hub-sync — shell disk + live goal1/home slices only."""
    now = time.time()
    from sina_command_lib import goal1_auto_run_payload, goal1_hub_status_bundle  # noqa: WPS433

    shell = read_shell_disk()
    g1 = goal1_auto_run_payload()
    qpos = (g1.get("queue") or {}).get("queue_pos")
    cached = _HUB_SYNC_CACHE.get("payload")
    if (
        cached
        and (now - float(_HUB_SYNC_CACHE.get("at") or 0)) < _HUB_SYNC_TTL_SEC
        and _HUB_SYNC_CACHE.get("queue_pos") == qpos
    ):
        return cached
    hfv = shell.get("home_founder_view") or {}
    try:
        from hub_home_founder_view_v1 import hub_home_founder_payload  # noqa: WPS433

        hfv = hub_home_founder_payload(hub_payload=shell or None)
    except Exception:
        pass
    gid = ensure_shell_generation_id()
    row = {
        "ok": True,
        "generation_id": gid,
        "built_at": shell.get("built_at"),
        "schema_version": shell.get("schema_version"),
        "home_founder_view": hfv,
        **goal1_hub_status_bundle(g1),
        "healthy_drain_rail": g1.get("queue") or shell.get("healthy_drain_rail") or {},
        "worker_inbox": g1.get("inbox") or shell.get("worker_inbox") or {},
        "command_center": shell.get("command_center") or {},
        "founder_advisor_discussion": shell.get("founder_advisor_discussion") or {},
    }
    _HUB_SYNC_CACHE["at"] = now
    _HUB_SYNC_CACHE["payload"] = row
    _HUB_SYNC_CACHE["queue_pos"] = qpos
    return row


def live_queue_payload() -> dict:
    from sina_command_lib import goal1_auto_run_payload  # noqa: WPS433

    g1 = goal1_auto_run_payload()
    q = g1.get("queue") or {}
    inbox = g1.get("inbox") or {}
    return {
        "ok": True,
        "generation_id": ensure_shell_generation_id(),
        "sa_id": q.get("sa_id"),
        "queue_role": q.get("queue_role"),
        "pos": q.get("queue_pos"),
        "pending": bool(inbox.get("pending")),
    }


def live_factory_payload() -> dict:
    fn: dict = {}
    try:
        fn = json.loads((Path.home() / ".sina" / "factory-now-v1.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        pass
    return {
        "ok": True,
        "generation_id": ensure_shell_generation_id(),
        "frozen": bool(fn.get("kill_flag") or fn.get("mode") == "FREEZE"),
        "mode": fn.get("mode"),
        "factory_now": fn,
    }
