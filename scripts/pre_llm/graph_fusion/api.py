"""Hub API — GET /api/graph-fusion-v1"""
from __future__ import annotations

from pre_llm.graph_fusion.fusion_builder import run_fusion
from pre_llm.graph_fusion.query_engine import run_query
from pre_llm.graph_fusion.store import FUSION_SSOT_PATH, SCHEMA


def graph_fusion_v1_payload(
    *,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    query_type: str = "",
    query_arg: str = "",
) -> dict:
    result = run_fusion(repo_root=repo_root, task_id=task_id, force_refresh=force_refresh)
    if not result.get("ok"):
        return result

    payload = {
        "ok": True,
        "path": str(FUSION_SSOT_PATH),
        "schema": result.get("schema") or SCHEMA,
        "generated_at": result.get("generated_at"),
        "repo_root": result.get("repo_root"),
        "d1_ref": result.get("d1_ref"),
        "fusion_stats": result.get("fusion_stats"),
        "fusion_ready": result.get("fusion_ready"),
        "node_sample": (result.get("nodes") or [])[:12],
        "edge_sample": (result.get("edges") or [])[:12],
    }

    if query_type and query_arg:
        payload["query_result"] = run_query(query_type=query_type, arg=query_arg, canonical=result)

    return payload
