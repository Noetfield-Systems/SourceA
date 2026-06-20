"""Persist execution records — single writeback layer."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from execution_spine.executor import RawResult
from execution_spine.types import ExecutionRecord, TaskSpec

STATE_DIR = Path.home() / ".sina"
MEMORY_PATH = STATE_DIR / "execution_memory.jsonl"
ARTIFACT_DIR = STATE_DIR / "execution-artifacts"
SCHEMA_PATH = Path(__file__).resolve().parent / "schema.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _error_signature(stderr: str, exit_code: int) -> str:
    if exit_code == 0:
        return ""
    line = (stderr or "").strip().splitlines()
    if line:
        return line[-1][:240]
    return f"exit_{exit_code}"


def write_record(task: TaskSpec, raw: RawResult, *, queue_status: str) -> ExecutionRecord:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

    artifact = ARTIFACT_DIR / f"{task.task_id}.log"
    artifact.write_text(
        f"# command: {raw.input_command}\n# exit: {raw.exit_code}\n\n--- stdout ---\n{raw.stdout}\n\n--- stderr ---\n{raw.stderr}\n",
        encoding="utf-8",
    )

    success = raw.exit_code == 0
    record = ExecutionRecord(
        task_id=task.task_id,
        timestamp=_now(),
        status="success" if success else "failed",
        stdout=raw.stdout[-12000:] if len(raw.stdout) > 12000 else raw.stdout,
        stderr=raw.stderr[-8000:] if len(raw.stderr) > 8000 else raw.stderr,
        exit_code=raw.exit_code,
        execution_time_ms=raw.execution_time_ms,
        input_command=raw.input_command,
        artifact_path=str(artifact),
        error_signature=_error_signature(raw.stderr, raw.exit_code),
        action_id=task.action_id,
        producer=task.producer,
        plan_id=task.plan_id,
        queue_status=queue_status,
    )

    with MEMORY_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(record.to_dict(), ensure_ascii=False) + "\n")

    _mirror_runreceipt(record)
    if success:
        from execution_spine.progress_sync import apply_success_to_progress  # noqa: WPS433

        apply_success_to_progress(record)

    return record


def read_memory(*, task_id: str | None = None, limit: int = 50) -> list[dict]:
    if not MEMORY_PATH.is_file():
        return []
    rows: list[dict] = []
    for line in MEMORY_PATH.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if task_id and row.get("task_id") != task_id:
            continue
        rows.append(row)
    if task_id:
        return rows
    return rows[-limit:]


def memory_stats() -> dict:
    rows = read_memory(limit=10_000)
    ok = sum(1 for r in rows if r.get("status") == "success")
    fail = sum(1 for r in rows if r.get("status") == "failed")
    last = rows[-1] if rows else None
    return {
        "path": str(MEMORY_PATH),
        "total": len(rows),
        "success": ok,
        "failed": fail,
        "last_task_id": (last or {}).get("task_id"),
        "last_status": (last or {}).get("status"),
        "last_timestamp": (last or {}).get("timestamp"),
        "schema": str(SCHEMA_PATH),
    }


def _mirror_runreceipt(record: ExecutionRecord) -> None:
    """Align with P0 RunReceipt — append run.jsonl when plan is P0-RUNRECEIPT."""
    if record.plan_id != "P0-RUNRECEIPT":
        return
    mono_rr = Path.home() / "Desktop" / "SinaaiMonoRepo" / "SinaaiDataBase" / "runreceipt" / "run.jsonl"
    hq_rr = Path.home() / "Desktop" / "SinaaiDataBase" / "runreceipt" / "run.jsonl"
    line = {
        "round": 0,
        "ts": record.timestamp,
        "plan": record.plan_id,
        "outcome": "PASS" if record.status == "success" else "FAIL",
        "summary": f"spine {record.action_id} exit={record.exit_code}",
        "blockers": [],
        "task_id": record.task_id,
        "backend_verify": {"ok": record.status == "success", "detail": record.error_signature or "spine"},
        "ui_e2e": {"ok": True, "detail": "N/A — spine execution"},
        "near_misses": [],
    }
    payload = json.dumps(line, ensure_ascii=False) + "\n"
    for path in (mono_rr, hq_rr):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.open("a", encoding="utf-8").write(payload)
