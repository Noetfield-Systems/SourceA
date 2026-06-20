"""Hub API — GET /api/dependency-graph-v1"""
from __future__ import annotations

from pre_llm.dependency_graph.graph_engine import run_dependency_graph
from pre_llm.dependency_graph.query_engine import run_query
from pre_llm.dependency_graph.store import DEP_GRAPH_SSOT_PATH, SCHEMA


def dependency_graph_v1_payload(
    *,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    query_type: str = "",
    query_arg: str = "",
    target_type: str = "",
) -> dict:
    result = run_dependency_graph(repo_root=repo_root, task_id=task_id, force_refresh=force_refresh)
    if not result.get("ok"):
        return result

    payload = {
        "ok": True,
        "path": str(DEP_GRAPH_SSOT_PATH),
        "schema": result.get("schema") or SCHEMA,
        "generated_at": result.get("generated_at"),
        "repo_root": result.get("repo_root"),
        "d2_ref": result.get("d2_ref"),
        "graph_stats": result.get("graph_stats"),
        "dependency_ready": result.get("dependency_ready"),
        "module_edge_sample": (result.get("module_graph") or [])[:8],
        "file_edge_sample": (result.get("file_graph") or [])[:8],
        "call_edge_sample": (result.get("call_graph") or [])[:8],
    }

    if query_type and query_arg:
        payload["query_result"] = run_query(
            query_type=query_type,
            arg=query_arg,
            target_type=target_type,
            canonical=result,
        )

    return payload
