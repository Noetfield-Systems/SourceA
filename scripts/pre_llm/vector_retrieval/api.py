"""Hub API — GET /api/vector-retrieval-v1"""
from __future__ import annotations

from pre_llm.vector_retrieval.retrieval_engine import run_retrieval
from pre_llm.vector_retrieval.store import VECTOR_SSOT_PATH, SCHEMA


def vector_retrieval_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    top_k: int = 8,
) -> dict:
    if not (text or "").strip():
        return {"ok": False, "error": "text query required"}
    result = run_retrieval(
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
        "path": str(VECTOR_SSOT_PATH),
        "schema": SCHEMA,
        "api": "/api/vector-retrieval-v1",
        "producer": "D5+L8" if result.get("hybrid_retrieval") else "D5",
        "mode": "hybrid" if result.get("hybrid_retrieval") else "token",
    }
