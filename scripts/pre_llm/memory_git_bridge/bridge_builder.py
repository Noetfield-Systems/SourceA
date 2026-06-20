"""Build D6 bridge index from read-only sources."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from pre_llm.memory_git_bridge.git_reader import (
    git_available,
    read_git_commits,
    read_git_diff_stat,
)
from pre_llm.memory_git_bridge.log_reader import (
    log_source_stats,
    read_artifact_log_slots,
    read_execution_memory_slots,
    read_gate_shadow_slots,
)
from pre_llm.memory_git_bridge.store import BRIDGE_SSOT_PATH, SCHEMA, load_canonical, write_canonical

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_MEMORY_BRIDGE_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def build_bridge_index(
    *,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    root = _repo_root(repo_root)
    tid = task_id or f"memory-bridge:{root.name}"

    if not force_refresh:
        cached = load_canonical()
        if cached and cached.get("repo_root") == str(root) and BRIDGE_SSOT_PATH.is_file():
            return {"ok": True, **cached, "cached": True}

    memory_slots = read_execution_memory_slots(limit=25)
    git_slots = read_git_commits(root, limit=12)
    diff_slots = read_git_diff_stat(root, commits_back=3) if git_slots else []
    gate_slots = read_gate_shadow_slots(limit=8)
    artifact_slots = read_artifact_log_slots(limit=6)

    slots = memory_slots + git_slots + diff_slots + gate_slots + artifact_slots
    stats = log_source_stats()

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": tid,
        "repo_root": str(root),
        "producer": "D6",
        "read_only": True,
        "memory_role": "retrieval substrate only — reads B-layer, never overrides truth",
        "slot_count": len(slots),
        "slots": slots,
        "bridge_ready": len(slots) >= 1,
        "git_available": git_available(root),
        "sources": {
            **stats,
            "git_commit_count": len(git_slots),
            "memory_slot_count": len(memory_slots),
            "gate_shadow_slot_count": len(gate_slots),
            "artifact_slot_count": len(artifact_slots),
        },
    }
    write_canonical(canonical=canonical, task_id=tid)
    return {"ok": True, **canonical, "cached": False}
