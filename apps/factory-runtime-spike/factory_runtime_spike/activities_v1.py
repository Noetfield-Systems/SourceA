"""Temporal activities + shared runners for dry-run."""
from __future__ import annotations

import asyncio
import time
from typing import Any, Literal

from factory_runtime_spike.critic_boot_stub_v1 import run_critic_boot_stub
from factory_runtime_spike.langgraph_gate_v1 import (
    intake_node,
    run_langgraph_gate,
    run_validate_and_receipt_nodes,
)
from factory_runtime_spike.maf_workflow_v1 import maf_workflow_metadata, run_maf_workflow, run_maf_workflow_with_meta
from factory_runtime_spike.types_v1 import JobInput, JobState, build_receipt, utc_now

try:
    from temporalio import activity

    def activity_defn(fn):
        return activity.defn(fn)

except ImportError:  # pragma: no cover

    def activity_defn(fn):
        return fn


def _state_to_dict(state: JobState) -> dict[str, Any]:
    return {
        "job": state.job.to_dict(),
        "offer_headline": state.offer_headline,
        "offer_summary": state.offer_summary,
        "gate_verdict": state.gate_verdict,
        "gate_reasons": state.gate_reasons,
        "nodes_executed": state.nodes_executed,
        "artifact_urls": state.artifact_urls,
    }


def dict_to_state(data: dict[str, Any]) -> JobState:
    j = data["job"]
    return JobState(
        job=JobInput(**j),
        offer_headline=data.get("offer_headline", ""),
        offer_summary=data.get("offer_summary", ""),
        gate_verdict=data.get("gate_verdict", "BLOCK"),
        gate_reasons=list(data.get("gate_reasons") or []),
        nodes_executed=list(data.get("nodes_executed") or []),
        artifact_urls=list(data.get("artifact_urls") or []),
    )


def run_intake_phase(job_dict: dict[str, Any], *, embed: Literal["langgraph", "maf"] = "langgraph") -> dict[str, Any]:
    job = JobInput(**job_dict)
    boot = run_critic_boot_stub(job)
    maf_meta: dict[str, Any] | None = None
    if boot["verdict"] == "BLOCK":
        state = JobState(job=job, gate_verdict="BLOCK", gate_reasons=boot["reasons"], nodes_executed=["critic_boot"])
    elif embed == "maf":
        intake_gs = intake_node({"job": job.to_dict(), "nodes_executed": []})
        if intake_gs.get("gate_verdict") == "BLOCK":
            state = JobState(
                job=job,
                gate_verdict="BLOCK",
                gate_reasons=list(intake_gs.get("gate_reasons") or []),
                nodes_executed=["critic_boot", "intake"],
            )
        else:
            draft, maf_meta = run_maf_workflow_with_meta(job)
            state = run_validate_and_receipt_nodes(draft)
            state.nodes_executed = ["critic_boot", "intake"] + list(state.nodes_executed)
    else:
        state = run_langgraph_gate(job)
    return {
        "state": _state_to_dict(state),
        "phase": "langgraph_gate_complete" if embed == "langgraph" else "maf_hybrid_complete",
        "critic_boot": boot,
        "embed": embed,
        "maf_meta": maf_meta,
        "at": utc_now(),
    }


def run_emit_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    state = dict_to_state(payload["state"])
    policy_passed = state.gate_verdict == "PASS"
    status = "COMPLETED" if policy_passed else "BLOCKED"
    extra: dict[str, Any] = {}
    if payload.get("embed") == "maf":
        maf_meta = payload.get("maf_meta") or {}
        extra.update(maf_meta if isinstance(maf_meta, dict) else maf_workflow_metadata(state))
        extra["critic_boot"] = payload.get("critic_boot")
    return build_receipt(
        state,
        status=status,
        execution_plane=payload.get("execution_plane", "temporal"),
        duration_ms=int(payload.get("duration_ms", 0)),
        policy_passed=policy_passed,
        extra=extra or None,
    )


@activity_defn
async def intake_and_plan_activity(job_dict: dict[str, Any]) -> dict[str, Any]:
    return run_intake_phase(job_dict)


@activity_defn
async def emit_receipt_activity(payload: dict[str, Any]) -> dict[str, Any]:
    return run_emit_receipt(payload)


def run_dry_factory_job(job: JobInput, *, embed: Literal["langgraph", "maf"] = "langgraph") -> dict[str, Any]:
    t0 = time.perf_counter()
    phase = run_intake_phase(job.to_dict(), embed=embed)
    duration_ms = int((time.perf_counter() - t0) * 1000)
    return run_emit_receipt(
        {
            "state": phase["state"],
            "execution_plane": "dry-run-maf" if embed == "maf" else "dry-run",
            "duration_ms": duration_ms,
            "embed": embed,
            "critic_boot": phase.get("critic_boot"),
            "maf_meta": phase.get("maf_meta"),
        }
    )


async def run_temporal_factory_job(job: JobInput, workflow_runner) -> dict[str, Any]:
    """workflow_runner: async callable returning receipt dict."""
    return await workflow_runner(job.to_dict())
