"""Read-only inputs + verified graph SSOT store."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
GRAPH_PATH = STATE_DIR / "tool_graph_v1.json"
VERIFIED_PATH = STATE_DIR / "tool_graph_verified_v1.json"
VERIFY_STATE_PATH = STATE_DIR / "tool-graph-verify-v1-state.json"

INPUT_PATHS = {
    "graph": GRAPH_PATH,
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


def load_planner() -> dict:
    return load_json(INPUT_PATHS["planner"])


def load_context() -> dict:
    return load_json(INPUT_PATHS["context"])


def load_graph_entry(*, goal_tool_id: str, task_id: str) -> dict | None:
    store = load_json(GRAPH_PATH)
    cache_key = f"{goal_tool_id}:{task_id}"
    graphs = store.get("graphs") or {}
    if cache_key in graphs:
        return graphs[cache_key]
    latest = store.get("latest") or {}
    if latest.get("goal_tool_id") == goal_tool_id:
        return latest
    return None


def load_verified_snapshot() -> dict:
    return load_json(VERIFIED_PATH)


def write_verified(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    VERIFIED_PATH.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")


def should_skip(*, fingerprint: dict, force: bool = False) -> bool:
    if force or not VERIFIED_PATH.is_file():
        return False
    prev = load_json(VERIFY_STATE_PATH)
    return prev.get("fingerprint") == fingerprint


def mark_built(store: dict, fingerprint: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    VERIFY_STATE_PATH.write_text(
        json.dumps({"updated_at": store.get("generated_at"), "fingerprint": fingerprint}, indent=2) + "\n",
        encoding="utf-8",
    )
