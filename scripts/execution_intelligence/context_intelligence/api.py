"""Context Intelligence v1 — hub API + SSOT snapshot."""
from __future__ import annotations

from execution_intelligence.context_intelligence.context_builder import (
    build_task_context,
    build_unified_context,
)
from execution_intelligence.context_intelligence.context_store import (
    CONTEXT_SSOT_PATH,
    load_snapshot,
    mark_built,
    should_skip,
    write_snapshot,
)
from execution_intelligence.context_intelligence.retrieval_api import retrieve_context

CONTEXT_SCHEMA_VERSION = "context-intelligence-v1"
LEGACY_SCHEMA_VERSION = "execution-context-v1"


def run_context_intelligence(*, force: bool = False) -> dict:
    if should_skip(force=force):
        cached = load_snapshot()
        if cached:
            return {**cached, "ok": True, "skipped": True, "reason": "inputs unchanged"}

    context = build_unified_context()
    context["ok"] = True
    context["skipped"] = False
    context["path"] = str(CONTEXT_SSOT_PATH)
    write_snapshot(context)
    mark_built(context)
    return context


def context_intelligence_v1_payload() -> dict:
    result = run_context_intelligence()
    return {
        "ok": True,
        "schema": CONTEXT_SCHEMA_VERSION,
        "path": str(CONTEXT_SSOT_PATH),
        "skipped": result.get("skipped", False),
        "generated_at": result.get("generated_at"),
        "system_state": result.get("system_state") or {},
        "repo_state": result.get("repo_state") or {},
        "behavior_state": result.get("behavior_state") or {},
        "planner_state": result.get("planner_state") or {},
        "context_summary": result.get("context_summary") or "",
    }


def execution_context_payload(*, task_id: str = "", action_id: str | None = None) -> dict:
    """Legacy alias — task-scoped retrieval."""
    run_context_intelligence()
    data = retrieve_context(task_id=task_id, action_id=action_id)
    return {
        "ok": True,
        "schema": LEGACY_SCHEMA_VERSION,
        **data,
    }
