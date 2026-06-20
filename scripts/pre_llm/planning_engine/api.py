"""Hub API — GET /api/planning-engine-v1"""
from __future__ import annotations

from pre_llm.planning_engine.planning_engine import run_planning_engine
from pre_llm.planning_engine.store import PLANNING_SSOT_PATH, SCHEMA


def planning_engine_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    result = run_planning_engine(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
    )
    if not result.get("ok"):
        return result
    return {
        **result,
        "path": str(PLANNING_SSOT_PATH),
        "schema": SCHEMA,
        "api": "/api/planning-engine-v1",
        "producer": "D10",
    }
