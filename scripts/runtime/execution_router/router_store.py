"""Read-only inputs + execution router SSOT."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
ROUTER_SSOT_PATH = STATE_DIR / "execution_router_v1.json"
ROUTER_STATE_PATH = STATE_DIR / "execution-router-v1-state.json"

INPUT_PATHS = {
    "verified": STATE_DIR / "tool_graph_verified_v1.json",
    "graph": STATE_DIR / "tool_graph_v1.json",
    "memory": STATE_DIR / "execution_memory.jsonl",
    "planner": STATE_DIR / "planner_context_v1.json",
    "context": STATE_DIR / "context_intelligence_v1.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.is_file() else 0.0


def input_fingerprint(*, goal: str, task_id: str) -> dict:
    return {
        "verified_mtime": _mtime(INPUT_PATHS["verified"]),
        "graph_mtime": _mtime(INPUT_PATHS["graph"]),
        "memory_mtime": _mtime(INPUT_PATHS["memory"]),
        "planner_mtime": _mtime(INPUT_PATHS["planner"]),
        "context_mtime": _mtime(INPUT_PATHS["context"]),
        "goal": goal,
        "task_id": task_id,
    }


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def load_memory() -> list[dict]:
    path = INPUT_PATHS["memory"]
    if not path.is_file():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


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


def load_planner() -> dict:
    return load_json(INPUT_PATHS["planner"])


def load_context() -> dict:
    return load_json(INPUT_PATHS["context"])


def load_router_snapshot() -> dict:
    return load_json(ROUTER_SSOT_PATH)


def write_router_snapshot(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ROUTER_SSOT_PATH.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")


def load_task_progress(task_id: str) -> dict:
    snap = load_router_snapshot()
    progress = snap.get("task_progress") or {}
    return progress.get(task_id) or {}


def save_task_progress(task_id: str, progress: dict) -> None:
    snap = load_router_snapshot() if ROUTER_SSOT_PATH.is_file() else {"task_progress": {}}
    progress = {**progress, "updated_at": _now()}
    snap.setdefault("task_progress", {})[task_id] = progress
    write_router_snapshot(snap)
