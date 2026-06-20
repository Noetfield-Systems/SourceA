"""Hub API — GET /api/memory-git-bridge-v1"""
from __future__ import annotations

from pre_llm.memory_git_bridge.bridge_engine import run_bridge
from pre_llm.memory_git_bridge.store import BRIDGE_SSOT_PATH, SCHEMA


def memory_git_bridge_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    top_k: int = 12,
) -> dict:
    result = run_bridge(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
        top_k=top_k,
    )
    if not result.get("ok"):
        return result
    return {
        **result,
        "path": str(BRIDGE_SSOT_PATH),
        "schema": SCHEMA,
        "api": "/api/memory-git-bridge-v1",
        "producer": "D6",
    }
