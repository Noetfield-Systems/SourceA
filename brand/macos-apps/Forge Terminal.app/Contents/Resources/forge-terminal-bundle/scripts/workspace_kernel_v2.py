#!/usr/bin/env python3
"""SourceA Workspace Kernel V2 — manifest · agents · tasks · events · state.

Install on any project:
  project/.sourcea/{project.yaml,agents.yaml,models.yaml,policies.yaml,tasks.db,receipts/}

Flow: Founder → Task → Kernel → Agent → Execution → Receipt → State Update
V1 Forge Terminal remains; kernel hooks emit events without replacing chat path.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / "templates" / "sourcea-workspace-v2"
SOURCEA_DIR = ".sourcea"

REQUIRED_PATHS = (
    "project.yaml",
    "agents.yaml",
    "models.yaml",
    "policies.yaml",
    "tasks.db",
    "receipts",
)

EVENT_TYPES = (
    "TASK_CREATED",
    "TASK_APPROVED",
    "TASK_REJECTED",
    "TASK_REVISE",
    "TASK_EXECUTING",
    "TASK_COMPLETED",
    "TASK_FAILED",
    "WORKSPACE_INIT",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_yaml(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    raw = path.read_text(encoding="utf-8")
    try:
        import yaml  # type: ignore

        doc = yaml.safe_load(raw)
        return doc if isinstance(doc, dict) else {}
    except Exception:
        return {}


def find_workspace_root(start: Path | None = None) -> Path | None:
    """Walk up from start (or cwd) until .sourcea/project.yaml exists."""
    env = os.environ.get("SOURCEA_WORKSPACE_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if (p / SOURCEA_DIR / "project.yaml").is_file():
            return p
    cur = (start or Path.cwd()).resolve()
    for _ in range(32):
        if (cur / SOURCEA_DIR / "project.yaml").is_file():
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def sourcea_dir(project_root: Path) -> Path:
    return project_root / SOURCEA_DIR


def _db_path(project_root: Path) -> Path:
    return sourcea_dir(project_root) / "tasks.db"


def _connect(project_root: Path) -> sqlite3.Connection:
    db = _db_path(project_root)
    db.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db))
    conn.row_factory = sqlite3.Row
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            task_id TEXT PRIMARY KEY,
            type TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            owner TEXT NOT NULL DEFAULT 'builder',
            approval INTEGER NOT NULL DEFAULT 1,
            founder_text TEXT,
            run_id TEXT,
            payload_json TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            task_id TEXT,
            run_id TEXT,
            payload_json TEXT,
            at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS state (
            key TEXT PRIMARY KEY,
            value_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """
    )
    conn.commit()


def workspace_ready(project_root: Path) -> dict[str, Any]:
    sa = sourcea_dir(project_root)
    missing = [p for p in REQUIRED_PATHS if not (sa / p).exists()]
    return {
        "ok": len(missing) == 0,
        "project_root": str(project_root),
        "sourcea": str(sa),
        "missing": missing,
    }


def init_workspace(
    project_root: Path,
    *,
    name: str = "workspace",
    profile: str = "startup",
    overwrite: bool = False,
) -> dict[str, Any]:
    """Bootstrap mandatory .sourcea/ tree from templates."""
    project_root = project_root.expanduser().resolve()
    sa = sourcea_dir(project_root)
    sa.mkdir(parents=True, exist_ok=True)
    (sa / "receipts").mkdir(exist_ok=True)
    (sa / "agents").mkdir(exist_ok=True)
    (sa / "tasks").mkdir(exist_ok=True)
    (sa / "runs").mkdir(exist_ok=True)

    copied: list[str] = []
    for rel in ("project.yaml", "agents.yaml", "models.yaml", "policies.yaml"):
        dst = sa / rel
        if dst.exists() and not overwrite:
            continue
        src = TEMPLATES / rel
        if src.is_file():
            text = src.read_text(encoding="utf-8")
            if name != "virelux" and rel == "project.yaml":
                text = re.sub(r"^name: .*$", f"name: {name}", text, count=1, flags=re.M)
                text = re.sub(r"^type: .*$", f"type: {profile}", text, count=1, flags=re.M)
            dst.write_text(text, encoding="utf-8")
            copied.append(rel)

    for agent_file in ("planner.yaml", "builder.yaml", "verifier.yaml"):
        dst = sa / "agents" / agent_file
        if dst.exists() and not overwrite:
            continue
        src = TEMPLATES / "agents" / agent_file
        if src.is_file():
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
            copied.append(f"agents/{agent_file}")

    conn = _connect(project_root)
    _init_db(conn)
    conn.close()

    emit_event(project_root, "WORKSPACE_INIT", payload={"name": name, "profile": profile, "copied": copied})
    return {
        "ok": True,
        "project_root": str(project_root),
        "sourcea": str(sa),
        "copied": copied,
        "ready": workspace_ready(project_root),
    }


def load_manifest(project_root: Path) -> dict[str, Any]:
    sa = sourcea_dir(project_root)
    project = _load_yaml(sa / "project.yaml")
    return {
        "ok": bool(project),
        "project_root": str(project_root),
        "project": project,
        "agents": _load_yaml(sa / "agents.yaml"),
        "models": _load_yaml(sa / "models.yaml"),
        "policies": _load_yaml(sa / "policies.yaml"),
    }


def _next_task_id(conn: sqlite3.Connection) -> str:
    row = conn.execute("SELECT COUNT(*) AS c FROM tasks").fetchone()
    n = int(row["c"] if row else 0) + 1
    return f"TASK-{n:03d}"


def create_task(
    project_root: Path,
    *,
    task_type: str,
    founder_text: str = "",
    owner: str = "builder",
    approval: bool = True,
    run_id: str = "",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    conn = _connect(project_root)
    _init_db(conn)
    task_id = _next_task_id(conn)
    now = _now()
    conn.execute(
        """
        INSERT INTO tasks (task_id, type, status, owner, approval, founder_text, run_id, payload_json, created_at, updated_at)
        VALUES (?, ?, 'pending', ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            task_id,
            task_type,
            owner,
            1 if approval else 0,
            founder_text[:8000],
            run_id,
            json.dumps(payload or {}, ensure_ascii=False),
            now,
            now,
        ),
    )
    conn.commit()
    conn.close()
    emit_event(
        project_root,
        "TASK_CREATED",
        task_id=task_id,
        run_id=run_id,
        payload={"type": task_type, "owner": owner, "approval": approval},
    )
    return get_task(project_root, task_id)


def get_task(project_root: Path, task_id: str) -> dict[str, Any]:
    conn = _connect(project_root)
    _init_db(conn)
    row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    conn.close()
    if not row:
        return {"ok": False, "error": "task_not_found", "task_id": task_id}
    return {"ok": True, "task": _task_row(dict(row))}


def _task_row(row: dict) -> dict[str, Any]:
    payload = {}
    try:
        payload = json.loads(row.get("payload_json") or "{}")
    except json.JSONDecodeError:
        payload = {}
    return {
        "task_id": row["task_id"],
        "type": row["type"],
        "status": row["status"],
        "owner": row["owner"],
        "approval": bool(row["approval"]),
        "founder_text": row.get("founder_text") or "",
        "run_id": row.get("run_id") or "",
        "payload": payload,
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


def update_task_status(
    project_root: Path,
    task_id: str,
    status: str,
    *,
    event_type: str | None = None,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    conn = _connect(project_root)
    _init_db(conn)
    now = _now()
    cur = conn.execute(
        "UPDATE tasks SET status = ?, updated_at = ? WHERE task_id = ?",
        (status, now, task_id),
    )
    conn.commit()
    row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    conn.close()
    if cur.rowcount == 0:
        return {"ok": False, "error": "task_not_found", "task_id": task_id}
    et = event_type or f"TASK_{status.upper()}"
    if et not in EVENT_TYPES:
        et = "TASK_EXECUTING"
    emit_event(project_root, et, task_id=task_id, run_id=dict(row)["run_id"] if row else "", payload=extra or {})
    return {"ok": True, "task": _task_row(dict(row)) if row else {}}


def list_tasks(project_root: Path, *, limit: int = 50, status: str | None = None) -> dict[str, Any]:
    conn = _connect(project_root)
    _init_db(conn)
    if status:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?",
            (status, limit),
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
    conn.close()
    return {"ok": True, "tasks": [_task_row(dict(r)) for r in rows]}


def emit_event(
    project_root: Path,
    event_type: str,
    *,
    task_id: str = "",
    run_id: str = "",
    payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    conn = _connect(project_root)
    _init_db(conn)
    at = _now()
    conn.execute(
        "INSERT INTO events (event_type, task_id, run_id, payload_json, at) VALUES (?, ?, ?, ?, ?)",
        (event_type, task_id or None, run_id or None, json.dumps(payload or {}, ensure_ascii=False), at),
    )
    conn.commit()
    conn.close()
    return {"ok": True, "event_type": event_type, "task_id": task_id, "run_id": run_id, "at": at}


def tail_events(project_root: Path, *, limit: int = 30) -> dict[str, Any]:
    conn = _connect(project_root)
    _init_db(conn)
    rows = conn.execute(
        "SELECT event_type, task_id, run_id, payload_json, at FROM events ORDER BY id DESC LIMIT ?",
        (limit,),
    ).fetchall()
    conn.close()
    events = []
    for r in rows:
        try:
            payload = json.loads(r["payload_json"] or "{}")
        except json.JSONDecodeError:
            payload = {}
        events.append(
            {
                "event_type": r["event_type"],
                "task_id": r["task_id"],
                "run_id": r["run_id"],
                "payload": payload,
                "at": r["at"],
            }
        )
    return {"ok": True, "events": list(reversed(events))}


def write_receipt(project_root: Path, *, run_id: str, payload: dict[str, Any]) -> Path:
    sa = sourcea_dir(project_root)
    rec_dir = sa / "receipts"
    rec_dir.mkdir(parents=True, exist_ok=True)
    safe = re.sub(r"[^\w\-]", "_", run_id)[:64] or uuid.uuid4().hex[:12]
    path = rec_dir / f"{safe}.json"
    doc = {"schema": "sourcea-workspace-receipt-v2", "run_id": run_id, "at": _now(), "payload": payload}
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def list_receipts(project_root: Path, *, limit: int = 30) -> dict[str, Any]:
    rec_dir = sourcea_dir(project_root) / "receipts"
    if not rec_dir.is_dir():
        return {"ok": True, "receipts": []}
    files = sorted(rec_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)[:limit]
    rows: list[dict[str, Any]] = []
    for fp in files:
        try:
            doc = json.loads(fp.read_text(encoding="utf-8"))
            rows.append(
                {
                    "file": fp.name,
                    "run_id": doc.get("run_id"),
                    "at": doc.get("at"),
                    "preview": str(doc.get("payload", {}))[:200],
                }
            )
        except (OSError, json.JSONDecodeError):
            rows.append({"file": fp.name, "run_id": None, "at": None, "preview": ""})
    return {"ok": True, "receipts": rows}


def list_agents(project_root: Path) -> dict[str, Any]:
    manifest = load_manifest(project_root)
    agents_doc = manifest.get("agents") or {}
    agents = agents_doc.get("agents") if isinstance(agents_doc, dict) else {}
    rows = []
    if isinstance(agents, dict):
        for aid, meta in agents.items():
            if isinstance(meta, dict):
                rows.append({"id": aid, **meta})
    return {"ok": True, "agents": rows}


def kernel_status(project_root: Path | None = None) -> dict[str, Any]:
    root = project_root or find_workspace_root()
    if not root:
        return {"ok": False, "error": "no_workspace", "hint": "Run init-sourcea-workspace-v2.sh <path> <name>"}
    ready = workspace_ready(root)
    manifest = load_manifest(root)
    tasks = list_tasks(root, limit=5)
    events = tail_events(root, limit=8)
    return {
        "ok": ready["ok"],
        "schema": "workspace-kernel-status-v2",
        "project_root": str(root),
        "ready": ready,
        "manifest": manifest,
        "recent_tasks": tasks.get("tasks") or [],
        "recent_events": events.get("events") or [],
    }


def sync_forge_run(
    project_root: Path,
    *,
    phase: str,
    run_id: str,
    founder_text: str = "",
    decision: str = "",
    success: bool | None = None,
    error: str = "",
) -> dict[str, Any] | None:
    """Thin bridge: map Forge Terminal V1 phases → kernel tasks/events."""
    if not workspace_ready(project_root)["ok"]:
        return None
    phase = phase.lower()
    if phase == "run":
        return create_task(
            project_root,
            task_type="forge_mission",
            founder_text=founder_text,
            owner="planner",
            approval=True,
            run_id=run_id,
            payload={"source": "forge_terminal_v1"},
        )
    conn = _connect(project_root)
    _init_db(conn)
    row = conn.execute(
        "SELECT task_id FROM tasks WHERE run_id = ? ORDER BY created_at DESC LIMIT 1",
        (run_id,),
    ).fetchone()
    conn.close()
    if not row:
        return None
    task_id = row["task_id"]
    dec = (decision or "").lower()
    if phase == "decide":
        if dec == "approved":
            return update_task_status(project_root, task_id, "approved", event_type="TASK_APPROVED")
        if dec == "rejected":
            return update_task_status(project_root, task_id, "rejected", event_type="TASK_REJECTED")
        if dec == "revise":
            return update_task_status(project_root, task_id, "revise", event_type="TASK_REVISE")
    if phase == "execute_start":
        return update_task_status(project_root, task_id, "executing", event_type="TASK_EXECUTING")
    if phase == "execute_done":
        st = "completed" if success else "failed"
        et = "TASK_COMPLETED" if success else "TASK_FAILED"
        rec = write_receipt(
            project_root,
            run_id=run_id,
            payload={"success": success, "error": error[:500] if error else None},
        )
        out = update_task_status(
            project_root,
            task_id,
            st,
            event_type=et,
            extra={"receipt": str(rec)},
        )
        return out
    return None


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="SourceA Workspace Kernel V2")
    ap.add_argument("command", choices=["init", "status", "tasks", "events"])
    ap.add_argument("--path", default=".")
    ap.add_argument("--name", default="workspace")
    ap.add_argument("--profile", default="startup")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    root = Path(args.path).expanduser().resolve()
    if args.command == "init":
        out = init_workspace(root, name=args.name, profile=args.profile)
    elif args.command == "status":
        out = kernel_status(root if (root / SOURCEA_DIR / "project.yaml").is_file() else None)
    elif args.command == "tasks":
        out = list_tasks(root)
    else:
        out = tail_events(root)
    print(json.dumps(out, indent=2, ensure_ascii=False))
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
