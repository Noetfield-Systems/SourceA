"""SSOT store + read-only intelligence inputs for tool graph."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
GRAPH_SSOT_PATH = STATE_DIR / "tool_graph_v1.json"
GRAPH_STATE_PATH = STATE_DIR / "tool-graph-v1-state.json"

INPUT_PATHS = {
    "memory": STATE_DIR / "execution_memory.jsonl",
    "planner": STATE_DIR / "planner_context_v1.json",
    "context": STATE_DIR / "context_intelligence_v1.json",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _mtime(path: Path) -> float:
    return path.stat().st_mtime if path.is_file() else 0.0


def _line_count(path: Path) -> int:
    if not path.is_file():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())


def input_fingerprint(*, registry_count: int) -> dict:
    return {
        "memory_mtime": _mtime(INPUT_PATHS["memory"]),
        "memory_lines": _line_count(INPUT_PATHS["memory"]),
        "planner_mtime": _mtime(INPUT_PATHS["planner"]),
        "context_mtime": _mtime(INPUT_PATHS["context"]),
        "registry_count": registry_count,
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


def load_planner_context() -> dict:
    return load_json(INPUT_PATHS["planner"])


def load_context_intelligence() -> dict:
    return load_json(INPUT_PATHS["context"])


def load_snapshot() -> dict:
    return load_json(GRAPH_SSOT_PATH)


def write_snapshot(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_SSOT_PATH.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")


def should_skip(*, fingerprint: dict, force: bool = False) -> bool:
    if force or not GRAPH_SSOT_PATH.is_file():
        return False
    prev = load_json(GRAPH_STATE_PATH)
    return prev.get("fingerprint") == fingerprint


def mark_built(store: dict, fingerprint: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    GRAPH_STATE_PATH.write_text(
        json.dumps({"updated_at": store.get("generated_at"), "fingerprint": fingerprint}, indent=2) + "\n",
        encoding="utf-8",
    )
