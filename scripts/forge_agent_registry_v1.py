#!/usr/bin/env python3
"""Forge Agent Registry v1 — persistent agent identity + reputation."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
REGISTRY_PATH = SINA / "forge-agent-registry-v1.json"

SEED_AGENTS: list[dict[str, Any]] = [
    {"id": "planner-001", "role": "planner", "skills": ["architecture", "decompose"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "planner-002", "role": "planner", "skills": ["risk", "scope"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "planner-003", "role": "planner", "skills": ["repo_scan"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "builder-001", "role": "builder", "skills": ["patch", "python"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "builder-002", "role": "builder", "skills": ["patch", "typescript"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "builder-003", "role": "builder", "skills": ["test", "verify"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "builder-004", "role": "builder", "skills": ["docs"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "builder-005", "role": "builder", "skills": ["refactor"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "critic-001", "role": "critic", "skills": ["review", "quality"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "critic-002", "role": "critic", "skills": ["security"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "critic-003", "role": "critic", "skills": ["tests"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "repair-001", "role": "repair", "skills": ["fix", "patch"], "reputation": 0.5, "cost_efficiency": 1.0, "runs": 0, "status": "active"},
    {"id": "optimizer-001", "role": "optimizer", "skills": ["roi", "cost"], "reputation": 0.5, "cost_efficiency": 1.2, "runs": 0, "status": "active"},
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load() -> dict[str, Any]:
    try:
        doc = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        if doc.get("agents"):
            return doc
    except (OSError, json.JSONDecodeError):
        pass
    return {"schema": "forge-agent-registry-v1", "agents": [dict(a) for a in SEED_AGENTS], "at": _now()}


def _save(doc: dict[str, Any]) -> None:
    doc["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_registry() -> dict[str, Any]:
    return _load()


def get_agents(*, role: str | None = None) -> list[dict[str, Any]]:
    agents = _load().get("agents") or []
    if role:
        return [a for a in agents if a.get("role") == role]
    return agents


def update_reputation(*, agent_ids: list[str], success: bool) -> dict[str, Any]:
    doc = _load()
    delta = 0.1 if success else -0.15
    updated: list[str] = []
    for agent in doc.get("agents") or []:
        if agent.get("id") in agent_ids:
            rep = float(agent.get("reputation") or 0.5) + delta
            agent["reputation"] = round(max(0.0, min(1.0, rep)), 3)
            agent["runs"] = int(agent.get("runs") or 0) + 1
            updated.append(agent["id"])
    _save(doc)
    return {"ok": True, "updated": updated, "success": success}


def assign_planner_ids(count: int = 3) -> list[str]:
    planners = get_agents(role="planner")
    planners.sort(key=lambda a: float(a.get("reputation") or 0), reverse=True)
    return [p["id"] for p in planners[:count]]


def evolve_agents(*, success: bool) -> dict[str, Any]:
    """Simple evolution: boost top performers on success."""
    doc = _load()
    for agent in doc.get("agents") or []:
        rep = float(agent.get("reputation") or 0.5)
        if success and rep > 0.8:
            agent["cost_efficiency"] = round(float(agent.get("cost_efficiency") or 1.0) * 1.05, 3)
        elif not success and rep < 0.3:
            agent["cost_efficiency"] = round(float(agent.get("cost_efficiency") or 1.0) * 0.95, 3)
    _save(doc)
    return {"ok": True, "evolved": True}
