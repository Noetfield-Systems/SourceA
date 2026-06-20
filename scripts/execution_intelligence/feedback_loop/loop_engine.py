"""Feedback loop v1 — patterns + decisions → influence signals (read-only upstream)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from execution_intelligence.decision_memory.api import read_decisions
from execution_intelligence.feedback_loop.influence_mapper import map_influence
from execution_intelligence.feedback_loop.priority_adjuster import actions_by_type, build_ranking
from execution_intelligence.feedback_loop.signal_generator import generate_signals
from execution_intelligence.pattern_engine.helpers import action_from_pattern

STATE_DIR = Path.home() / ".sina"
PATTERNS_V1_PATH = STATE_DIR / "execution_patterns_v1.json"
DECISIONS_V1_PATH = STATE_DIR / "execution_decisions_v1.jsonl"
SIGNALS_PATH = STATE_DIR / "execution_feedback_signals.jsonl"
LOOP_STATE_PATH = STATE_DIR / "feedback-loop-v1-state.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> dict:
    if not LOOP_STATE_PATH.is_file():
        return {}
    try:
        return json.loads(LOOP_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    LOOP_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def _input_fingerprint() -> dict:
    patterns_mtime = PATTERNS_V1_PATH.stat().st_mtime if PATTERNS_V1_PATH.is_file() else 0.0
    decisions_mtime = DECISIONS_V1_PATH.stat().st_mtime if DECISIONS_V1_PATH.is_file() else 0.0
    decisions_lines = 0
    if DECISIONS_V1_PATH.is_file():
        decisions_lines = sum(1 for line in DECISIONS_V1_PATH.read_text(encoding="utf-8").splitlines() if line.strip())
    patterns_count = 0
    if PATTERNS_V1_PATH.is_file():
        try:
            patterns_count = int(json.loads(PATTERNS_V1_PATH.read_text(encoding="utf-8")).get("pattern_count") or 0)
        except json.JSONDecodeError:
            patterns_count = 0
    return {
        "patterns_mtime": patterns_mtime,
        "decisions_mtime": decisions_mtime,
        "decisions_lines": decisions_lines,
        "patterns_count": patterns_count,
    }


def load_patterns_readonly() -> list[dict]:
    """Read patterns SSOT without triggering extraction."""
    if not PATTERNS_V1_PATH.is_file():
        return []
    try:
        data = json.loads(PATTERNS_V1_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    return data.get("patterns") or []


def read_signals(*, limit: int = 500) -> list[dict]:
    if not SIGNALS_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in SIGNALS_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def _write_signals(signals: list[dict]) -> int:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    with SIGNALS_PATH.open("w", encoding="utf-8") as fh:
        for row in signals:
            fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    return len(signals)


def _repeated_errors_from_patterns(patterns: list[dict]) -> list[dict]:
    out: list[dict] = []
    for pattern in patterns:
        if pattern.get("type") != "repetition":
            continue
        action = action_from_pattern(pattern)
        out.append(
            {
                "error_signature": pattern.get("signature") or "",
                "frequency": pattern.get("frequency") or 0,
                "action_id": action,
                "related_tasks": (pattern.get("related_task_ids") or [])[-15:],
            }
        )
    return sorted(out, key=lambda x: -int(x.get("frequency") or 0))


def run_feedback_loop(*, force: bool = False) -> dict:
    """
    Patterns + decisions → influence signals.
    Idempotent: skips when upstream SSOT files unchanged unless force=True.
    """
    fp = _input_fingerprint()
    prev = _load_state()
    unchanged = (
        prev.get("patterns_mtime") == fp["patterns_mtime"]
        and prev.get("decisions_mtime") == fp["decisions_mtime"]
        and prev.get("decisions_lines") == fp["decisions_lines"]
        and SIGNALS_PATH.is_file()
    )
    if not force and unchanged:
        patterns = load_patterns_readonly()
        decisions = read_decisions(limit=10_000)
        return {
            "ok": True,
            "skipped": True,
            "reason": "patterns and decisions unchanged",
            "signals_count": prev.get("signals_count", len(read_signals(limit=10_000))),
            "patterns_count": len(patterns),
            "decisions_total": len(decisions),
            "patterns": patterns,
            "repeated_errors": _repeated_errors_from_patterns(patterns),
            "updated_at": prev.get("updated_at"),
            "ranking": prev.get("ranking") or [],
        }

    patterns = load_patterns_readonly()
    decisions = read_decisions(limit=10_000)
    raw = generate_signals(patterns, decisions)
    mapped = map_influence(raw)
    ranking = build_ranking(mapped)
    written = _write_signals(mapped)

    state = {
        "updated_at": _now(),
        **fp,
        "raw_signals": len(raw),
        "signals_count": written,
        "decisions_total": len(decisions),
        "ranking": ranking[:20],
        "by_signal_type": actions_by_type(mapped),
    }
    _save_state(state)
    try:
        from runtime.event_bus.bus_v1 import publish  # noqa: WPS433

        publish(
            topic="feedback.loop",
            payload={"signals_count": written, "patterns_count": len(patterns)},
            source="feedback_loop",
        )
    except Exception:
        pass

    return {
        "ok": True,
        "skipped": False,
        "signals_count": written,
        "raw_signals": len(raw),
        "patterns_count": len(patterns),
        "decisions_total": len(decisions),
        "patterns": patterns,
        "repeated_errors": _repeated_errors_from_patterns(patterns),
        "mapped_signals": mapped,
        "ranking": ranking,
        **state,
    }
