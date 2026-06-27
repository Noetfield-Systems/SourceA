#!/usr/bin/env python3
"""Forge Terminal — isolated workspace jail (not whole Mac)."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
DEFAULT_NAME = os.environ.get("FORGE_WORKSPACE_NAME", "default").strip() or "default"


def workspace_root(*, name: str | None = None) -> Path:
    env = os.environ.get("FORGE_WORKSPACE_ROOT", "").strip()
    if env:
        return Path(env).expanduser().resolve()
    ws_name = (name or DEFAULT_NAME).strip() or "default"
    return (SINA / "forge-workspaces" / ws_name).resolve()


def ensure_workspace(*, name: str | None = None) -> Path:
    root = workspace_root(name=name)
    root.mkdir(parents=True, exist_ok=True)
    readme = root / "README.md"
    if not readme.is_file():
        readme.write_text(
            "# Forge workspace\n\nLLM and terminal actions are scoped to this folder only.\n",
            encoding="utf-8",
        )
    return root


def _inside_root(root: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def resolve_workspace_path(rel: str, *, name: str | None = None) -> Path | None:
    root = ensure_workspace(name=name)
    clean = (rel or "").strip().lstrip("/")
    if not clean or ".." in clean.split("/"):
        return None
    target = (root / clean).resolve()
    if not _inside_root(root, target):
        return None
    return target


def list_workspace(*, name: str | None = None, max_items: int = 80) -> dict[str, Any]:
    root = ensure_workspace(name=name)
    files: list[dict[str, Any]] = []
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = p.relative_to(root).as_posix()
        files.append({"path": rel, "size": p.stat().st_size})
        if len(files) >= max_items:
            break
    return {
        "ok": True,
        "name": name or DEFAULT_NAME,
        "root": str(root),
        "file_count": len(files),
        "files": files,
    }


def workspace_status(*, name: str | None = None) -> dict[str, Any]:
    row = list_workspace(name=name, max_items=12)
    return {
        "name": row["name"],
        "root": row["root"],
        "file_count": row["file_count"],
        "files": row["files"],
    }
