#!/usr/bin/env python3
"""Start FactoryJobWorkflowV1 on Temporal (requires server)."""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
from pathlib import Path

SPIKE = Path(__file__).resolve().parents[1]
if str(SPIKE) not in sys.path:
    sys.path.insert(0, str(SPIKE))

from temporalio.client import Client  # noqa: E402

from factory_runtime_spike.types_v1 import PUREFLOW_FIXTURE  # noqa: E402
from factory_runtime_spike.workflow_v1 import FactoryJobWorkflowV1  # noqa: E402

TASK_QUEUE = os.environ.get("TEMPORAL_TASK_QUEUE", "sourcea-factory-spike-v1")
HOST = os.environ.get("TEMPORAL_HOST", "127.0.0.1:7233")


async def _run(fixture: str) -> dict:
    if fixture != "pureflow":
        raise SystemExit("only pureflow fixture wired for temporal start")
    client = await Client.connect(HOST)
    handle = await client.start_workflow(
        FactoryJobWorkflowV1.run,
        PUREFLOW_FIXTURE.to_dict(),
        id=PUREFLOW_FIXTURE.job_id,
        task_queue=TASK_QUEUE,
    )
    receipt = await handle.result()
    return {"ok": receipt.get("policy_passed"), "workflow_id": handle.id, "receipt": receipt}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", default="pureflow")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    row = asyncio.run(_run(args.fixture))
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
