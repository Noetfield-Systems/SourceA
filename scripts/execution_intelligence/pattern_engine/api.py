"""Pattern store + hub API (mining only — no prediction/planning)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from execution_intelligence.pattern_engine.extractor import extract_all_patterns
from execution_intelligence.reader import memory_line_count, read_execution_memory

STATE_DIR = Path.home() / ".sina"
PATTERNS_V1_PATH = STATE_DIR / "execution_patterns_v1.json"
PATTERNS_STATE_PATH = STATE_DIR / "pattern-engine-v1-state.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_extraction(*, force: bool = False) -> dict:
    records = read_execution_memory()
    line_count = memory_line_count()
    prev: dict = {}
    if PATTERNS_STATE_PATH.is_file():
        try:
            prev = json.loads(PATTERNS_STATE_PATH.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            prev = {}

    if not force and prev.get("memory_line_count") == line_count and PATTERNS_V1_PATH.is_file():
        return {"ok": True, "skipped": True, "reason": "memory unchanged", **load_store_meta()}

    patterns = extract_all_patterns(records)
    by_type: dict[str, list[dict]] = {}
    for p in patterns:
        by_type.setdefault(p["type"], []).append(p)

    store = {
        "schema": "execution-patterns-v1",
        "updated_at": _now(),
        "source": str(STATE_DIR / "execution_memory.jsonl"),
        "memory_line_count": line_count,
        "pattern_count": len(patterns),
        "patterns": patterns,
        "summary": {
            "success": len(by_type.get("success", [])),
            "failure": len(by_type.get("failure", [])),
            "repetition": len(by_type.get("repetition", [])),
            "fix": len(by_type.get("fix", [])),
        },
    }
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    PATTERNS_V1_PATH.write_text(json.dumps(store, indent=2) + "\n", encoding="utf-8")
    PATTERNS_STATE_PATH.write_text(
        json.dumps({"updated_at": _now(), "memory_line_count": line_count, "pattern_count": len(patterns)}, indent=2) + "\n",
        encoding="utf-8",
    )
    return {"ok": True, "skipped": False, **store}


def load_patterns_v1() -> list[dict]:
    run_extraction()
    if not PATTERNS_V1_PATH.is_file():
        return []
    data = json.loads(PATTERNS_V1_PATH.read_text(encoding="utf-8"))
    return data.get("patterns") or []


def load_store_meta() -> dict:
    if not PATTERNS_V1_PATH.is_file():
        return {"pattern_count": 0, "patterns": []}
    data = json.loads(PATTERNS_V1_PATH.read_text(encoding="utf-8"))
    return {
        "updated_at": data.get("updated_at"),
        "pattern_count": data.get("pattern_count", 0),
        "summary": data.get("summary", {}),
        "patterns": data.get("patterns") or [],
    }


def patterns_v1_payload() -> dict:
    result = run_extraction()
    patterns = result.get("patterns") or load_patterns_v1()
    by_type = {t: [p for p in patterns if p.get("type") == t] for t in ("success", "failure", "repetition", "fix")}

    sig_counts: dict[str, int] = {}
    for p in patterns:
        sig = p.get("signature") or ""
        sig_counts[sig] = sig_counts.get(sig, 0) + p.get("frequency", 1)
    top_sigs = sorted(sig_counts.items(), key=lambda x: -x[1])[:12]

    return {
        "ok": True,
        "schema": "execution-patterns-v1",
        "path": str(PATTERNS_V1_PATH),
        "updated_at": result.get("updated_at"),
        "skipped": result.get("skipped", False),
        "pattern_count": len(patterns),
        "summary": result.get("summary") or {},
        "top_success_patterns": sorted(by_type["success"], key=lambda p: -p.get("frequency", 0))[:10],
        "top_failure_clusters": sorted(by_type["failure"], key=lambda p: -p.get("frequency", 0))[:10],
        "fix_mappings": by_type["fix"][:15],
        "repetition_patterns": by_type["repetition"][:10],
        "most_frequent_signatures": [{"signature": s, "weight": w} for s, w in top_sigs],
    }
