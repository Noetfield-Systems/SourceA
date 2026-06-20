"""Hub API — GET /api/graph-reasoning-v1"""
from __future__ import annotations

from pre_llm.graph_reasoning.reasoning_engine import run_graph_reasoning
from pre_llm.graph_reasoning.store import REASONING_SSOT_PATH, SCHEMA


def graph_reasoning_v1_payload(
    *,
    text: str = "",
    target: str = "",
    target_type: str = "file",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    result = run_graph_reasoning(
        text=text,
        target=target,
        target_type=target_type,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
    )
    if not result.get("ok"):
        return result
    return {
        **result,
        "path": str(REASONING_SSOT_PATH),
        "schema": SCHEMA,
        "api": "/api/graph-reasoning-v1",
        "producer": "D8",
    }
