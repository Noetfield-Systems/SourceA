"""Read-only execution memory + trace logs for D6."""
from __future__ import annotations

import json
from pathlib import Path

from execution_intelligence.reader import MEMORY_PATH, memory_line_count, read_execution_memory

STATE_DIR = Path.home() / ".sina"
GATE_SHADOW_PATH = STATE_DIR / "gate_shadow_v1.jsonl"
ARTIFACTS_DIR = STATE_DIR / "execution-artifacts"


def _tail_jsonl(path: Path, limit: int) -> list[dict]:
    if not path.is_file():
        return []
    lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines() if ln.strip()]
    rows: list[dict] = []
    for line in lines[-limit:]:
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return rows


def read_execution_memory_slots(*, limit: int = 25) -> list[dict]:
    rows = read_execution_memory()
    if not rows:
        return []

    slots: list[dict] = []
    for rec in rows[-limit:]:
        task_id = rec.get("task_id") or ""
        action_id = rec.get("action_id") or rec.get("producer") or "execution"
        status = rec.get("status") or "unknown"
        stdout = (rec.get("stdout") or "").strip()
        excerpt = stdout[:400] if stdout else (rec.get("input_command") or "")[:200]
        slots.append(
            {
                "slot_id": f"mem-{task_id}" if task_id else f"mem-{len(slots)}",
                "kind": "execution_memory",
                "task_id": task_id,
                "action_id": action_id,
                "status": status,
                "timestamp": rec.get("timestamp"),
                "summary": f"{action_id}: {status}",
                "path": rec.get("artifact_path") or str(MEMORY_PATH),
                "excerpt": excerpt,
                "producer": "D6",
                "read_only": True,
            }
        )
    return slots


def read_gate_shadow_slots(*, limit: int = 10) -> list[dict]:
    rows = _tail_jsonl(GATE_SHADOW_PATH, limit)
    slots: list[dict] = []
    for i, rec in enumerate(rows):
        slots.append(
            {
                "slot_id": f"gate-{rec.get('task_id') or i}",
                "kind": "gate_shadow",
                "task_id": rec.get("task_id"),
                "timestamp": rec.get("at") or rec.get("timestamp"),
                "summary": (
                    f"gate_eligible={rec.get('gate_eligible')} "
                    f"readiness={rec.get('readiness_score')}"
                ),
                "path": str(GATE_SHADOW_PATH),
                "excerpt": json.dumps(
                    {
                        "missing_for_gate": rec.get("missing_for_gate"),
                        "producer_steps": rec.get("producer_steps"),
                    },
                    default=str,
                )[:500],
                "producer": "D6",
            }
        )
    return slots


def read_artifact_log_slots(*, limit: int = 8) -> list[dict]:
    if not ARTIFACTS_DIR.is_dir():
        return []

    logs = sorted(
        ARTIFACTS_DIR.glob("*.log"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )[:limit]

    slots: list[dict] = []
    for path in logs:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        slots.append(
            {
                "slot_id": f"artifact-{path.stem[:12]}",
                "kind": "execution_artifact_log",
                "task_id": path.stem,
                "summary": f"artifact log {path.name}",
                "path": str(path),
                "excerpt": text[:400],
                "producer": "D6",
            }
        )
    return slots


def log_source_stats() -> dict:
    return {
        "execution_memory_path": str(MEMORY_PATH),
        "execution_memory_lines": memory_line_count(),
        "gate_shadow_path": str(GATE_SHADOW_PATH),
        "gate_shadow_lines": len(_tail_jsonl(GATE_SHADOW_PATH, 10_000)),
        "artifact_log_count": len(list(ARTIFACTS_DIR.glob("*.log"))) if ARTIFACTS_DIR.is_dir() else 0,
    }
