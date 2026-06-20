"""D10 orchestration — intent + ranking → semantic plan graph."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.intent_engine.decomposition import build_decomposition_tree
from pre_llm.intent_engine.intent_engine import analyze_intent
from pre_llm.intent_engine.store import load_canonical as load_d4
from pre_llm.context_ranking.ranking_engine import run_context_ranking
from pre_llm.context_ranking.store import load_canonical as load_d9
from pre_llm.planning_engine.graph_builder import build_plan_graph
from pre_llm.planning_engine.store import PLANNING_SSOT_PATH, SCHEMA, load_canonical, write_canonical

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_PLANNING_ENGINE_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def _resolve_intent(*, text: str, repo_root: str) -> dict[str, Any]:
    d4 = load_d4()
    if d4 and d4.get("input_text") == text.strip() and d4.get("packet_intent"):
        return {
            "goal_class": d4.get("goal_class") or d4["packet_intent"].get("goal_class"),
            "decomposition_tree": d4["packet_intent"].get("decomposition_tree") or [],
            "intent_ready": d4.get("intent_ready"),
        }
    live = analyze_intent(text=text, repo_root=repo_root)
    if not live.get("ok"):
        return {"goal_class": "other", "decomposition_tree": build_decomposition_tree(goal_class="other", text=text), "intent_ready": False}
    return {
        "goal_class": live.get("goal_class") or "other",
        "decomposition_tree": live.get("decomposition_tree") or [],
        "intent_ready": live.get("intent_ready"),
    }


def _packet_plan_from_canonical(canonical: dict[str, Any]) -> dict[str, Any]:
    graph = canonical.get("graph") or {}
    return {
        "graph": {
            "nodes": [
                {
                    "id": n.get("id"),
                    "title": n.get("title"),
                    "kind": n.get("kind"),
                    "order": n.get("order"),
                    "status": n.get("status"),
                    "evidence_refs": n.get("evidence_refs") or [],
                }
                for n in (graph.get("nodes") or [])
            ],
            "edges": [
                {
                    "from": e.get("from"),
                    "to": e.get("to"),
                    "kind": e.get("kind"),
                }
                for e in (graph.get("edges") or [])
            ],
        },
        "producer": "D10",
        "goal_class": canonical.get("goal_class"),
        "planning_authority": canonical.get("planning_authority"),
    }


def run_planning_engine(
    *,
    text: str,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    input_text = (text or "").strip()
    if not input_text:
        return {"ok": False, "error": "text required"}

    root = _repo_root(repo_root)
    tid = task_id or f"planning-engine:{root.name}"

    if not force_refresh:
        cached = load_canonical()
        if (
            cached
            and cached.get("input_text") == input_text
            and cached.get("repo_root") == str(root)
            and PLANNING_SSOT_PATH.is_file()
        ):
            return {
                "ok": True,
                **cached,
                "cached": True,
                "packet_plan": _packet_plan_from_canonical(cached),
            }

    intent = _resolve_intent(text=input_text, repo_root=str(root))
    goal_class = intent.get("goal_class") or "other"
    tree = intent.get("decomposition_tree") or build_decomposition_tree(goal_class=goal_class, text=input_text)

    d9 = load_d9()
    if not d9 or d9.get("input_text") != input_text or not d9.get("ranking_ready"):
        d9_live = run_context_ranking(text=input_text, repo_root=str(root), task_id=f"d10-{tid}", force_refresh=force_refresh)
        if not d9_live.get("ok"):
            return {"ok": False, "error": "D9 ranking required", "d9": d9_live}
        ranked = d9_live.get("ranked_evidence") or []
        d9_ref = d9_live.get("generated_at")
    else:
        ranked = d9.get("ranked_evidence") or []
        d9_ref = d9.get("generated_at")

    graph = build_plan_graph(
        goal_class=goal_class,
        decomposition_tree=tree,
        ranked_evidence=ranked,
        text=input_text,
    )

    plan_ready = len(graph.get("nodes") or []) >= 3 and len(graph.get("edges") or []) >= 2

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": tid,
        "repo_root": str(root),
        "input_text": input_text,
        "producer": "D10",
        "goal_class": goal_class,
        "planning_authority": "ONLY SSOT for LLM-bound pre-exec plan; B4=soft signal; C6=runtime only",
        "graph": graph,
        "plan_ready": plan_ready,
        "node_count": graph.get("node_count", 0),
        "edge_count": graph.get("edge_count", 0),
        "d4_ref": goal_class,
        "d9_ref": d9_ref,
        "fallback_node": "plan-fallback-retry",
    }
    write_canonical(canonical=canonical, task_id=tid)

    return {
        "ok": True,
        **canonical,
        "cached": False,
        "packet_plan": _packet_plan_from_canonical(canonical),
    }
