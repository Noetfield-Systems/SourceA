"""Planner SSOT — read-only upstream runtime artifacts."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
PLANNER_SSOT_PATH = STATE_DIR / "multi_step_planner_v1.json"

INPUT_PATHS = {
    "verified": STATE_DIR / "tool_graph_verified_v1.json",
    "graph": STATE_DIR / "tool_graph_v1.json",
    "router": STATE_DIR / "execution_router_v1.json",
    "repair": STATE_DIR / "repair_loop_v1.json",
    "fabric": STATE_DIR / "semantic_context_fabric_v1.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def load_planner_snapshot() -> dict:
    return load_json(PLANNER_SSOT_PATH)


def write_planner_snapshot(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PLANNER_SSOT_PATH.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")


def load_verified_entry(*, goal_tool_id: str, task_id: str) -> dict | None:
    store = load_json(INPUT_PATHS["verified"])
    key = f"{goal_tool_id}:{task_id}"
    entries = store.get("verifications") or {}
    if key in entries:
        return entries[key]
    latest = store.get("latest") or {}
    if latest.get("goal_tool_id") == goal_tool_id:
        return latest
    return None


def load_graph_entry(*, goal_tool_id: str, task_id: str) -> dict | None:
    store = load_json(INPUT_PATHS["graph"])
    key = f"{goal_tool_id}:{task_id}"
    graphs = store.get("graphs") or {}
    if key in graphs:
        return graphs[key]
    latest = store.get("latest") or {}
    if latest.get("goal_tool_id") == goal_tool_id:
        return latest
    return None
