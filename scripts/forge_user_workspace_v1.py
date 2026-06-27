#!/usr/bin/env python3
"""Provision per-user Forge workspaces under ~/.sina/forge-workspaces/."""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
WORKSPACES_ROOT = SINA / "forge-workspaces"
SESSION_PATH = SINA / "sourcea-platform-session-v1.json"
SESSION_SCHEMA = "sourcea-platform-session-v1"


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def slugify(text: str) -> str:
    raw = (text or "").strip().lower()
    slug = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return slug[:48] or "my-project"


def read_platform_session() -> dict[str, Any]:
    if not SESSION_PATH.is_file():
        return {"schema": SESSION_SCHEMA}
    try:
        row = json.loads(SESSION_PATH.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else {"schema": SESSION_SCHEMA}
    except Exception:
        return {"schema": SESSION_SCHEMA}


def write_platform_session(row: dict[str, Any]) -> dict[str, Any]:
    SINA.mkdir(parents=True, exist_ok=True)
    row = dict(row)
    row["schema"] = SESSION_SCHEMA
    row["updated_at"] = _now()
    SESSION_PATH.write_text(json.dumps(row, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return row


def list_user_workspaces() -> list[dict[str, str]]:
    out: list[dict[str, str]] = []
    if not WORKSPACES_ROOT.is_dir():
        return out
    for child in sorted(WORKSPACES_ROOT.iterdir()):
        if not child.is_dir():
            continue
        proj = child / ".sourcea" / "project.yaml"
        name = child.name
        if proj.is_file():
            try:
                import yaml  # type: ignore

                doc = yaml.safe_load(proj.read_text(encoding="utf-8")) or {}
                if isinstance(doc, dict) and doc.get("name"):
                    name = str(doc["name"])
            except Exception:
                pass
        out.append({"slug": child.name, "name": name, "path": str(child.resolve())})
    return out


def resolve_user_workspace(slug: str) -> dict[str, Any]:
    ws_slug = slugify(slug)
    root = (WORKSPACES_ROOT / ws_slug).resolve()
    if not root.is_dir():
        return {"ok": False, "error": "workspace_not_found", "slug": ws_slug}
    session = read_platform_session()
    if session.get("workspace_slug") != ws_slug:
        write_platform_session({**session, "workspace_slug": ws_slug, "workspace_path": str(root)})
    return {"ok": True, "slug": ws_slug, "path": str(root)}


def provision_user_workspace(
    *,
    email: str = "",
    name: str = "",
    org: str = "",
    project_name: str = "",
    slug: str = "",
    profile: str = "startup",
) -> dict[str, Any]:
    project = (project_name or org or name or email.split("@")[0] or "My project").strip()
    ws_slug = slugify(slug or project)
    root = (WORKSPACES_ROOT / ws_slug).resolve()
    WORKSPACES_ROOT.mkdir(parents=True, exist_ok=True)
    root.mkdir(parents=True, exist_ok=True)

    import sys

    scripts = Path(__file__).resolve().parent
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from workspace_kernel_v2 import init_workspace, workspace_ready  # noqa: WPS433

    init_row = init_workspace(root, name=project[:80], profile=profile or "startup", overwrite=False)
    readme = root / "README.md"
    if not readme.is_file():
        readme.write_text(
            f"# {project}\n\nProvisioned by SourceA Platform · {ws_slug}\n\n"
            f"Open this folder in **Forge Terminal** to run, build, and ship with receipts.\n",
            encoding="utf-8",
        )
    ready = workspace_ready(root)
    session = write_platform_session(
        {
            "email": email.strip(),
            "name": name.strip(),
            "org": org.strip(),
            "project_name": project,
            "workspace_slug": ws_slug,
            "workspace_path": str(root),
            "profile": profile or "startup",
            "signed_in_at": read_platform_session().get("signed_in_at") or _now(),
            "provisioned_at": _now(),
        }
    )
    return {
        "ok": True,
        "slug": ws_slug,
        "path": str(root),
        "project_name": project,
        "workspace_ready": ready.get("ok"),
        "init": init_row,
        "session": session,
        "forge_terminal_url": f"http://127.0.0.1:13029/terminal/?workspace={ws_slug}",
    }
