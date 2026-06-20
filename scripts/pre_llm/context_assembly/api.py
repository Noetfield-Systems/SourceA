"""Hub API — GET /api/context-assembly-v1"""
from __future__ import annotations

from pre_llm.context_assembly.assembly_engine import run_context_assembly
from pre_llm.context_assembly.store import PACKET_SSOT_PATH, SCHEMA


def context_assembly_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    result = run_context_assembly(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
    )
    if not result.get("ok"):
        return result
    val = result.get("validation") or {}
    return {
        **result,
        "schema": SCHEMA,
        "api": "/api/context-assembly-v1",
        "producer": "D15",
        "path": str(PACKET_SSOT_PATH),
        "assembly_ready": (result.get("assembly") or {}).get("assembly_ready"),
        "gate_eligible": val.get("gate_eligible"),
        "readiness_score": val.get("readiness_score"),
        "missing_for_gate": val.get("missing_for_gate"),
    }
