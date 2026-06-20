"""Hub API — GET /api/context-compression-v1"""
from __future__ import annotations

from pre_llm.context_compression.compression_engine import run_context_compression
from pre_llm.context_compression.store import COMPRESSION_SSOT_PATH, SCHEMA


def context_compression_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    token_limit: int | None = None,
) -> dict:
    result = run_context_compression(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
        token_limit=token_limit,
    )
    if not result.get("ok"):
        return result
    return {
        **result,
        "path": str(COMPRESSION_SSOT_PATH),
        "schema": SCHEMA,
        "api": "/api/context-compression-v1",
        "producer": "D14",
    }
