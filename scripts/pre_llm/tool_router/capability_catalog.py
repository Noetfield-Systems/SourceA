"""Pre-LLM capability catalog — maps plan step kinds to tools."""
from __future__ import annotations

from typing import Any

# cost: 1=low read · 5=medium · 10=high execute
_CATALOG: dict[str, list[dict[str, Any]]] = {
    "intent": [
        {"capability_id": "read_intent", "tool_id": "api/intent-engine-v1", "permission": "read", "cost": 1},
        {"capability_id": "read_governance", "tool_id": "doc/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md", "permission": "read", "cost": 1},
    ],
    "diagnose": [
        {"capability_id": "graph_reasoning", "tool_id": "api/graph-reasoning-v1", "permission": "read", "cost": 2},
        {"capability_id": "read_memory", "tool_id": "api/memory-git-bridge-v1", "permission": "read", "cost": 2},
    ],
    "graph": [
        {"capability_id": "dependency_graph", "tool_id": "api/dependency-graph-v1", "permission": "read", "cost": 2},
        {"capability_id": "graph_reasoning", "tool_id": "api/graph-reasoning-v1", "permission": "read", "cost": 2},
    ],
    "retrieve": [
        {"capability_id": "vector_retrieval", "tool_id": "api/vector-retrieval-v1", "permission": "read", "cost": 2},
        {"capability_id": "query_expansion", "tool_id": "api/query-expansion-v1", "permission": "read", "cost": 2},
        {"capability_id": "context_ranking", "tool_id": "api/context-ranking-v1", "permission": "read", "cost": 2},
    ],
    "reason": [
        {"capability_id": "context_ranking", "tool_id": "api/context-ranking-v1", "permission": "read", "cost": 2},
    ],
    "plan": [
        {"capability_id": "planning_engine", "tool_id": "api/planning-engine-v1", "permission": "read", "cost": 2},
    ],
    "execute": [
        {"capability_id": "spine_queue", "tool_id": "spine/execution-queue", "permission": "execute", "cost": 8},
        {"capability_id": "hub_refresh", "tool_id": "hub/refresh", "permission": "write", "cost": 3},
        {"capability_id": "hub_build", "tool_id": "script/build-sina-command-panel.py", "permission": "write", "cost": 5},
    ],
    "validate": [
        {"capability_id": "run_validator", "tool_id": "script/validate-*.sh", "permission": "read", "cost": 3},
        {"capability_id": "packet_schema", "tool_id": "api/llm-context-packet-schema-v1", "permission": "read", "cost": 1},
    ],
    "governance": [
        {"capability_id": "alignment_audit", "tool_id": "script/find_critical_bugs.py", "permission": "read", "cost": 2},
    ],
    "observe": [
        {"capability_id": "code_intelligence", "tool_id": "api/code-intelligence-v1", "permission": "read", "cost": 1},
    ],
    "report": [
        {"capability_id": "hub_refresh", "tool_id": "hub/refresh", "permission": "write", "cost": 3},
    ],
    "fallback": [
        {"capability_id": "rerank_context", "tool_id": "api/context-ranking-v1", "permission": "read", "cost": 2},
        {"capability_id": "replan", "tool_id": "api/planning-engine-v1", "permission": "read", "cost": 3},
    ],
}


def capabilities_for_kind(kind: str) -> list[dict[str, Any]]:
    return list(_CATALOG.get(kind, _CATALOG.get("plan", [])))
