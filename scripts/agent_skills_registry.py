#!/usr/bin/env python3
"""Agent skills registry — SSOT scan + hub payload."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
SKILLS_ROOT = SOURCE_A / "agent-skills"
REGISTRY_PATH = SKILLS_ROOT / "REGISTRY_LOCKED_v1.json"
LAW_DOC = "AGENT_SKILLS_AND_RESEARCH_PIPELINE_LOCKED_v1.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _parse_skill_meta(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    text = path.read_text(encoding="utf-8", errors="replace")
    if not text.startswith("---"):
        return {}
    end = text.find("---", 3)
    if end < 0:
        return {}
    block = text[3:end]
    out: dict[str, str] = {}
    for line in block.splitlines():
        if ":" in line:
            k, v = line.split(":", 1)
            out[k.strip()] = v.strip()
    return out


def _load_registry() -> dict:
    if not REGISTRY_PATH.is_file():
        return {"agents": [], "shared": []}
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


def _skill_row(*, agent_id: str | None, rel_path: str, cursor_name: str, role: str = "") -> dict[str, Any]:
    full = SKILLS_ROOT / rel_path
    meta = _parse_skill_meta(full)
    return {
        "agent_id": agent_id,
        "cursor_name": cursor_name,
        "path": rel_path,
        "role": role,
        "name": meta.get("name") or cursor_name,
        "description": meta.get("description") or "",
        "exists": full.is_file(),
        "source_a_path": str(full),
    }


def agent_skills_payload() -> dict[str, Any]:
    reg = _load_registry()
    shared = [
        _skill_row(
            agent_id=None,
            rel_path=s["path"],
            cursor_name=s["cursor_name"],
            role="shared",
        )
        for s in reg.get("shared") or []
    ]
    agents = []
    agent_rows = list(reg.get("agents") or [])
    agent_rows.sort(key=lambda a: (0 if a.get("agent_id") == "sourcea_worker" else 1, a.get("agent_id") or ""))
    for a in agent_rows:
        row = _skill_row(
            agent_id=a.get("agent_id"),
            rel_path=a.get("path"),
            cursor_name=a.get("cursor_name"),
            role=a.get("role") or "portfolio",
        )
        if a.get("description"):
            row["description"] = a["description"]
        if a.get("workspace"):
            row["workspace"] = a["workspace"]
        agents.append(row)
    law_path = SOURCE_A / LAW_DOC
    return {
        "ok": True,
        "schema": "agent_skills_v1",
        "built_at": _now(),
        "law_doc": LAW_DOC,
        "law_exists": law_path.is_file(),
        "registry_path": str(REGISTRY_PATH),
        "skills_root": str(SKILLS_ROOT),
        "sync_script": "scripts/sync-cursor-agent-skills.sh",
        "cursor_install_root": str(Path.home() / ".cursor" / "skills"),
        "shared_skills": shared,
        "agent_skills": agents,
        "skill_count": len(shared) + len(agents),
        "pipeline_tab": "agent-loop",
        "pipeline_api": "/api/agent-research",
    }
