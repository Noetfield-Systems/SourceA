"""Build semantic plan graph from D4 decomposition + D9 evidence."""
from __future__ import annotations

from typing import Any

_KIND_PRODUCER: dict[str, str] = {
    "intent": "D4",
    "diagnose": "D8",
    "graph": "D3",
    "retrieve": "D5",
    "reason": "D9",
    "plan": "D10",
    "execute": "spine",
    "validate": "validators",
    "governance": "governance",
    "observe": "D1",
    "report": "D10",
}


def _evidence_for_kind(kind: str, ranked: list[dict], limit: int = 3) -> list[str]:
    kind_map = {
        "graph": ("reasoning_path", "symbol"),
        "retrieve": ("retrieval_chunk",),
        "diagnose": ("reasoning_path", "memory_slot"),
        "validate": ("retrieval_chunk", "memory_slot"),
        "execute": ("retrieval_chunk", "symbol"),
        "intent": ("symbol", "retrieval_chunk"),
    }
    allowed = kind_map.get(kind, ("retrieval_chunk", "symbol", "memory_slot", "reasoning_path"))
    refs: list[str] = []
    for r in ranked:
        if r.get("kind") in allowed:
            eid = r.get("evidence_id")
            if eid and eid not in refs:
                refs.append(eid)
        if len(refs) >= limit:
            break
    if not refs:
        for r in ranked[:limit]:
            eid = r.get("evidence_id")
            if eid:
                refs.append(eid)
    return refs


def build_plan_graph(
    *,
    goal_class: str,
    decomposition_tree: list[dict[str, Any]],
    ranked_evidence: list[dict[str, Any]],
    text: str,
) -> dict[str, Any]:
    nodes: list[dict[str, Any]] = []
    edges: list[dict[str, Any]] = []

    for step in decomposition_tree:
        sid = step.get("id") or f"step-{step.get('order', len(nodes)+1)}"
        kind = step.get("kind") or "plan"
        node_id = f"plan-{sid}"
        nodes.append(
            {
                "id": node_id,
                "step_id": sid,
                "title": step.get("title") or sid,
                "kind": kind,
                "order": step.get("order", len(nodes) + 1),
                "status": "pending",
                "producer_hint": _KIND_PRODUCER.get(kind, "D10"),
                "evidence_refs": _evidence_for_kind(kind, ranked_evidence),
                "goal_class": goal_class,
            }
        )

    fallback_id = "plan-fallback-retry"
    nodes.append(
        {
            "id": fallback_id,
            "step_id": "fallback_retry",
            "title": "Fallback: gather more context and re-rank (D9)",
            "kind": "fallback",
            "order": len(nodes) + 1,
            "status": "pending",
            "producer_hint": "D9",
            "evidence_refs": [],
            "goal_class": goal_class,
        }
    )

    for i in range(len(nodes) - 2):
        edges.append(
            {
                "from": nodes[i]["id"],
                "to": nodes[i + 1]["id"],
                "kind": "sequential",
            }
        )

    validate_nodes = [n for n in nodes if n.get("kind") == "validate"]
    if validate_nodes:
        last_validate = validate_nodes[-1]["id"]
        edges.append(
            {
                "from": last_validate,
                "to": fallback_id,
                "kind": "fallback_on_fail",
            }
        )

    execute_nodes = [n for n in nodes if n.get("kind") == "execute"]
    if execute_nodes and validate_nodes:
        edges.append(
            {
                "from": execute_nodes[-1]["id"],
                "to": validate_nodes[0]["id"],
                "kind": "gates",
            }
        )

    return {
        "nodes": nodes,
        "edges": edges,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "goal_class": goal_class,
        "input_hint": (text or "")[:160],
        "authority": "D10 semantic SSOT — not C6 runtime sequence",
    }
