"""Repair loop SSOT — read-only upstream inputs."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
REPAIR_SSOT_PATH = STATE_DIR / "repair_loop_v1.json"

INPUT_PATHS = {
    "router": STATE_DIR / "execution_router_v1.json",
    "verified": STATE_DIR / "tool_graph_verified_v1.json",
    "graph": STATE_DIR / "tool_graph_v1.json",
    "memory": STATE_DIR / "execution_memory.jsonl",
    "decisions": STATE_DIR / "execution_decisions_v1.jsonl",
    "feedback": STATE_DIR / "execution_feedback_signals.jsonl",
    "planner": STATE_DIR / "planner_context_v1.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.is_file() else 0.0


def input_fingerprint(*, goal: str, task_id: str) -> dict:
    return {
        "router_mtime": _mtime(INPUT_PATHS["router"]),
        "verified_mtime": _mtime(INPUT_PATHS["verified"]),
        "graph_mtime": _mtime(INPUT_PATHS["graph"]),
        "memory_mtime": _mtime(INPUT_PATHS["memory"]),
        "decisions_mtime": _mtime(INPUT_PATHS["decisions"]),
        "feedback_mtime": _mtime(INPUT_PATHS["feedback"]),
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


def load_jsonl(path: Path, *, limit: int = 500) -> list[dict]:
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
    return rows[-limit:]


def load_router_route(*, task_id: str) -> dict:
    store = load_json(INPUT_PATHS["router"])
    routes = store.get("routes") or {}
    if task_id in routes:
        return routes[task_id]
    latest = store.get("latest") or {}
    if latest.get("task_id") == task_id:
        return latest
    return latest if latest else {}


def load_planner() -> dict:
    return load_json(INPUT_PATHS["planner"])


def load_repair_snapshot() -> dict:
    return load_json(REPAIR_SSOT_PATH)


def write_repair_snapshot(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    REPAIR_SSOT_PATH.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")
