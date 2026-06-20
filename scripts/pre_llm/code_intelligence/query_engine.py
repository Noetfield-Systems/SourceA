"""Queryable semantic map — who_calls, what_breaks, find_symbol."""
from __future__ import annotations

from typing import Any


def _normalize(name: str) -> str:
    return name.strip().split(".")[-1]


def _imported_by(module_graph: list[dict]) -> dict[str, list[str]]:
    out: dict[str, list[str]] = {}
    for edge in module_graph:
        out.setdefault(edge["to"], []).append(edge["from"])
    return {k: sorted(set(v)) for k, v in out.items()}


def query_who_calls(*, symbol: str, canonical: dict[str, Any]) -> dict[str, Any]:
    needle = _normalize(symbol)
    sym = (canonical.get("symbols") or {}).get(needle) or {}
    refs = sym.get("references") or []
    return {
        "query": "who_calls",
        "symbol": symbol,
        "definition": sym,
        "caller_count": len(refs),
        "callers": refs[:50],
    }


def query_what_breaks(*, module: str, canonical: dict[str, Any]) -> dict[str, Any]:
    imported_by = _imported_by(canonical.get("module_graph") or [])
    direct = sorted(set(imported_by.get(module, [])))
    transitive: set[str] = set()
    frontier = list(direct)
    while frontier:
        cur = frontier.pop()
        if cur in transitive:
            continue
        transitive.add(cur)
        for parent in imported_by.get(cur, []):
            if parent not in transitive:
                frontier.append(parent)
    return {
        "query": "what_breaks",
        "module": module,
        "direct_dependents": direct,
        "transitive_dependent_count": len(transitive),
        "transitive_dependents": sorted(transitive)[:100],
    }


def query_find_symbol(*, name: str, canonical: dict[str, Any]) -> dict[str, Any]:
    symbols = canonical.get("symbols") or {}
    hits: list[dict] = []
    if name in symbols:
        hits = [{"name": name, **symbols[name]}]
    else:
        needle = _normalize(name)
        if needle in symbols:
            hits = [{"name": needle, **symbols[needle]}]
    return {"query": "find_symbol", "name": name, "hit_count": len(hits), "hits": hits}


def run_query(*, query_type: str, arg: str, canonical: dict[str, Any]) -> dict[str, Any]:
    q = (query_type or "find_symbol").strip().lower().replace("-", "_")
    if q in ("who_calls", "who_calls_what"):
        return query_who_calls(symbol=arg, canonical=canonical)
    if q in ("what_breaks", "impact"):
        return query_what_breaks(module=arg, canonical=canonical)
    return query_find_symbol(name=arg, canonical=canonical)
