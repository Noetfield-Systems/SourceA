#!/usr/bin/env python3
"""Forge Terminal desktop mesh — living chat thread + Chat Unify · Cloud Workers · Hub wire."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
THREAD_PATH = SINA / "forge-terminal-chat-thread-v1.json"
MESH_RECEIPT = SINA / "forge-terminal-desktop-mesh-v1.json"

CHAT_UNIFY_PORT = int(os.environ.get("CHAT_UNIFY_PORT", "13023"))
CLOUD_WORKERS_PORT = int(os.environ.get("CLOUD_WORKERS_PORT", "13027"))
HUB_PORT = int(os.environ.get("HUB_PORT", "13020"))
FORGE_TERMINAL_PORT = int(os.environ.get("FORGE_TERMINAL_PORT", "13029"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _probe(url: str, timeout: float = 1.5) -> dict[str, Any]:
    try:
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read(8192).decode("utf-8", errors="replace")
            body: Any = None
            try:
                body = json.loads(raw) if raw.strip() else None
            except json.JSONDecodeError:
                body = raw[:200]
            return {"ok": 200 <= resp.status < 300, "status": resp.status, "body": body, "url": url}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": str(exc.reason), "url": url}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:200], "url": url}


def _thread_key(workspace_path: str | None) -> str:
    ws = (workspace_path or "").strip() or "__global__"
    return ws


SCHEMA_V2 = "forge-terminal-chat-sessions-v2"


def _ensure_store() -> dict[str, Any]:
    store = _read_json(THREAD_PATH)
    if store.get("schema") == SCHEMA_V2 and isinstance(store.get("workspaces"), dict):
        return store
    migrated: dict[str, Any] = {"schema": SCHEMA_V2, "workspaces": {}, "updated_at": _now()}
    old_threads = store.get("threads") or {}
    for key, row in old_threads.items():
        ws_path = row.get("workspace_path") or (key if key != "__global__" else "")
        sid = "s-0001"
        migrated["workspaces"][key] = {
            "workspace_path": ws_path,
            "active_session_id": sid,
            "sessions": [
                {
                    "id": sid,
                    "title": "Chat 1",
                    "created_at": row.get("updated_at") or _now(),
                    "updated_at": row.get("updated_at") or _now(),
                    "turns": row.get("turns") or [],
                }
            ],
        }
    _write_json(THREAD_PATH, migrated)
    return migrated


def _next_session_id(sessions: list[dict[str, Any]]) -> str:
    n = 1
    existing = {s.get("id") for s in sessions}
    while f"s-{n:04d}" in existing:
        n += 1
    return f"s-{n:04d}"


def _session_row(ws: dict[str, Any], session_id: str | None) -> dict[str, Any]:
    sessions = list(ws.get("sessions") or [])
    if not sessions:
        sid = "s-0001"
        row = {"id": sid, "title": "New chat", "created_at": _now(), "updated_at": _now(), "turns": []}
        sessions.append(row)
        ws["sessions"] = sessions
        ws["active_session_id"] = sid
        return row
    sid = (session_id or ws.get("active_session_id") or sessions[-1]["id"]).strip()
    for row in sessions:
        if row.get("id") == sid:
            ws["active_session_id"] = sid
            return row
    row = sessions[0]
    ws["active_session_id"] = row["id"]
    return row


def _ensure_workspace(store: dict[str, Any], workspace_path: str | None) -> tuple[str, dict[str, Any]]:
    key = _thread_key(workspace_path)
    workspaces = store.setdefault("workspaces", {})
    ws = workspaces.get(key)
    if not ws:
        sid = "s-0001"
        ws = {
            "workspace_path": workspace_path or "",
            "active_session_id": sid,
            "sessions": [
                {"id": sid, "title": "New chat", "created_at": _now(), "updated_at": _now(), "turns": []}
            ],
        }
        workspaces[key] = ws
    return key, ws


def list_chat_sessions(*, workspace_path: str | None = None) -> dict[str, Any]:
    store = _ensure_store()
    _, ws = _ensure_workspace(store, workspace_path)
    sessions = []
    for s in ws.get("sessions") or []:
        turns = s.get("turns") or []
        sessions.append(
            {
                "id": s.get("id"),
                "title": s.get("title") or "Chat",
                "turn_count": len(turns),
                "updated_at": s.get("updated_at") or _now(),
                "created_at": s.get("created_at") or _now(),
            }
        )
    sessions.sort(key=lambda x: x.get("updated_at") or "", reverse=True)
    return {
        "ok": True,
        "schema": SCHEMA_V2,
        "workspace_path": workspace_path or "",
        "active_session_id": ws.get("active_session_id"),
        "sessions": sessions,
    }


def create_chat_session(*, workspace_path: str | None = None, title: str = "") -> dict[str, Any]:
    store = _ensure_store()
    _, ws = _ensure_workspace(store, workspace_path)
    sessions = list(ws.get("sessions") or [])
    sid = _next_session_id(sessions)
    row = {
        "id": sid,
        "title": (title or "New chat").strip()[:80] or "New chat",
        "created_at": _now(),
        "updated_at": _now(),
        "turns": [],
    }
    sessions.insert(0, row)
    ws["sessions"] = sessions
    ws["active_session_id"] = sid
    store["updated_at"] = _now()
    _write_json(THREAD_PATH, store)
    return {"ok": True, "session": row, "active_session_id": sid}


def delete_chat_session(*, workspace_path: str | None = None, session_id: str = "") -> dict[str, Any]:
    store = _ensure_store()
    _, ws = _ensure_workspace(store, workspace_path)
    sid = (session_id or "").strip()
    sessions = [s for s in (ws.get("sessions") or []) if s.get("id") != sid]
    if len(sessions) == len(ws.get("sessions") or []):
        return {"ok": False, "error": "session_not_found"}
    if not sessions:
        return create_chat_session(workspace_path=workspace_path)
    ws["sessions"] = sessions
    if ws.get("active_session_id") == sid:
        ws["active_session_id"] = sessions[0]["id"]
    store["updated_at"] = _now()
    _write_json(THREAD_PATH, store)
    return {"ok": True, "deleted": sid, "active_session_id": ws.get("active_session_id")}


def load_thread(*, workspace_path: str | None = None, session_id: str | None = None) -> dict[str, Any]:
    store = _ensure_store()
    _, ws = _ensure_workspace(store, workspace_path)
    sess = _session_row(ws, session_id)
    store["updated_at"] = _now()
    _write_json(THREAD_PATH, store)
    return {
        "ok": True,
        "schema": SCHEMA_V2,
        "workspace_path": workspace_path or "",
        "session_id": sess.get("id"),
        "session_title": sess.get("title") or "Chat",
        "active_session_id": ws.get("active_session_id"),
        "turns": sess.get("turns") or [],
        "updated_at": sess.get("updated_at") or _now(),
    }


def append_turn(
    *,
    workspace_path: str | None,
    role: str,
    text: str,
    meta: dict[str, Any] | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    store = _ensure_store()
    _, ws = _ensure_workspace(store, workspace_path)
    row = _session_row(ws, session_id)
    turn = {
        "id": f"t-{len(row.get('turns') or []) + 1:04d}",
        "role": role,
        "text": text,
        "at": _now(),
        "meta": meta or {},
    }
    turns = list(row.get("turns") or [])
    turns.append(turn)
    row["turns"] = turns[-200:]
    row["updated_at"] = _now()
    if role == "user" and (row.get("title") or "New chat") in ("New chat", "Chat 1") and text.strip():
        row["title"] = text.strip()[:48] + ("…" if len(text.strip()) > 48 else "")
    store["updated_at"] = _now()
    _write_json(THREAD_PATH, store)
    return {
        "ok": True,
        "turn": turn,
        "turn_count": len(row["turns"]),
        "session_id": row.get("id"),
        "session_title": row.get("title"),
    }


def clear_thread(
    *,
    workspace_path: str | None = None,
    session_id: str | None = None,
) -> dict[str, Any]:
    store = _ensure_store()
    _, ws = _ensure_workspace(store, workspace_path)
    row = _session_row(ws, session_id)
    row["turns"] = []
    row["updated_at"] = _now()
    store["updated_at"] = _now()
    _write_json(THREAD_PATH, store)
    return {
        "ok": True,
        "cleared": True,
        "workspace_path": workspace_path or "",
        "session_id": row.get("id"),
    }


def _mesh_probes(*, timeout: float = 1.5, parallel: bool = False) -> dict[str, dict[str, Any]]:
    targets = {
        "chat": f"http://127.0.0.1:{CHAT_UNIFY_PORT}/health",
        "chat_forge": f"http://127.0.0.1:{CHAT_UNIFY_PORT}/api/forge-terminal/v1?status=1&light=1",
        "cloud": f"http://127.0.0.1:{CLOUD_WORKERS_PORT}/health",
        "hub": f"http://127.0.0.1:{HUB_PORT}/health",
        "forge_self": f"http://127.0.0.1:{FORGE_TERMINAL_PORT}/health",
        "integrations": f"http://127.0.0.1:{CHAT_UNIFY_PORT}/api/integrations/v1",
    }
    if not parallel:
        return {name: _probe(url, timeout=timeout) for name, url in targets.items()}
    from concurrent.futures import ThreadPoolExecutor

    out: dict[str, dict[str, Any]] = {}
    with ThreadPoolExecutor(max_workers=len(targets)) as pool:
        futs = {name: pool.submit(_probe, url, timeout) for name, url in targets.items()}
        for name, fut in futs.items():
            try:
                out[name] = fut.result()
            except Exception as exc:
                out[name] = {"ok": False, "status": 0, "body": str(exc)[:120], "url": targets[name]}
    return out


def _mesh_payload_from_probes(probes: dict[str, dict[str, Any]]) -> dict[str, Any]:
    chat = probes.get("chat") or {}
    chat_forge = probes.get("chat_forge") or {}
    cloud = probes.get("cloud") or {}
    hub = probes.get("hub") or {}
    forge_self = probes.get("forge_self") or {}
    integrations = probes.get("integrations") or {}

    def _live(probe: dict[str, Any]) -> str:
        if probe.get("ok"):
            return "live"
        if probe.get("status"):
            return "degraded"
        return "offline"

    peers = [
        {
            "id": "forge_terminal",
            "label": "Forge Terminal",
            "port": FORGE_TERMINAL_PORT,
            "status": _live(forge_self),
            "url": f"http://127.0.0.1:{FORGE_TERMINAL_PORT}/terminal/",
            "app": "Forge Terminal.app",
            "role": "living_chat_ide",
        },
        {
            "id": "chat_unify",
            "label": "Chat Unify",
            "port": CHAT_UNIFY_PORT,
            "status": _live(chat),
            "url": f"http://127.0.0.1:{CHAT_UNIFY_PORT}/",
            "app": "Chat Unify.app",
            "role": "mobile_forge_api_connect",
            "forge_api": chat_forge.get("ok"),
        },
        {
            "id": "cloud_workers",
            "label": "Cloud Workers",
            "port": CLOUD_WORKERS_PORT,
            "status": _live(cloud),
            "url": f"http://127.0.0.1:{CLOUD_WORKERS_PORT}/",
            "app": "Cloud Workers.app",
            "role": "railway_factory_body",
            "dispatch": f"http://127.0.0.1:{CLOUD_WORKERS_PORT}/api/cloud-worker/dispatch/v1",
        },
        {
            "id": "hub",
            "label": "SourceA Hub",
            "port": HUB_PORT,
            "status": _live(hub),
            "url": f"http://127.0.0.1:{HUB_PORT}/",
            "app": "Hub control panel",
            "role": "mac_control_plane",
        },
    ]

    live_count = sum(1 for p in peers if p["status"] == "live")
    return {
        "ok": live_count >= 2,
        "schema": "forge-terminal-desktop-mesh-v1",
        "at": _now(),
        "live_peers": live_count,
        "total_peers": len(peers),
        "peers": peers,
        "mesh_ready": chat.get("ok") and (cloud.get("ok") or forge_self.get("ok")),
        "chat_unify_forge": chat_forge.get("body") if isinstance(chat_forge.get("body"), dict) else {},
        "integrations_ok": bool(integrations.get("ok")),
        "open_urls": {p["id"]: p["url"] for p in peers},
    }


def desktop_mesh_status(*, ensure_peers: bool = False, fast: bool = False) -> dict[str, Any]:
    if ensure_peers:
        try:
            import sys
            from pathlib import Path as P

            root = P(__file__).resolve().parents[1]
            sys.path.insert(0, str(root / "scripts"))
            from forge_terminal_os_bridge_v1 import ensure_chat_unify  # noqa: WPS433

            ensure_chat_unify()
        except Exception:
            pass

    timeout = 0.35 if fast else 1.5
    probes = _mesh_probes(timeout=timeout, parallel=fast)
    payload = _mesh_payload_from_probes(probes)
    if not fast:
        _write_json(MESH_RECEIPT, payload)
    return payload


def peer_dispatch(*, peer: str, body: dict[str, Any]) -> dict[str, Any]:
    peer = (peer or "").strip().lower()
    if peer in ("chat_unify", "chat-unify", "13023"):
        url = f"http://127.0.0.1:{CHAT_UNIFY_PORT}/api/chat-unify"
        payload = body.get("payload") or body
        if not payload.get("action"):
            payload = {"action": "prompt_forge", "text": str(body.get("text") or ""), **payload}
    elif peer in ("cloud_workers", "cloud-workers", "13027"):
        url = f"http://127.0.0.1:{CLOUD_WORKERS_PORT}/api/cloud-worker/dispatch/v1"
        payload = body.get("dispatch") or body.get("payload") or {
            "kind": body.get("kind") or "forge_terminal_mesh",
            "source": "forge_terminal_v1",
            "text": str(body.get("text") or ""),
            "run_id": body.get("run_id"),
            "dry_run": bool(body.get("dry_run", True)),
        }
    elif peer in ("integrations", "chat_unify_connect"):
        url = f"http://127.0.0.1:{CHAT_UNIFY_PORT}/api/integrations/v1"
        payload = body.get("payload") or {"action": "refresh"}
    else:
        return {"ok": False, "error": "unknown_peer", "peer": peer}

    data = json.dumps(payload).encode("utf-8")
    try:
        req = urllib.request.Request(
            url,
            data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            raw = resp.read(16384).decode("utf-8", errors="replace")
            try:
                parsed = json.loads(raw)
            except json.JSONDecodeError:
                parsed = {"raw": raw[:500]}
            return {"ok": True, "peer": peer, "url": url, "response": parsed}
    except urllib.error.HTTPError as exc:
        err_body = exc.read(4096).decode("utf-8", errors="replace")
        return {"ok": False, "peer": peer, "error": "http_error", "status": exc.code, "body": err_body[:500]}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "peer": peer, "error": type(exc).__name__, "message": str(exc)[:300]}
