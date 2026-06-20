"""Hub API — GET /api/query-expansion-v1"""
from __future__ import annotations

from pre_llm.query_expansion.expansion_engine import run_query_expansion
from pre_llm.query_expansion.store import EXPANSION_SSOT_PATH, SCHEMA


def query_expansion_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    result = run_query_expansion(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
    )
    if not result.get("ok"):
        return result
    return {
        **result,
        "path": str(EXPANSION_SSOT_PATH),
        "schema": SCHEMA,
        "api": "/api/query-expansion-v1",
        "producer": "D7",
    }
