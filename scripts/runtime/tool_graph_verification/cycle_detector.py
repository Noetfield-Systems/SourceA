"""Detect cycles in tool execution graph."""
from __future__ import annotations


def detect_cycles(*, nodes: list[str], edges: list[dict]) -> dict:
    adj: dict[str, list[str]] = {n: [] for n in nodes}
    for edge in edges:
        src, dst = edge.get("from"), edge.get("to")
        if src in adj and dst in adj:
            adj[src].append(dst)

    visited: set[str] = set()
    stack: set[str] = set()
    cycle_nodes: list[str] = []

    def dfs(node: str) -> bool:
        visited.add(node)
        stack.add(node)
        for nxt in adj.get(node, []):
            if nxt not in visited:
                if dfs(nxt):
                    return True
            elif nxt in stack:
                cycle_nodes.append(node)
                cycle_nodes.append(nxt)
                return True
        stack.remove(node)
        return False

    for node in nodes:
        if node not in visited:
            if dfs(node):
                break

    return {
        "cycle_detected": bool(cycle_nodes),
        "cycle_nodes": sorted(set(cycle_nodes)),
    }
