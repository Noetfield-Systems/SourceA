"""SSOT store for unified context intelligence snapshot."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

STATE_DIR = Path.home() / ".sina"
CONTEXT_SSOT_PATH = STATE_DIR / "context_intelligence_v1.json"
CONTEXT_STATE_PATH = STATE_DIR / "context-intelligence-v1-state.json"

INPUT_PATHS = {
    "memory": STATE_DIR / "execution_memory.jsonl",
    "patterns": STATE_DIR / "execution_patterns_v1.json",
    "decisions": STATE_DIR / "execution_decisions_v1.jsonl",
    "signals": STATE_DIR / "execution_feedback_signals.jsonl",
    "planner": STATE_DIR / "planner_context_v1.json",
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
    }


def load_planner_context_readonly() -> dict:
    path = INPUT_PATHS["planner"]
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def load_snapshot() -> dict:
    if not CONTEXT_SSOT_PATH.is_file():
        return {}
    try:
        return json.loads(CONTEXT_SSOT_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _load_state() -> dict:
    if not CONTEXT_STATE_PATH.is_file():
        return {}
    try:
        return json.loads(CONTEXT_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    CONTEXT_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def write_snapshot(context: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    CONTEXT_SSOT_PATH.write_text(json.dumps(context, indent=2) + "\n", encoding="utf-8")


def should_skip(*, force: bool = False) -> bool:
    if force or not CONTEXT_SSOT_PATH.is_file():
        return False
    fp = input_fingerprint()
    prev = _load_state()
    return prev.get("fingerprint") == fp


def mark_built(context: dict) -> None:
    _save_state({"updated_at": context.get("generated_at"), "fingerprint": input_fingerprint()})
