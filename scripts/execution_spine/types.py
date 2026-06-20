"""Execution spine — shared types."""
from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    DONE = "done"
    FAILED = "failed"


@dataclass
class TaskSpec:
    """Queued work unit."""

    task_id: str
    producer: str
    action_id: str
    kind: str
    payload: dict[str, Any]
    plan_id: str = ""
    status: TaskStatus = TaskStatus.PENDING
    created_at: str = ""
    started_at: str = ""
    finished_at: str = ""


@dataclass
class ExecutionRecord:
    task_id: str
    timestamp: str
    status: str
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    input_command: str
    artifact_path: str
    error_signature: str
    action_id: str = ""
    producer: str = ""
    plan_id: str = ""
    queue_status: str = ""

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


SPINE_EXECUTABLE_KINDS = frozenset({"one_click", "shell", "brief", "ingest_clipboard"})
