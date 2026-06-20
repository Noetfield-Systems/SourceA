"""L0/L1 — user signals + workspace state SSOT."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA_HOME = Path.home() / ".sina"
SIGNALS_PATH = SINA_HOME / "user_signals_v1.json"
WORKSPACE_PATH = SINA_HOME / "workspace_state_v1.json"
SCHEMA = "user-workspace-signals-v1"
_HUB_REFRESH_SOURCES = frozenset({"refresh", "hub_build", "hub_self_refresh"})


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}


def _write(path: Path, payload: dict) -> None:
    SINA_HOME.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def load_signals() -> dict[str, Any]:
    data = _read(SIGNALS_PATH)
    if data.get("schema") != SCHEMA:
        return {
            "schema": SCHEMA,
            "generated_at": None,
            "signals": [],
            "last_hub_tab": None,
            "last_refresh_at": None,
        }
    return data


def load_workspace_state() -> dict[str, Any]:
    data = _read(WORKSPACE_PATH)
    if data.get("schema") != SCHEMA:
        return {
            "schema": SCHEMA,
            "generated_at": None,
            "active_repo": None,
            "active_thread": None,
            "hub_tab": None,
            "loop_round": None,
            "open_files": [],
        }
    return data


def record_hub_touch(
    *,
    hub_tab: str = "",
    active_repo: str = "",
    active_thread: str = "",
    loop_round: int | None = None,
    source: str = "hub",
) -> dict[str, Any]:
    now = _now()
    sig = load_signals()
    row = {
        "at": now,
        "hub_tab": hub_tab or None,
        "source": source,
    }
    signals = list(sig.get("signals") or [])
    signals.append(row)
    sig.update(
        {
            "schema": SCHEMA,
            "generated_at": now,
            "signals": signals[-120:],
            "last_hub_tab": hub_tab or sig.get("last_hub_tab"),
            "last_refresh_at": now if source in _HUB_REFRESH_SOURCES else sig.get("last_refresh_at"),
        }
    )
    _write(SIGNALS_PATH, sig)

    ws = load_workspace_state()
    ws.update(
        {
            "schema": SCHEMA,
            "generated_at": now,
            "hub_tab": hub_tab or ws.get("hub_tab"),
            "active_repo": active_repo or ws.get("active_repo"),
            "active_thread": active_thread or ws.get("active_thread"),
            "loop_round": loop_round if loop_round is not None else ws.get("loop_round"),
            "open_files": ws.get("open_files") or [],
        }
    )
    _write(WORKSPACE_PATH, ws)
    return {"signals": sig, "workspace": ws}


def record_workspace_files(files: list[str], *, source: str = "hub") -> dict[str, Any]:
    now = _now()
    ws = load_workspace_state()
    clean = [f for f in files if f and isinstance(f, str)][:24]
    ws.update(
        {
            "schema": SCHEMA,
            "generated_at": now,
            "open_files": clean,
        }
    )
    _write(WORKSPACE_PATH, ws)
    sig = load_signals()
    signals = list(sig.get("signals") or [])
    signals.append({"at": now, "hub_tab": "workspace", "source": source, "files": len(clean)})
    sig.update(
        {
            "schema": SCHEMA,
            "generated_at": now,
            "signals": signals[-120:],
        }
    )
    _write(SIGNALS_PATH, sig)
    return {"signals": sig, "workspace": ws}


def hub_payload() -> dict[str, Any]:
    sig = load_signals()
    ws = load_workspace_state()
    n = len(sig.get("signals") or [])
    live = n > 0 and bool(sig.get("last_hub_tab") or sig.get("last_refresh_at"))
    return {
        "ok": True,
        "schema": SCHEMA,
        "api": "/api/user-workspace-signals-v1",
        "producer": "L0+L1",
        "signals_path": str(SIGNALS_PATH),
        "workspace_path": str(WORKSPACE_PATH),
        "signal_count": n,
        "l0_status": "done" if live else "missing",
        "l1_status": "done" if ws.get("hub_tab") or ws.get("active_repo") else "partial",
        "user_signals": sig,
        "workspace_state": ws,
    }


def packet_workspace_slice() -> dict[str, Any]:
    ws = load_workspace_state()
    sig = load_signals()
    return {
        "active_files": list(ws.get("open_files") or [])[:12],
        "session_focus": ws.get("active_thread") or ws.get("hub_tab"),
        "hub_tab": ws.get("hub_tab"),
        "active_repo": ws.get("active_repo"),
        "loop_round": ws.get("loop_round"),
        "last_signal_at": sig.get("generated_at"),
        "producer": "L0,L1",
    }
