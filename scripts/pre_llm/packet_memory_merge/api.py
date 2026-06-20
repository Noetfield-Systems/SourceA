"""Hub API — GET /api/packet-memory-merge-v1"""
from __future__ import annotations

from pre_llm.packet_memory_merge.merge_engine import run_memory_merge_writeback
from pre_llm.packet_memory_merge.store import MERGE_SSOT_PATH, SCHEMA


def packet_memory_merge_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    result = run_memory_merge_writeback(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
    )
    if not result.get("ok"):
        return result
    return {
        **result,
        "api": "/api/packet-memory-merge-v1",
        "schema": SCHEMA,
        "path": str(MERGE_SSOT_PATH),
        "producer": "D16",
        "gate_eligible": (result.get("validation") or {}).get("gate_eligible"),
        "readiness_score": (result.get("validation") or {}).get("readiness_score"),
    }
