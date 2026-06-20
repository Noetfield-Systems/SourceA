"""Intent engine queries — reclassify, explain flags."""
from __future__ import annotations

from typing import Any

from pre_llm.intent_engine.intent_engine import analyze_intent


def run_query(*, query_type: str, arg: str, canonical: dict[str, Any]) -> dict[str, Any]:
    q = (query_type or "classify").strip().lower().replace("-", "_")
    if q in ("classify", "reclassify", "parse"):
        text = arg or canonical.get("input_text") or ""
        return analyze_intent(text=text, repo_root=canonical.get("repo_root"), task_id=canonical.get("task_id", ""))
    if q in ("flags", "ambiguity"):
        return {
            "query": q,
            "ambiguity_flags": canonical.get("ambiguity_flags") or [],
            "needs_clarification": canonical.get("needs_clarification"),
            "missing_context": canonical.get("missing_context") or [],
        }
    if q in ("tree", "decomposition"):
        return {
            "query": q,
            "goal_class": canonical.get("goal_class"),
            "decomposition_tree": canonical.get("decomposition_tree") or [],
        }
    return {"query": q, "error": "unknown query_type", "arg": arg}
