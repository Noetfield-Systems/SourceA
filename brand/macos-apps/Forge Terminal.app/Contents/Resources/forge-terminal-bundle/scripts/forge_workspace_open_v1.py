#!/usr/bin/env python3
"""Forge IDE — open-folder workspace session (Cursor-style, path is SSOT)."""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
SESSION_PATH = SINA / "forge-terminal-session-v1.json"
MAX_RECENT = 12
SKIP_DIRS = frozenset(
    {
        ".git",
        "node_modules",
        "__pycache__",
        "dist",
        "build",
        ".venv",
        "venv",
        ".next",
        "receipts",
        ".cursor",
    }
)
_CONTEXT_CACHE: dict[str, tuple[float, str]] = {}
CONTEXT_TTL_S = 30.0


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def read_session() -> dict[str, Any]:
    if not SESSION_PATH.is_file():
        return {"schema": "forge-terminal-session-v1", "active_path": "", "recent": []}
    try:
        row = json.loads(SESSION_PATH.read_text(encoding="utf-8"))
        if isinstance(row, dict):
            row.setdefault("recent", [])
            return row
    except Exception:
        pass
    return {"schema": "forge-terminal-session-v1", "active_path": "", "recent": []}


def write_session(row: dict[str, Any]) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    SESSION_PATH.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def active_path() -> Path | None:
    env = os.environ.get("FORGE_WORKSPACE_ROOT", "").strip() or os.environ.get("SOURCEA_WORKSPACE_ROOT", "").strip()
    if env:
        p = Path(env).expanduser().resolve()
        if p.is_dir():
            return p
    raw = (read_session().get("active_path") or "").strip()
    if not raw:
        return None
    p = Path(raw).expanduser().resolve()
    return p if p.is_dir() else None


def list_recent() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for item in read_session().get("recent") or []:
        if isinstance(item, str):
            path = item
            name = Path(path).name
        elif isinstance(item, dict):
            path = str(item.get("path") or "")
            name = str(item.get("name") or Path(path).name)
        else:
            continue
        path = str(Path(path).expanduser().resolve()) if path else ""
        if not path or path in seen:
            continue
        if not Path(path).is_dir():
            continue
        seen.add(path)
        out.append({"path": path, "name": name or Path(path).name})
    return out[:MAX_RECENT]


def _touch_recent(session: dict[str, Any], path: Path) -> None:
    entry = {"path": str(path), "name": path.name, "opened_at": _now()}
    recent = [entry]
    for item in session.get("recent") or []:
        p = item if isinstance(item, str) else (item.get("path") if isinstance(item, dict) else "")
        if not p or str(Path(p).resolve()) == str(path):
            continue
        recent.append(item if isinstance(item, dict) else {"path": p, "name": Path(p).name})
        if len(recent) >= MAX_RECENT:
            break
    session["recent"] = recent


def open_folder(path: str, *, auto_init: bool = True, profile: str = "startup") -> dict[str, Any]:
    """Validate folder, bootstrap .sourcea if needed, persist session."""
    raw = (path or "").strip()
    if not raw:
        return {"ok": False, "error": "empty_path", "message": "Choose a folder to open."}

    project_root = Path(raw).expanduser().resolve()
    if not project_root.is_dir():
        return {
            "ok": False,
            "error": "not_a_directory",
            "message": f"Not a folder: {project_root}",
            "path": str(project_root),
        }

    from workspace_kernel_v2 import init_workspace, kernel_status, workspace_ready  # noqa: WPS433

    ready = workspace_ready(project_root)
    initialized = False
    if not ready["ok"]:
        if not auto_init:
            return {
                "ok": False,
                "error": "workspace_not_ready",
                "message": "Folder has no .sourcea workspace. Open with auto-init or run init-sourcea-workspace-v2.sh.",
                "missing": ready.get("missing") or [],
                "path": str(project_root),
            }
        init_row = init_workspace(project_root, name=project_root.name, profile=profile)
        if not init_row.get("ok"):
            return {
                "ok": False,
                "error": "init_failed",
                "message": init_row.get("message") or "Could not initialize .sourcea in folder.",
                "path": str(project_root),
            }
        initialized = True
        ready = workspace_ready(project_root)

    session = read_session()
    session["active_path"] = str(project_root)
    session["opened_at"] = _now()
    _touch_recent(session, project_root)
    write_session(session)

    scan = scan_workspace(project_root)
    return {
        "ok": True,
        "schema": "forge-open-folder-v1",
        "path": str(project_root),
        "name": project_root.name,
        "initialized": initialized,
        "kernel": kernel_status(project_root),
        "scan": scan,
        "recent": list_recent(),
    }


def scan_workspace(
    project_root: Path,
    *,
    max_entries: int = 100,
    max_depth: int = 2,
) -> dict[str, Any]:
    """Fast project tree + key file snippets for LLM pre-context."""
    project_root = project_root.expanduser().resolve()
    entries: list[dict[str, Any]] = []

    def walk(directory: Path, depth: int) -> None:
        if depth > max_depth or len(entries) >= max_entries:
            return
        try:
            children = sorted(directory.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except (OSError, PermissionError):
            return
        for child in children:
            if child.name in SKIP_DIRS:
                continue
            if child.name.startswith(".") and child.name != ".sourcea":
                continue
            rel = str(child.relative_to(project_root))
            entries.append({"name": child.name, "path": rel, "dir": child.is_dir()})
            if len(entries) >= max_entries:
                return
            if child.is_dir() and depth < max_depth:
                walk(child, depth + 1)

    if project_root.is_dir():
        walk(project_root, 0)

    context_parts: list[str] = []
    key_paths = (
        project_root / "README.md",
        project_root / "package.json",
        project_root / "pyproject.toml",
        project_root / ".sourcea" / "project.yaml",
        project_root / "apps" / "README.md",
    )
    for fp in key_paths:
        if not fp.is_file():
            continue
        try:
            snippet = fp.read_text(encoding="utf-8", errors="replace")[:1200]
        except OSError:
            continue
        rel = fp.relative_to(project_root)
        context_parts.append(f"--- {rel} ---\n{snippet}")

    top_names = [e["name"] for e in entries[:24]]
    summary = f"Top-level: {', '.join(top_names)}" if top_names else "Empty folder"

    return {
        "entries": entries,
        "entry_count": len(entries),
        "summary": summary,
        "context_preview": "\n\n".join(context_parts)[:4500],
    }


def workspace_context_for_llm(project_root: Path) -> str:
    """Cached project context injected before every LLM call."""
    import time

    key = str(project_root.resolve())
    now = time.time()
    cached = _CONTEXT_CACHE.get(key)
    if cached and (now - cached[0]) < CONTEXT_TTL_S:
        return cached[1]
    scan = scan_workspace(project_root, max_entries=60, max_depth=2)
    ctx = scan.get("context_preview") or scan.get("summary") or f"Project: {project_root.name}"
    block = f"{scan.get('summary', '')}\n\n{ctx}".strip()
    _CONTEXT_CACHE[key] = (now, block[:5000])
    return block[:5000]


def clear_session() -> dict[str, Any]:
    session = read_session()
    session["active_path"] = ""
    write_session(session)
    return {"ok": True, "recent": list_recent()}
