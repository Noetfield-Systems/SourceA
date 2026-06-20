"""High-level spine API — enqueue, execute, respond."""
from __future__ import annotations

from pathlib import Path

from execution_spine.executor import run_task
from execution_spine.queue import enqueue, get_task, init_db, list_tasks, pending_count, set_status
from execution_spine.types import SPINE_EXECUTABLE_KINDS, ExecutionRecord, TaskStatus
from execution_spine.writer import memory_stats, read_memory, write_record

SOURCE_A = Path(__file__).resolve().parents[2]
PROMPTOS_ROOT = Path.home() / "Desktop" / "SinaPromptOS"

from execution_spine.progress_sync import plan_id_for_action


def action_to_payload(spec: dict) -> dict:
    kind = spec.get("kind")
    if kind == "one_click":
        return {"action": spec["action"], "promptos_root": str(PROMPTOS_ROOT), "timeout": 300}
    if kind == "shell":
        return {"argv": spec["argv"], "cwd": spec["cwd"], "timeout": spec.get("timeout", 120)}
    if kind == "brief":
        return {"lang": spec.get("lang", "en"), "timeout": 120}
    if kind == "ingest_clipboard":
        return {"repo": spec["repo"], "promptos_root": str(PROMPTOS_ROOT), "timeout": 120}
    raise ValueError(f"cannot build payload for kind={kind}")


def enqueue_branch_action(action_id: str, spec: dict) -> str:
    init_db()
    plan_id = plan_id_for_action(action_id, spec.get("plan_id", ""))
    task = enqueue(
        producer="run_branch_action",
        action_id=action_id,
        kind=spec["kind"],
        payload=action_to_payload(spec),
        plan_id=plan_id,
    )
    return task.task_id


def execute_task_sync(task_id: str) -> ExecutionRecord:
    task = get_task(task_id)
    if not task:
        raise ValueError(f"unknown task: {task_id}")
    set_status(task_id, TaskStatus.RUNNING)
    try:
        raw = run_task(task)
        q_status = TaskStatus.DONE.value if raw.exit_code == 0 else TaskStatus.FAILED.value
        record = write_record(task, raw, queue_status=q_status)
        set_status(task_id, TaskStatus.DONE if raw.exit_code == 0 else TaskStatus.FAILED)
        return record
    except Exception as exc:  # noqa: BLE001
        from execution_spine.executor import RawResult

        raw = RawResult(stdout="", stderr=str(exc), exit_code=1, execution_time_ms=0, input_command=task.kind)
        record = write_record(task, raw, queue_status=TaskStatus.FAILED.value)
        set_status(task_id, TaskStatus.FAILED)
        return record


def run_branch_via_spine(action_id: str, spec: dict) -> dict:
    task_id = enqueue_branch_action(action_id, spec)
    record = execute_task_sync(task_id)
    return record_to_branch_response(record)


def record_to_branch_response(record: ExecutionRecord) -> dict:
    out = (record.stdout or "") + (record.stderr or "")
    ok = record.status == "success"
    resp = {
        "ok": ok,
        "task_id": record.task_id,
        "stdout": record.stdout,
        "stderr": record.stderr,
        "output": out.strip(),
        "exit_code": record.exit_code,
        "execution_time_ms": record.execution_time_ms,
        "artifact_path": record.artifact_path,
        "message": "Done" if ok else "Engine failed",
        "spine": True,
    }
    if not ok and record.error_signature:
        resp["error"] = record.error_signature
    return resp


def spine_payload() -> dict:
    init_db()
    recent = read_memory(limit=20)
    return {
        "ok": True,
        "stats": memory_stats(),
        "queue_pending": pending_count(),
        "recent": list(reversed(recent[-20:])),
        "tasks": [
            {
                "task_id": t.task_id,
                "action_id": t.action_id,
                "kind": t.kind,
                "status": t.status.value,
                "plan_id": t.plan_id,
                "created_at": t.created_at,
            }
            for t in list_tasks(limit=30)
        ],
    }


def should_use_spine(spec: dict) -> bool:
    return spec.get("kind") in SPINE_EXECUTABLE_KINDS
