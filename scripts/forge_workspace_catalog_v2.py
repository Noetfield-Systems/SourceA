#!/usr/bin/env python3
"""Forge IDE workspace catalog — VIRELUX · Noetfield · WitnessBC · 777 Foundation."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
FORGE_WS = SINA / "forge-workspaces"

CATALOG: dict[str, dict[str, str]] = {
    "virelux": {
        "label": "VIRELUX",
        "slug": "virelux",
        "profile": "startup",
    },
    "noetfield": {
        "label": "Noetfield",
        "slug": "noetfield",
        "profile": "startup",
    },
    "witnessbc": {
        "label": "WitnessBC",
        "slug": "witnessbc",
        "profile": "compliance",
    },
    "777": {
        "label": "777 Foundation",
        "slug": "777-foundation",
        "profile": "foundation",
    },
}


def _default_path(workspace_id: str) -> Path:
    meta = CATALOG.get(workspace_id) or {}
    slug = meta.get("slug") or workspace_id
    # VIRELUX pilot lives in repo labs for ship proof
    if workspace_id == "virelux":
        repo = ROOT / "labs" / "virelux-pilot"
        if (repo / ".sourcea" / "project.yaml").is_file():
            return repo.resolve()
    return (FORGE_WS / slug).resolve()


def resolve_workspace_path(workspace_id: str) -> Path:
    env_key = f"FORGE_WS_{workspace_id.upper()}_PATH"
    override = os.environ.get(env_key, "").strip()
    if override:
        return Path(override).expanduser().resolve()
    return _default_path(workspace_id)


def ensure_workspace_ready(workspace_id: str) -> dict[str, Any]:
    from workspace_kernel_v2 import init_workspace, workspace_ready  # noqa: WPS433

    path = resolve_workspace_path(workspace_id)
    ready = workspace_ready(path)
    if not ready["ok"]:
        meta = CATALOG.get(workspace_id, {})
        init_workspace(
            path,
            name=meta.get("slug") or workspace_id,
            profile=meta.get("profile") or "startup",
            overwrite=False,
        )
        ready = workspace_ready(path)
    return {
        "id": workspace_id,
        "label": CATALOG.get(workspace_id, {}).get("label") or workspace_id,
        "path": str(path),
        "ready": ready["ok"],
        "missing": ready.get("missing") or [],
    }


def list_workspaces() -> dict[str, Any]:
    rows = [ensure_workspace_ready(wid) for wid in CATALOG]
    return {"ok": True, "workspaces": rows, "default": "virelux"}


def resolve_for_request(workspace_id: str | None) -> Path | None:
    wid = (workspace_id or os.environ.get("FORGE_WORKSPACE_ID") or "virelux").strip().lower()
    if wid not in CATALOG:
        wid = "virelux"
    row = ensure_workspace_ready(wid)
    if row["ready"]:
        return Path(row["path"])
    return None
