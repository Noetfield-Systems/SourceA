#!/usr/bin/env python3
"""Forge Civilization Loop v1 — continuous task processing for v4 foundation."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
TICK_RECEIPT = SINA / "forge-civilization-tick-latest-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def generate_tasks_from_backlog(*, workspace_path: str) -> list[dict[str, Any]]:
    """Collect tasks from L3 queue + civilization memory failures."""
    tasks: list[dict[str, Any]] = []
    try:
        from forge_l3_auto_runtime_v1 import list_pending  # noqa: WPS433

        for item in list_pending()[:3]:
            tasks.append({"goal": f"Repair Forge run {item.get('run_id')}", "source": "l3_queue", "run_id": item.get("run_id")})
    except Exception:
        pass
    try:
        from forge_civilization_memory_v1 import pending_failures  # noqa: WPS433

        tasks.extend(pending_failures()[:3])
    except Exception:
        pass
    if not tasks:
        tasks.append({"goal": "Verify forge terminal health", "source": "default", "workspace_path": workspace_path})
    return tasks[:5]


def civilization_tick(*, workspace_path: str, dry_run: bool = True) -> dict[str, Any]:
    """One civilization tick: backlog → agent select → swarm/cloud → memory update."""
    from forge_agent_registry_v1 import evolve_agents, load_registry  # noqa: WPS433
    from forge_civilization_memory_v1 import record_run  # noqa: WPS433
    from forge_swarm_blackboard_v1 import select_agent_for_task  # noqa: WPS433

    tasks = generate_tasks_from_backlog(workspace_path=workspace_path)
    registry = load_registry()
    processed: list[dict[str, Any]] = []

    for task in tasks:
        economy_task = {
            "id": task.get("run_id") or "tick-task",
            "goal": task.get("goal"),
            "cost_estimate": 1.0,
        }
        winner = select_agent_for_task(economy_task, registry)
        if dry_run:
            result = {
                "ok": True,
                "schema": "forge-agent-kernel-swarm-v3",
                "goal": task.get("goal"),
                "dry_run": True,
                "state": "DONE",
                "agent_winner": winner,
            }
        else:
            from forge_swarm_cloud_dispatch_v1 import dispatch_swarm_cloud  # noqa: WPS433

            result = dispatch_swarm_cloud(
                goal=str(task.get("goal") or ""),
                workspace_path=workspace_path,
                dry_run=False,
            )
            result["agent_winner"] = winner

        record_run(result)
        evolve_agents(success=bool(result.get("ok")))
        processed.append({"task": task, "result_ok": result.get("ok"), "winner": winner})

    out = {
        "ok": True,
        "schema": "forge-civilization-tick-v1",
        "dry_run": dry_run,
        "processed": len(processed),
        "tasks": processed,
        "at": _now(),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    TICK_RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    try:
        from forge_world_state_v1 import world_tick  # noqa: WPS433

        world_tick(dry_run=dry_run)
    except Exception:
        pass
    return out
