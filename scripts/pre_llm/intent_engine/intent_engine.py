"""Run intent classification pipeline — D4 orchestrator."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.intent_engine.ambiguity import detect_ambiguity
from pre_llm.intent_engine.classifier import classify_goal
from pre_llm.intent_engine.decomposition import build_decomposition_tree, missing_context_hints
from pre_llm.intent_engine.store import INTENT_SSOT_PATH, SCHEMA, load_canonical, write_canonical

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def analyze_intent(*, text: str, repo_root: str | None = None, task_id: str = "") -> dict[str, Any]:
    """Classify user text into packet.intent shape — deterministic, no LLM."""
    input_text = (text or "").strip()
    if not input_text:
        return {"ok": False, "error": "text required", "schema": SCHEMA}

    classification = classify_goal(input_text)
    ambiguity = detect_ambiguity(text=input_text, classification=classification)
    goal_class = classification["goal_class"]
    tree = build_decomposition_tree(goal_class=goal_class, text=input_text)
    missing = missing_context_hints(goal_class=goal_class, ambiguity=ambiguity, text=input_text)

    confidence = float(classification.get("confidence") or 0)
    intent_ready = bool(goal_class) and confidence >= 0.4 and not ambiguity.get("needs_clarification")

    packet_intent = {
        "goal_class": goal_class,
        "confidence": confidence,
        "ambiguity_flags": ambiguity.get("ambiguity_flags") or [],
        "decomposition_tree": tree,
        "missing_context": missing,
        "needs_clarification": ambiguity.get("needs_clarification", False),
        "producer": "D4",
    }

    return {
        "ok": True,
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": task_id or "intent:default",
        "repo_root": repo_root or str(SOURCE_A),
        "input_text": input_text,
        "input_hash": str(abs(hash(input_text))),
        "goal_class": goal_class,
        "confidence": confidence,
        "scores": classification.get("scores") or {},
        "runner_up": classification.get("runner_up"),
        "ambiguity_flags": ambiguity.get("ambiguity_flags") or [],
        "ambiguity_score": ambiguity.get("ambiguity_score"),
        "needs_clarification": ambiguity.get("needs_clarification", False),
        "decomposition_tree": tree,
        "missing_context": missing,
        "packet_intent": packet_intent,
        "intent_ready": intent_ready,
        "d3_ref": _d3_ref(),
    }


def _d3_ref() -> dict[str, str]:
    try:
        from pre_llm.dependency_graph.store import load_canonical as load_d3  # noqa: WPS433

        d3 = load_d3()
        if d3:
            return {"schema": d3.get("schema", ""), "generated_at": d3.get("generated_at", "")}
    except Exception:
        pass
    return {}


def run_intent_engine(
    *,
    text: str,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict[str, Any]:
    tid = task_id or "intent:default"
    if not force_refresh and not text:
        cached = load_canonical()
        if cached.get("intent_ready"):
            return {**cached, "ok": True, "cached": True}

    result = analyze_intent(text=text, repo_root=repo_root, task_id=tid)
    if not result.get("ok"):
        return result

    write_canonical(canonical=result, task_id=tid)
    result["path"] = str(INTENT_SSOT_PATH)
    result["cached"] = False
    return result
