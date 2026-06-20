"""Dependency graph queries — impact, dependents, call fan-in."""
from __future__ import annotations

from typing import Any

from pre_llm.dependency_graph.graph_engine import simulate_impact


def run_query(*, query_type: str, arg: str, target_type: str, canonical: dict[str, Any]) -> dict[str, Any]:
    q = (query_type or "impact").strip().lower().replace("-", "_")
    if q in ("impact", "what_breaks", "simulate"):
        tt = target_type or ("module" if "." in arg and "/" not in arg else "file")
        return simulate_impact(target_type=tt, target=arg, canonical=canonical)
    if q in ("callers", "who_calls"):
        idx = canonical.get("impact_index") or {}
        callers = sorted(set((idx.get("symbol_callers") or {}).get(arg, [])))
        return {
            "query": "callers",
            "symbol": arg,
            "caller_count": len(callers),
            "callers": callers[:80],
        }
    return {"query": q, "error": "unknown query_type", "arg": arg}
