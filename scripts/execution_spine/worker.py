#!/usr/bin/env python3
"""Continuous worker — polls queue and executes tasks."""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1]
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from execution_spine.executor import run_task  # noqa: E402
from execution_spine.queue import claim_next, init_db, pending_count, set_status  # noqa: E402
from execution_spine.types import TaskStatus  # noqa: E402
from execution_spine.writer import write_record  # noqa: E402


def process_one() -> dict | None:
    task = claim_next()
    if not task:
        return None
    try:
        raw = run_task(task)
        q_status = TaskStatus.DONE.value if raw.exit_code == 0 else TaskStatus.FAILED.value
        record = write_record(task, raw, queue_status=q_status)
        set_status(task.task_id, TaskStatus.DONE if raw.exit_code == 0 else TaskStatus.FAILED)
        return record.to_dict()
    except Exception as exc:  # noqa: BLE001
        from execution_spine.executor import RawResult

        raw = RawResult(
            stdout="",
            stderr=str(exc),
            exit_code=1,
            execution_time_ms=0,
            input_command=task.payload.get("input_command", task.kind),
        )
        record = write_record(task, raw, queue_status=TaskStatus.FAILED.value)
        set_status(task.task_id, TaskStatus.FAILED)
        return record.to_dict()


def run_forever(*, poll_seconds: float = 1.0, max_idle: int | None = None) -> int:
    init_db()
    idle = 0
    processed = 0
    while True:
        result = process_one()
        if result:
            processed += 1
            idle = 0
            print(f"OK task={result.get('task_id')} status={result.get('status')}", flush=True)
        else:
            idle += 1
            if max_idle is not None and idle >= max_idle:
                break
            time.sleep(poll_seconds)
    return processed


def main() -> None:
    parser = argparse.ArgumentParser(description="Sina execution spine worker")
    parser.add_argument("--once", action="store_true", help="Process one task and exit")
    parser.add_argument("--drain", action="store_true", help="Process all pending then exit")
    parser.add_argument("--poll", type=float, default=1.0, help="Poll interval seconds")
    args = parser.parse_args()

    init_db()
    if args.once:
        out = process_one()
        if not out:
            print("no pending tasks")
            sys.exit(0)
        print(json_dump(out))
        sys.exit(0 if out.get("status") == "success" else 1)

    if args.drain:
        n = 0
        while pending_count() > 0:
            if process_one():
                n += 1
            else:
                break
        print(f"drained {n} tasks")
        sys.exit(0)

    print(f"worker started pending={pending_count()}", flush=True)
    try:
        run_forever(poll_seconds=args.poll)
    except KeyboardInterrupt:
        print("worker stopped", flush=True)


def json_dump(obj: dict) -> str:
    import json

    return json.dumps(obj, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()
