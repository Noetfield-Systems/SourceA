"""Hub API — GET /api/context-ranking-v1"""
from __future__ import annotations

from pre_llm.context_ranking.ranking_engine import run_context_ranking
from pre_llm.context_ranking.store import RANKING_SSOT_PATH, SCHEMA


def context_ranking_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    top_k: int = 16,
) -> dict:
    result = run_context_ranking(
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
        "path": str(RANKING_SSOT_PATH),
        "schema": SCHEMA,
        "api": "/api/context-ranking-v1",
        "producer": "D9",
    }
