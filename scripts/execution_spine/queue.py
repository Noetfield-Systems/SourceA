"""SQLite job queue for execution spine."""
from __future__ import annotations

import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path

from execution_spine.types import TaskSpec, TaskStatus

STATE_DIR = Path.home() / ".sina"
DB_PATH = STATE_DIR / "execution-queue.db"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                task_id TEXT PRIMARY KEY,
                producer TEXT NOT NULL,
                action_id TEXT NOT NULL,
                kind TEXT NOT NULL,
                plan_id TEXT,
                payload_json TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                started_at TEXT,
                finished_at TEXT
            )
            """
        )
        conn.execute("CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks(status, created_at)")
        conn.commit()


def enqueue(
    *,
    producer: str,
    action_id: str,
    kind: str,
    payload: dict,
    plan_id: str = "",
    task_id: str | None = None,
) -> TaskSpec:
    init_db()
    tid = task_id or str(uuid.uuid4())
    created = _now()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO tasks (task_id, producer, action_id, kind, plan_id, payload_json, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (tid, producer, action_id, kind, plan_id, json.dumps(payload), TaskStatus.PENDING.value, created),
        )
        conn.commit()
    return TaskSpec(
        task_id=tid,
        producer=producer,
        action_id=action_id,
        kind=kind,
        payload=payload,
        plan_id=plan_id,
        status=TaskStatus.PENDING,
        created_at=created,
    )


def claim_next() -> TaskSpec | None:
    init_db()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT * FROM tasks
            WHERE status = ?
            ORDER BY created_at ASC
            LIMIT 1
            """,
            (TaskStatus.PENDING.value,),
        ).fetchone()
        if not row:
            return None
        started = _now()
        conn.execute(
            "UPDATE tasks SET status = ?, started_at = ? WHERE task_id = ? AND status = ?",
            (TaskStatus.RUNNING.value, started, row["task_id"], TaskStatus.PENDING.value),
        )
        if conn.total_changes != 1:
            conn.rollback()
            return None
        conn.commit()
    return _row_to_spec(row, status=TaskStatus.RUNNING, started_at=started)


def get_task(task_id: str) -> TaskSpec | None:
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,)).fetchone()
    if not row:
        return None
    return _row_to_spec(row, status=TaskStatus(row["status"]))


def set_status(task_id: str, status: TaskStatus) -> None:
    finished = _now() if status in (TaskStatus.DONE, TaskStatus.FAILED) else None
    with _connect() as conn:
        if finished:
            conn.execute(
                "UPDATE tasks SET status = ?, finished_at = ? WHERE task_id = ?",
                (status.value, finished, task_id),
            )
        else:
            conn.execute("UPDATE tasks SET status = ? WHERE task_id = ?", (status.value, task_id))
        conn.commit()


def list_tasks(*, status: str | None = None, limit: int = 50) -> list[TaskSpec]:
    init_db()
    with _connect() as conn:
        if status:
            rows = conn.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY created_at DESC LIMIT ?",
                (status, limit),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM tasks ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()
    return [_row_to_spec(r, status=TaskStatus(r["status"])) for r in rows]


def pending_count() -> int:
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT COUNT(*) AS n FROM tasks WHERE status = ?", (TaskStatus.PENDING.value,)).fetchone()
    return int(row["n"]) if row else 0


def _row_to_spec(row: sqlite3.Row, *, status: TaskStatus | None = None, started_at: str | None = None) -> TaskSpec:
    return TaskSpec(
        task_id=row["task_id"],
        producer=row["producer"],
        action_id=row["action_id"],
        kind=row["kind"],
        payload=json.loads(row["payload_json"]),
        plan_id=row["plan_id"] or "",
        status=status or TaskStatus(row["status"]),
        created_at=row["created_at"],
        started_at=started_at or row["started_at"] or "",
        finished_at=row["finished_at"] or "",
    )
