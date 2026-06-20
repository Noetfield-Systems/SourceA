"""D7 orchestration — intent → multi-query → retrieval plan."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.code_intelligence.store import load_canonical as load_d1
from pre_llm.intent_engine.intent_engine import analyze_intent
from pre_llm.intent_engine.store import load_canonical as load_d4
from pre_llm.query_expansion.plan_builder import build_retrieval_plan
from pre_llm.query_expansion.query_templates import build_query_variants
from pre_llm.query_expansion.symbol_expander import expand_symbols
from pre_llm.query_expansion.store import EXPANSION_SSOT_PATH, SCHEMA, load_canonical, write_canonical

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_QUERY_EXPANSION_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def _resolve_intent(*, text: str, repo_root: str) -> dict[str, Any]:
    d4 = load_d4()
    if d4 and d4.get("input_text") == text.strip() and d4.get("packet_intent"):
        return {
            "goal_class": d4.get("goal_class") or d4["packet_intent"].get("goal_class"),
            "packet_intent": d4["packet_intent"],
            "decomposition_tree": d4["packet_intent"].get("decomposition_tree") or [],
            "intent_ready": d4.get("intent_ready"),
            "source": "d4_cache",
        }
    live = analyze_intent(text=text, repo_root=repo_root)
    if not live.get("ok"):
        return {"goal_class": "other", "packet_intent": {}, "decomposition_tree": [], "intent_ready": False, "source": "fallback"}
    return {
        "goal_class": live.get("goal_class") or "other",
        "packet_intent": live.get("packet_intent") or {},
        "decomposition_tree": live.get("decomposition_tree") or [],
        "intent_ready": live.get("intent_ready"),
        "source": "d4_analyze",
    }


def _packet_retrieval_from_canonical(canonical: dict[str, Any]) -> dict[str, Any]:
    queries = canonical.get("queries") or []
    return {
        "queries": [
            {
                "id": q.get("id"),
                "text": q.get("text"),
                "mode": q.get("mode"),
                "source": q.get("source"),
                "top_k": q.get("top_k"),
                "weight": q.get("weight"),
            }
            for q in queries
        ],
        "retrieval_plan": canonical.get("retrieval_plan"),
        "producer": "D7",
    }


def run_query_expansion(
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
    tid = task_id or f"query-expansion:{root.name}"

    if not force_refresh:
        cached = load_canonical()
        if (
            cached
            and cached.get("input_text") == input_text
            and cached.get("repo_root") == str(root)
            and EXPANSION_SSOT_PATH.is_file()
        ):
            return {
                "ok": True,
                **cached,
                "cached": True,
                "packet_retrieval": _packet_retrieval_from_canonical(cached),
            }

    d1 = load_d1()
    if not d1:
        return {"ok": False, "error": "D1 code_intelligence_v1.json required"}

    intent = _resolve_intent(text=input_text, repo_root=str(root))
    goal_class = intent.get("goal_class") or "other"
    symbols = expand_symbols(text=input_text, d1=d1)
    queries = build_query_variants(
        text=input_text,
        goal_class=goal_class,
        symbols=symbols,
        decomposition_tree=intent.get("decomposition_tree") or [],
    )
    plan = build_retrieval_plan(queries=queries, goal_class=goal_class, repo_root=str(root))

    expansion_ready = len(queries) >= 3 and bool(plan.get("stages"))

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": tid,
        "repo_root": str(root),
        "input_text": input_text,
        "producer": "D7",
        "goal_class": goal_class,
        "intent_source": intent.get("source"),
        "intent_ready": intent.get("intent_ready"),
        "symbol_count": len(symbols),
        "symbols": symbols,
        "query_count": len(queries),
        "queries": queries,
        "retrieval_plan": plan,
        "expansion_ready": expansion_ready,
        "d4_ref": intent.get("packet_intent", {}).get("goal_class"),
        "d1_ref": d1.get("generated_at"),
    }
    write_canonical(canonical=canonical, task_id=tid)

    return {
        "ok": True,
        **canonical,
        "cached": False,
        "packet_retrieval": _packet_retrieval_from_canonical(canonical),
    }
