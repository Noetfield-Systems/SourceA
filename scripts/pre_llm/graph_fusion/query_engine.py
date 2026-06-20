"""Lightweight queries on fused graph."""
from __future__ import annotations

from typing import Any


def neighbors(*, node_id: str, canonical: dict[str, Any], edge_type: str = "") -> dict[str, Any]:
    out_edges = [e for e in canonical.get("edges") or [] if e.get("from") == node_id]
    in_edges = [e for e in canonical.get("edges") or [] if e.get("to") == node_id]
    if edge_type:
        out_edges = [e for e in out_edges if e.get("type") == edge_type]
        in_edges = [e for e in in_edges if e.get("type") == edge_type]
    nodes = {n["id"]: n for n in canonical.get("nodes") or []}
    return {
        "query": "neighbors",
        "node_id": node_id,
        "outbound": out_edges[:80],
        "inbound": in_edges[:80],
        "outbound_targets": [nodes.get(e["to"], {"id": e["to"]}) for e in out_edges[:40]],
        "inbound_sources": [nodes.get(e["from"], {"id": e["from"]}) for e in in_edges[:40]],
    }


def find_node(*, kind: str, key: str, canonical: dict[str, Any]) -> dict[str, Any]:
    nid = f"{kind}:{key}"
    nodes = {n["id"]: n for n in canonical.get("nodes") or []}
    hit = nodes.get(nid)
    return {"query": "find_node", "node_id": nid, "hit": hit, "found": hit is not None}


def run_query(*, query_type: str, arg: str, canonical: dict[str, Any]) -> dict[str, Any]:
    q = (query_type or "").strip().lower()
    if q == "neighbors":
        return neighbors(node_id=arg, canonical=canonical)
    if q in ("find_symbol", "symbol"):
        return find_node(kind="symbol", key=arg, canonical=canonical)
    if q in ("find_file", "file"):
        return find_node(kind="file", key=arg, canonical=canonical)
    if q in ("find_module", "module"):
        return find_node(kind="module", key=arg, canonical=canonical)
    return {"query": q, "error": "unknown query_type", "arg": arg}
