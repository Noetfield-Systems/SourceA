"""Hub API — /api/semantic-context-fabric-v1"""
from __future__ import annotations

from runtime.context_fabric.fabric_engine import build_context_fabric
from runtime.context_fabric.fabric_store import FABRIC_SSOT_PATH

SCHEMA = "semantic-context-fabric-v1"


def semantic_context_fabric_v1_payload(*, task_id: str = "") -> dict:
    result = build_context_fabric(task_id=task_id)
    if not result.get("ok"):
        return result
    return {
        "ok": True,
        "schema": SCHEMA,
        "stateless": True,
        "path": str(FABRIC_SSOT_PATH),
        "task_id": result.get("task_id"),
        "bridge_law": result.get("bridge_law"),
        "runtime_handles": result.get("runtime_handles"),
        "pre_llm_handles": result.get("pre_llm_handles"),
        "packet_hooks": result.get("packet_hooks"),
        "readiness": result.get("readiness"),
        "instruction": result.get("instruction"),
    }
