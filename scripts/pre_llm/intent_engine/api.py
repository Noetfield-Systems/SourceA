"""Hub API — GET /api/intent-engine-v1"""
from __future__ import annotations

from pre_llm.intent_engine.intent_engine import run_intent_engine
from pre_llm.intent_engine.query_engine import run_query
from pre_llm.intent_engine.store import INTENT_SSOT_PATH, SCHEMA


def intent_engine_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    query_type: str = "",
    query_arg: str = "",
) -> dict:
    result = run_intent_engine(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
    )
    if not result.get("ok"):
        return result

    payload = {
        "ok": True,
        "path": str(INTENT_SSOT_PATH),
        "schema": result.get("schema") or SCHEMA,
        "generated_at": result.get("generated_at"),
        "repo_root": result.get("repo_root"),
        "task_id": result.get("task_id"),
        "input_text": result.get("input_text"),
        "goal_class": result.get("goal_class"),
        "confidence": result.get("confidence"),
        "scores": result.get("scores"),
        "ambiguity_flags": result.get("ambiguity_flags"),
        "needs_clarification": result.get("needs_clarification"),
        "decomposition_tree": result.get("decomposition_tree"),
        "missing_context": result.get("missing_context"),
        "packet_intent": result.get("packet_intent"),
        "intent_ready": result.get("intent_ready"),
        "d3_ref": result.get("d3_ref"),
        "cached": result.get("cached", False),
    }

    if query_type:
        payload["query_result"] = run_query(
            query_type=query_type,
            arg=query_arg or text,
            canonical=result,
        )

    return payload
