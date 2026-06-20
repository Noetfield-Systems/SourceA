"""Build stateless context fabric — maps runtime ↔ pre-LLM handles (no inference)."""
from __future__ import annotations

from datetime import datetime, timezone

from runtime.context_fabric.fabric_store import (
    FABRIC_SSOT_PATH,
    PRE_LLM_ARTIFACTS,
    RUNTIME_ARTIFACTS,
    resolve_handle,
    load_fabric_snapshot,
    write_fabric_snapshot,
)

SCHEMA = "semantic-context-fabric-v1"
BRIDGE_LAW = "Stateless mapping only — D1 + D4–D14 pre-LLM handles; no AST, retrieval, ranking, or inference"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_context_fabric(*, task_id: str = "") -> dict:
    """Recompute handle map every call — stateless fabric (snapshot is observability only)."""
    pre_llm_handles = {
        "d1_code_intelligence": resolve_handle(
            key="d1_code_intelligence",
            path=PRE_LLM_ARTIFACTS["d1_code_intelligence"],
            owner_step="D1",
            api="/api/code-intelligence-v1",
        ),
        "d4_intent_engine": resolve_handle(
            key="d4_intent_engine",
            path=PRE_LLM_ARTIFACTS["d4_intent_engine"],
            owner_step="D4",
            api="/api/intent-engine-v1",
        ),
        "d5_vector_retrieval": resolve_handle(
            key="d5_vector_retrieval",
            path=PRE_LLM_ARTIFACTS["d5_vector_retrieval"],
            owner_step="D5",
            api="/api/vector-retrieval-v1",
        ),
        "d6_memory_git_bridge": resolve_handle(
            key="d6_memory_git_bridge",
            path=PRE_LLM_ARTIFACTS["d6_memory_git_bridge"],
            owner_step="D6",
            api="/api/memory-git-bridge-v1",
        ),
        "d7_query_expansion": resolve_handle(
            key="d7_query_expansion",
            path=PRE_LLM_ARTIFACTS["d7_query_expansion"],
            owner_step="D7",
            api="/api/query-expansion-v1",
        ),
        "d8_graph_reasoning": resolve_handle(
            key="d8_graph_reasoning",
            path=PRE_LLM_ARTIFACTS["d8_graph_reasoning"],
            owner_step="D8",
            api="/api/graph-reasoning-v1",
        ),
        "d9_context_ranking": resolve_handle(
            key="d9_context_ranking",
            path=PRE_LLM_ARTIFACTS["d9_context_ranking"],
            owner_step="D9",
            api="/api/context-ranking-v1",
        ),
        "d10_planning_engine": resolve_handle(
            key="d10_planning_engine",
            path=PRE_LLM_ARTIFACTS["d10_planning_engine"],
            owner_step="D10",
            api="/api/planning-engine-v1",
        ),
        "d11_tool_router": resolve_handle(
            key="d11_tool_router",
            path=PRE_LLM_ARTIFACTS["d11_tool_router"],
            owner_step="D11",
            api="/api/tool-router-v1",
        ),
        "d12_validation_layer": resolve_handle(
            key="d12_validation_layer",
            path=PRE_LLM_ARTIFACTS["d12_validation_layer"],
            owner_step="D12",
            api="/api/validation-layer-v1",
        ),
        "d13_diff_intelligence": resolve_handle(
            key="d13_diff_intelligence",
            path=PRE_LLM_ARTIFACTS["d13_diff_intelligence"],
            owner_step="D13",
            api="/api/diff-intelligence-v1",
        ),
        "d14_context_compression": resolve_handle(
            key="d14_context_compression",
            path=PRE_LLM_ARTIFACTS["d14_context_compression"],
            owner_step="D14",
            api="/api/context-compression-v1",
        ),
    }

    runtime_handles = {
        key: resolve_handle(
            key=key,
            path=path,
            owner_step={"c1_tool_graph": "C1", "c2_tool_graph_verified": "C2", "c3_execution_router": "C3", "c4_repair_loop": "C4"}[key],
            api={
                "c1_tool_graph": "/api/tool-graph-v1",
                "c2_tool_graph_verified": "/api/tool-graph-verify-v1",
                "c3_execution_router": "/api/execution-router-v1",
                "c4_repair_loop": "/api/repair-loop-v1",
            }.get(key, ""),
        )
        for key, path in RUNTIME_ARTIFACTS.items()
    }

    packet_hooks = {
        "llm_packet_fields": {
            "code_intelligence": {
                "source_step": "D1",
                "handle_key": "d1_code_intelligence",
                "populated": pre_llm_handles["d1_code_intelligence"]["ready"],
            },
            "intent": {
                "source_step": "D4",
                "handle_key": "d4_intent_engine",
                "populated": pre_llm_handles["d4_intent_engine"]["ready"],
            },
            "vector_retrieval": {
                "source_step": "D5",
                "handle_key": "d5_vector_retrieval",
                "populated": pre_llm_handles["d5_vector_retrieval"]["ready"],
            },
        },
        "note": "D15 assembly reads handles when D1/D5 artifacts exist — fabric does not merge content",
    }

    result = {
        "ok": True,
        "schema": SCHEMA,
        "stateless": True,
        "generated_at": _now(),
        "path": str(FABRIC_SSOT_PATH),
        "task_id": task_id or "fabric:default",
        "bridge_law": BRIDGE_LAW,
        "runtime_handles": runtime_handles,
        "pre_llm_handles": pre_llm_handles,
        "packet_hooks": packet_hooks,
        "readiness": {
            "runtime_stack_ready": all(h["exists"] for h in runtime_handles.values()),
            "pre_llm_d1_ready": pre_llm_handles["d1_code_intelligence"]["ready"],
            "pre_llm_d4_ready": pre_llm_handles["d4_intent_engine"]["ready"],
            "pre_llm_d5_ready": pre_llm_handles["d5_vector_retrieval"]["ready"],
            "bridge_active": True,
        },
        "instruction": {
            "action": "read_handles_only",
            "note": "Fabric passes pointers — never builds AST, vectors, or rankings",
        },
    }

    _persist_fabric(result)
    return result


def _persist_fabric(result: dict) -> None:
    snap = load_fabric_snapshot() if FABRIC_SSOT_PATH.is_file() else {"fabrics": {}}
    snap["schema"] = SCHEMA
    snap["stateless"] = True
    snap["generated_at"] = result.get("generated_at")
    snap["path"] = str(FABRIC_SSOT_PATH)
    snap["latest"] = result
    tid = result.get("task_id") or "default"
    snap.setdefault("fabrics", {})[tid] = result
    write_fabric_snapshot(snap)
