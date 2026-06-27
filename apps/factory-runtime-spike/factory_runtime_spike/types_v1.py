"""Shared types and fixtures for factory runtime spike v1."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


@dataclass
class JobInput:
    job_id: str
    factory_id: str
    prompt: str
    vertical: str
    audience: str
    proof_artifact: str
    tenant_id: str = "labs-sandbox"

    def to_dict(self) -> dict[str, Any]:
        return {
            "job_id": self.job_id,
            "factory_id": self.factory_id,
            "prompt": self.prompt,
            "vertical": self.vertical,
            "audience": self.audience,
            "proof_artifact": self.proof_artifact,
            "tenant_id": self.tenant_id,
        }


@dataclass
class JobState:
    job: JobInput
    offer_headline: str = ""
    offer_summary: str = ""
    gate_verdict: str = ""
    gate_reasons: list[str] = field(default_factory=list)
    nodes_executed: list[str] = field(default_factory=list)
    artifact_urls: list[str] = field(default_factory=list)

    def to_graph_state(self) -> dict[str, Any]:
        return {
            "job": self.job.to_dict(),
            "offer_headline": self.offer_headline,
            "offer_summary": self.offer_summary,
            "gate_verdict": self.gate_verdict,
            "gate_reasons": self.gate_reasons,
            "nodes_executed": self.nodes_executed,
            "artifact_urls": self.artifact_urls,
        }


PUREFLOW_FIXTURE = JobInput(
    job_id="factory-job-pureflow-spike-v1",
    factory_id="web-product-factory-v1",
    prompt=(
        "Residential pool and spa service in Metro Vancouver. "
        "Audience: homeowners. Differentiator: documented PureFlow Report after every visit. "
        "Deliver acquisition system with tiers, booking, and trust artifact."
    ),
    vertical="pool_spa_residential",
    audience="vancouver_homeowners",
    proof_artifact="PureFlow Report",
)

FORBIDDEN_PROMPT_MARKERS = ("RUN INBOX", "cloud_forge_run", "fbe_motor")


def new_job_id() -> str:
    return f"factory-job-{uuid4().hex[:12]}"


def build_receipt(
    state: JobState,
    *,
    status: str,
    execution_plane: str,
    duration_ms: int,
    policy_passed: bool,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = {
        "schema": "fbe-execution-receipt-v1",
        "spike": "factory-runtime-spike-v1",
        "at": utc_now(),
        "job_id": state.job.job_id,
        "factory_id": state.job.factory_id,
        "status": status,
        "nodes_executed": state.nodes_executed,
        "duration_ms": duration_ms,
        "artifact_urls": state.artifact_urls,
        "policy_passed": policy_passed,
        "gate_verdict": state.gate_verdict,
        "gate_reasons": state.gate_reasons,
        "execution_plane": execution_plane,
        "tier_achieved": "spike-v1",
        "kernel_version": "factory-runtime-spike-v1",
        "kernel_hash": "spike-not-fbe",
        "offer_headline": state.offer_headline,
        "proof_artifact": state.job.proof_artifact,
    }
    if extra:
        row.update(extra)
    return row
