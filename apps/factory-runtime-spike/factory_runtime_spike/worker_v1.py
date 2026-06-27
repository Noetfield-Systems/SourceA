#!/usr/bin/env python3
"""Temporal worker for factory runtime spike."""
from __future__ import annotations

import asyncio
import os
import sys
from pathlib import Path

SPIKE = Path(__file__).resolve().parents[1]
if str(SPIKE) not in sys.path:
    sys.path.insert(0, str(SPIKE))

from temporalio.client import Client  # noqa: E402
from temporalio.worker import Worker  # noqa: E402

from factory_runtime_spike.activities_v1 import emit_receipt_activity, intake_and_plan_activity  # noqa: E402
from factory_runtime_spike.workflow_v1 import FactoryJobWorkflowV1  # noqa: E402

TASK_QUEUE = os.environ.get("TEMPORAL_TASK_QUEUE", "sourcea-factory-spike-v1")
HOST = os.environ.get("TEMPORAL_HOST", "127.0.0.1:7233")


async def main() -> None:
    client = await Client.connect(HOST)
    worker = Worker(
        client,
        task_queue=TASK_QUEUE,
        workflows=[FactoryJobWorkflowV1],
        activities=[intake_and_plan_activity, emit_receipt_activity],
    )
    print(f"factory-runtime-spike worker · queue={TASK_QUEUE} · host={HOST}")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
