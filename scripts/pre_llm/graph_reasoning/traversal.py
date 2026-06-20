"""Forward graph traversal on D3 file/module adjacency."""
from __future__ import annotations

from collections import deque
from typing import Any


def _file_adjacency(d3: dict[str, Any]) -> dict[str, list[str]]:
    adj: dict[str, list[str]] = {}
    for e in d3.get("file_graph") or []:
        src, tgt = e.get("from") or "", e.get("to") or ""
        if not src or not tgt:
            continue
        adj.setdefault(src, [])
        if tgt not in adj[src]:
            adj[src].append(tgt)
    return adj


def forward_traversal(
    *,
    start_file: str,
    d3: dict[str, Any],
    max_depth: int = 3,
    max_nodes: int = 24,
) -> dict[str, Any]:
    adj = _file_adjacency(d3)
    if start_file not in adj and not any(start_file == t for ts in adj.values() for t in ts):
        # allow seed even if only a sink
        pass

    visited: list[str] = []
    edges: list[dict[str, str]] = []
    q: deque[tuple[str, int]] = deque([(start_file, 0)])
    seen = {start_file}

    while q and len(visited) < max_nodes:
        node, depth = q.popleft()
        visited.append(node)
        if depth >= max_depth:
            continue
        for nxt in adj.get(node, []):
            edges.append({"from": node, "to": nxt, "kind": "file_import"})
            if nxt not in seen:
                seen.add(nxt)
                q.append((nxt, depth + 1))

    return {
        "path_id": f"traverse-{start_file.replace('/', '-')[:48]}",
        "kind": "traversal",
        "seed": start_file,
        "seed_type": "file",
        "nodes": visited,
        "edges": edges[:40],
        "depth": max_depth,
        "node_count": len(visited),
        "summary": f"Forward traversal from {start_file} — {len(visited)} nodes",
    }


def root_cause_trace(
    *,
    target: str,
    target_type: str,
    d3: dict[str, Any],
    max_depth: int = 4,
    max_nodes: int = 24,
) -> dict[str, Any]:
    idx = d3.get("impact_index") or {}
    if target_type == "symbol":
        rev = idx.get("call_dependents") or {}
        start = target
    elif target_type == "module":
        rev = idx.get("module_dependents") or {}
        start = target
    else:
        rev = idx.get("file_dependents") or {}
        start = target

    visited: list[str] = []
    edges: list[dict[str, str]] = []
    q: deque[tuple[str, int]] = deque([(start, 0)])
    seen = {start}

    while q and len(visited) < max_nodes:
        node, depth = q.popleft()
        visited.append(node)
        if depth >= max_depth:
            continue
        for parent in rev.get(node, []):
            edges.append({"from": parent, "to": node, "kind": "depends_on"})
            if parent not in seen:
                seen.add(parent)
                q.append((parent, depth + 1))

    return {
        "path_id": f"rootcause-{target_type}-{target.replace('/', '-')[:40]}",
        "kind": "root_cause",
        "seed": target,
        "seed_type": target_type,
        "nodes": visited,
        "edges": edges[:40],
        "depth": max_depth,
        "node_count": len(visited),
        "summary": f"Root-cause trace on {target_type}:{target} — {len(visited)} nodes",
    }
