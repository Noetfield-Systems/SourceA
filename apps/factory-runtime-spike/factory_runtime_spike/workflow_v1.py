"""Temporal workflow — FactoryJobWorkflow v1 spike."""
from __future__ import annotations

import time
from datetime import timedelta
from typing import Any

from temporalio import workflow

with workflow.unsafe.imports_passed_through():
    from factory_runtime_spike.activities_v1 import emit_receipt_activity, intake_and_plan_activity


@workflow.defn(name="FactoryJobWorkflowV1")
class FactoryJobWorkflowV1:
    @workflow.run
    async def run(self, job_dict: dict[str, Any]) -> dict[str, Any]:
        t0 = workflow.now()
        phase = await workflow.execute_activity(
            intake_and_plan_activity,
            job_dict,
            start_to_close_timeout=timedelta(minutes=5),
        )
        duration_ms = int((workflow.now() - t0).total_seconds() * 1000)
        receipt = await workflow.execute_activity(
            emit_receipt_activity,
            {
                "state": phase["state"],
                "execution_plane": "temporal",
                "duration_ms": duration_ms,
            },
            start_to_close_timeout=timedelta(minutes=2),
        )
        return receipt
