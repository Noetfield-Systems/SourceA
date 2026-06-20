"""Graph executor v1 — planner → policy → spine handoff."""
from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from runtime.graph_executor.spine_bridge import build_spine_bridge

EXECUTOR_SSOT_PATH = Path.home() / ".sina" / "graph_executor_v1.json"
SCHEMA = "graph-executor-v1"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_graph_executor(*, goal_tool_id: str = "pos-run", task_id: str = "") -> dict:
    bridge = build_spine_bridge(goal_tool_id=goal_tool_id, task_id=task_id)
    result = {
        **bridge,
        "schema": SCHEMA,
        "generated_at": _now(),
        "path": str(EXECUTOR_SSOT_PATH),
        "producer": "graph_executor",
        "api": "/api/graph-executor-v1",
    }
    if bridge.get("ok"):
        EXECUTOR_SSOT_PATH.parent.mkdir(parents=True, exist_ok=True)
        EXECUTOR_SSOT_PATH.write_text(
            __import__("json").dumps(result, indent=2),
            encoding="utf-8",
        )
    return result
