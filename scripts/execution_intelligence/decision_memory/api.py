"""Decision Memory v1 — store, pipeline, hub API."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from execution_intelligence.decision_memory.causality import build_cause_effect_mappings
from execution_intelligence.decision_memory.extractor import extract_decisions_v1
from execution_intelligence.decision_memory.fix_linker import link_fixes
from execution_intelligence.pattern_engine.api import load_patterns_v1
from execution_intelligence.reader import memory_line_count, read_execution_memory

STATE_DIR = Path.home() / ".sina"
DECISIONS_V1_PATH = STATE_DIR / "execution_decisions_v1.jsonl"
DECISION_STATE_PATH = STATE_DIR / "decision-memory-v1-state.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_state() -> dict:
    if not DECISION_STATE_PATH.is_file():
        return {}
    try:
        return json.loads(DECISION_STATE_PATH.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _save_state(state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    DECISION_STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")


def write_decisions_v1(decisions: list[dict], *, rewrite: bool = False) -> int:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    mode = "w" if rewrite else "a"
    existing_tasks: set[str] = set()
    if not rewrite and DECISIONS_V1_PATH.is_file():
        for line in DECISIONS_V1_PATH.read_text(encoding="utf-8").splitlines():
            if line.strip():
                try:
                    existing_tasks.add(json.loads(line).get("task_id", ""))
                except json.JSONDecodeError:
                    pass

    written = 0
    with DECISIONS_V1_PATH.open(mode, encoding="utf-8") as fh:
        if rewrite:
            for dec in decisions:
                row = {**dec, "stored_at": _now()}
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                written += 1
        else:
            for dec in decisions:
                tid = dec.get("task_id") or ""
                if tid and tid in existing_tasks:
                    continue
                row = {**dec, "stored_at": _now()}
                fh.write(json.dumps(row, ensure_ascii=False) + "\n")
                if tid:
                    existing_tasks.add(tid)
                written += 1
    return written


def read_decisions(*, limit: int = 200) -> list[dict]:
    if not DECISIONS_V1_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in DECISIONS_V1_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows[-limit:]


def run_decision_pipeline(*, force: bool = False) -> dict:
    line_count = memory_line_count()
    prev = _load_state()
    patterns_mtime = _patterns_mtime()

    if (
        not force
        and prev.get("memory_line_count") == line_count
        and prev.get("patterns_mtime") == patterns_mtime
        and DECISIONS_V1_PATH.is_file()
    ):
        return {
            "ok": True,
            "skipped": True,
            "reason": "inputs unchanged",
            "decisions_total": len(read_decisions(limit=10_000)),
        }

    records = read_execution_memory()
    patterns = load_patterns_v1()
    extracted = extract_decisions_v1(records, patterns)
    written = write_decisions_v1(extracted, rewrite=force)

    state = {
        "updated_at": _now(),
        "memory_line_count": line_count,
        "patterns_mtime": patterns_mtime,
        "extracted": len(extracted),
        "written": written,
        "decisions_total": len(read_decisions(limit=10_000)),
    }
    _save_state(state)
    return {"ok": True, "skipped": False, **state}


def _patterns_mtime() -> float:
    path = STATE_DIR / "execution_patterns_v1.json"
    return path.stat().st_mtime if path.is_file() else 0.0


def decisions_v1_payload() -> dict:
    run_decision_pipeline()
    records = read_execution_memory()
    patterns = load_patterns_v1()
    decisions = read_decisions(limit=100)
    fix_relationships = link_fixes(patterns, records)
    cause_effect = build_cause_effect_mappings(decisions)

    return {
        "ok": True,
        "schema": "execution-decisions-v1",
        "path": str(DECISIONS_V1_PATH),
        "decisions": decisions[-50:],
        "cause_effect_mappings": cause_effect[-30:],
        "fix_relationships": fix_relationships[:20],
        "confidence_summary": {
            "avg": round(sum(d.get("confidence", 0) for d in decisions) / max(len(decisions), 1), 3),
            "count": len(decisions),
        },
        "by_cause_type": _count_by_type(decisions, "cause_type"),
    }


def decisions_payload() -> dict:
    """Backward-compatible alias."""
    return decisions_v1_payload()


def _count_by_type(rows: list[dict], key: str) -> dict:
    counts: dict[str, int] = {}
    for row in rows:
        val = row.get(key) or "unknown"
        counts[val] = counts.get(val, 0) + 1
    return counts
