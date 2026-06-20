"""Hub API — GET /api/tool-router-v1"""
from __future__ import annotations

from pre_llm.tool_router.router_engine import run_tool_router
from pre_llm.tool_router.store import ROUTER_SSOT_PATH, SCHEMA


def tool_router_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    gate_mode: str = "shadow",
) -> dict:
    result = run_tool_router(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
        gate_mode=gate_mode,
    )
    if not result.get("ok"):
        return result
    return {
        **result,
        "path": str(ROUTER_SSOT_PATH),
        "schema": SCHEMA,
        "api": "/api/tool-router-v1",
        "producer": "D11",
    }
