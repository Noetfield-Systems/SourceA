"""Hub API — GET /api/code-intelligence-v1"""
from __future__ import annotations

from pre_llm.code_intelligence.index_builder import run_full_index
from pre_llm.code_intelligence.query_engine import run_query
from pre_llm.code_intelligence.store import CODE_INTEL_SSOT_PATH

SCHEMA = "code-intelligence-v1"


def code_intelligence_v1_payload(
    *,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    query_type: str = "",
    query_arg: str = "",
) -> dict:
    result = run_full_index(repo_root=repo_root, task_id=task_id, force_refresh=force_refresh)
    if not result.get("ok"):
        return result

    payload = {
        "ok": True,
        "path": str(CODE_INTEL_SSOT_PATH),
        "dispatch_ready": False,
        "schema": result.get("schema"),
        "generated_at": result.get("generated_at"),
        "repo_root": result.get("repo_root"),
        "files": result.get("files"),
        "symbols": result.get("symbols"),
        "imports_graph": result.get("imports_graph"),
        "module_graph": result.get("module_graph"),
        "index_stats": result.get("index_stats"),
        "query_layer_ready": result.get("query_layer_ready"),
    }

    if query_type and query_arg:
        payload["query_result"] = run_query(query_type=query_type, arg=query_arg, canonical=result)

    return payload
