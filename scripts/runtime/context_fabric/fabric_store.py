"""Fabric SSOT — pointer index only (no semantic artifacts)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
FABRIC_SSOT_PATH = STATE_DIR / "semantic_context_fabric_v1.json"

# Pre-LLM handles C5 may expose (law: D1 + D5 only)
PRE_LLM_ARTIFACTS: dict[str, Path] = {
    "d1_code_intelligence": STATE_DIR / "code_intelligence_v1.json",
    "d4_intent_engine": STATE_DIR / "intent_engine_v1.json",
    "d5_vector_retrieval": STATE_DIR / "vector_index_v1.json",
    "d6_memory_git_bridge": STATE_DIR / "memory_git_bridge_v1.json",
    "d7_query_expansion": STATE_DIR / "query_expansion_v1.json",
    "d8_graph_reasoning": STATE_DIR / "graph_reasoning_v1.json",
    "d9_context_ranking": STATE_DIR / "context_ranking_v1.json",
    "d10_planning_engine": STATE_DIR / "planning_engine_v1.json",
    "d11_tool_router": STATE_DIR / "tool_router_v1.json",
    "d12_validation_layer": STATE_DIR / "validation_layer_v1.json",
    "d13_diff_intelligence": STATE_DIR / "diff_intelligence_v1.json",
    "d14_context_compression": STATE_DIR / "context_compression_v1.json",
}

# Runtime stack artifacts the fabric may index for bridge visibility
RUNTIME_ARTIFACTS: dict[str, Path] = {
    "c1_tool_graph": STATE_DIR / "tool_graph_v1.json",
    "c2_tool_graph_verified": STATE_DIR / "tool_graph_verified_v1.json",
    "c3_execution_router": STATE_DIR / "execution_router_v1.json",
    "c4_repair_loop": STATE_DIR / "repair_loop_v1.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_fabric_snapshot() -> dict:
    if not FABRIC_SSOT_PATH.is_file():
        return {}
    try:
        data = json.loads(FABRIC_SSOT_PATH.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def write_fabric_snapshot(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    FABRIC_SSOT_PATH.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")


def resolve_handle(*, key: str, path: Path, owner_step: str, api: str = "") -> dict:
    exists = path.is_file()
    mtime = path.stat().st_mtime if exists else 0.0
    version = ""
    schema = ""
    if exists:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                version = str(payload.get("generated_at") or payload.get("version") or "")
                schema = str(payload.get("schema") or "")
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "key": key,
        "owner_step": owner_step,
        "path": str(path),
        "api": api,
        "exists": exists,
        "ready": exists and bool(schema or mtime),
        "mtime": mtime,
        "schema": schema,
        "version_hint": version,
    }
