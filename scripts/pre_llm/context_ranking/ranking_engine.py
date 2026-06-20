"""D9 orchestration — collect → score → rank evidence."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.code_intelligence.store import load_canonical as load_d1
from pre_llm.context_ranking.evidence_collector import collect_evidence
from pre_llm.context_ranking.ranker import rank_evidence
from pre_llm.context_ranking.store import RANKING_SSOT_PATH, SCHEMA, load_canonical, write_canonical
from pre_llm.graph_reasoning.store import load_canonical as load_d8
from pre_llm.intent_engine.intent_engine import analyze_intent
from pre_llm.intent_engine.store import load_canonical as load_d4
from pre_llm.memory_git_bridge.bridge_engine import run_bridge
from pre_llm.query_expansion.symbol_expander import expand_symbols
from pre_llm.vector_retrieval.retrieval_engine import run_retrieval

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_CONTEXT_RANKING_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def _resolve_goal_class(text: str, repo_root: str) -> str:
    d4 = load_d4()
    if d4 and d4.get("input_text") == text.strip() and d4.get("goal_class"):
        return d4["goal_class"]
    live = analyze_intent(text=text, repo_root=repo_root)
    return live.get("goal_class") or "other"


def _graph_node_set(d8: dict[str, Any]) -> set[str]:
    nodes: set[str] = set()
    for p in d8.get("paths") or []:
        for n in p.get("nodes") or []:
            if n:
                nodes.add(n)
        seed = p.get("seed")
        if seed:
            nodes.add(seed)
    return nodes


def _packet_ranking_from_canonical(canonical: dict[str, Any]) -> dict[str, Any]:
    return {
        "ranked_evidence": [
            {
                "rank": r.get("rank"),
                "evidence_id": r.get("evidence_id"),
                "kind": r.get("kind"),
                "source_step": r.get("source_step"),
                "path": r.get("path"),
                "summary": (r.get("summary") or "")[:300],
                "score": r.get("score"),
                "signals": r.get("signals"),
            }
            for r in (canonical.get("ranked_evidence") or [])
        ],
        "producer": "D9",
        "goal_class": canonical.get("goal_class"),
    }


def run_context_ranking(
    *,
    text: str,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    top_k: int = 16,
) -> dict:
    input_text = (text or "").strip()
    if not input_text:
        return {"ok": False, "error": "text required"}

    root = _repo_root(repo_root)
    tid = task_id or f"context-ranking:{root.name}"

    if not force_refresh:
        cached = load_canonical()
        if (
            cached
            and cached.get("input_text") == input_text
            and cached.get("repo_root") == str(root)
            and RANKING_SSOT_PATH.is_file()
        ):
            return {
                "ok": True,
                **cached,
                "cached": True,
                "packet_ranking": _packet_ranking_from_canonical(cached),
            }

    goal_class = _resolve_goal_class(input_text, str(root))
    d1 = load_d1()

    d5 = run_retrieval(text=input_text, repo_root=str(root), task_id=f"d9-{tid}", top_k=top_k)
    if not d5.get("ok"):
        return {"ok": False, "error": "D5 retrieval required", "d5": d5}

    d6 = run_bridge(text=input_text, repo_root=str(root), task_id=f"d9-{tid}", top_k=12)
    d8 = load_d8()
    if not d8 or not d8.get("reasoning_ready"):
        from pre_llm.graph_reasoning.reasoning_engine import run_graph_reasoning  # noqa: WPS433

        d8_live = run_graph_reasoning(text=input_text, repo_root=str(root), task_id=f"d9-{tid}")
        d8 = d8_live if d8_live.get("ok") else {}

    symbols = expand_symbols(text=input_text, d1=d1)
    candidates = collect_evidence(
        d5_hits=d5.get("hits") or [],
        d6_slots=d6.get("hits") or [],
        d8_paths=d8.get("paths") or [],
        symbols=symbols,
        d1=d1,
    )

    ranked = rank_evidence(
        candidates=candidates,
        goal_class=goal_class,
        query_text=input_text,
        graph_nodes=_graph_node_set(d8),
        top_k=top_k,
    )

    ranking_ready = len(ranked) >= 3

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": tid,
        "repo_root": str(root),
        "input_text": input_text,
        "producer": "D9",
        "goal_class": goal_class,
        "candidate_count": len(candidates),
        "ranked_count": len(ranked),
        "ranked_evidence": ranked,
        "ranking_ready": ranking_ready,
        "noise_filtered": len(candidates) - len(ranked),
        "d5_ref": d5.get("generated_at"),
        "d6_ref": d6.get("generated_at"),
        "d8_ref": d8.get("generated_at"),
    }
    write_canonical(canonical=canonical, task_id=tid)

    return {
        "ok": True,
        **canonical,
        "cached": False,
        "hybrid_ranking": bool(d5.get("hybrid_retrieval")),
        "packet_ranking": _packet_ranking_from_canonical(canonical),
    }
