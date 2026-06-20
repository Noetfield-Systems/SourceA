"""SSOT loaders + persistent optimization memory store."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
SSOT_PATH = STATE_DIR / "self_optimization_v1.json"
STATE_PATH = STATE_DIR / "self-optimization-v1-state.json"

INPUT_PATHS = {
    "memory": STATE_DIR / "execution_memory.jsonl",
    "patterns": STATE_DIR / "execution_patterns_v1.json",
    "decisions": STATE_DIR / "execution_decisions_v1.jsonl",
    "signals": STATE_DIR / "execution_feedback_signals.jsonl",
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


def input_fingerprint() -> dict:
    return {
        "memory_mtime": _mtime(INPUT_PATHS["memory"]),
        "memory_lines": _line_count(INPUT_PATHS["memory"]),
        "patterns_mtime": _mtime(INPUT_PATHS["patterns"]),
        "decisions_mtime": _mtime(INPUT_PATHS["decisions"]),
        "decisions_lines": _line_count(INPUT_PATHS["decisions"]),
        "signals_mtime": _mtime(INPUT_PATHS["signals"]),
        "signals_lines": _line_count(INPUT_PATHS["signals"]),
        "planner_mtime": _mtime(INPUT_PATHS["planner"]),
        "context_mtime": _mtime(INPUT_PATHS["context"]),
    }


def load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError:
        return {}


def load_jsonl(path: Path, *, limit: int = 1000) -> list[dict]:
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


def load_inputs() -> dict:
    patterns_store = load_json(INPUT_PATHS["patterns"])
    return {
        "memory": load_jsonl(INPUT_PATHS["memory"]),
        "patterns": patterns_store.get("patterns") or [],
        "decisions": load_jsonl(INPUT_PATHS["decisions"]),
        "signals": load_jsonl(INPUT_PATHS["signals"]),
        "planner": load_json(INPUT_PATHS["planner"]),
        "context": load_json(INPUT_PATHS["context"]),
    }


def load_snapshot() -> dict:
    return load_json(SSOT_PATH)


def write_snapshot(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    SSOT_PATH.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")


def should_skip(*, force: bool = False) -> bool:
    if force or not SSOT_PATH.is_file():
        return False
    prev = load_json(STATE_PATH)
    return prev.get("fingerprint") == input_fingerprint()


def mark_built(store: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    STATE_PATH.write_text(
        json.dumps({"updated_at": store.get("generated_at"), "fingerprint": input_fingerprint()}, indent=2) + "\n",
        encoding="utf-8",
    )
