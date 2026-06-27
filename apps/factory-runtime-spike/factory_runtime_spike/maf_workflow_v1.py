"""MAF factory job workflow sim — advisor pattern inside one Temporal activity.

Microsoft Agent Framework (GA 2026-04-03) mapping:
  offer_engineer → fan-out (asset_landing + asset_report) → fan-in → checkpoint → observability

SourceA PASS/BLOCK gate and receipt generation run OUTSIDE this module
(see activities_v1.py + langgraph_gate_v1.run_validate_and_receipt_nodes).

Deterministic · no cloud keys · no agent-framework pip required for Mac dry-run.
"""
from __future__ import annotations

from typing import Any, TypedDict
from uuid import uuid4

from langgraph.graph import END, StateGraph

from factory_runtime_spike.types_v1 import JobInput, JobState, utc_now

MAF_PATTERN_ID = "factory-job-fanout-gate-v1"


class MafState(TypedDict, total=False):
    job: dict[str, Any]
    offer_headline: str
    offer_summary: str
    pricing_tiers: str
    landing_outline: str
    report_template: str
    artifact_urls: list[str]
    maf_ckpt_ref: str
    maf_trace: list[str]
    nodes_executed: list[str]
    maf_internal_status: str


def _job(state: MafState) -> JobInput:
    j = state["job"]
    return JobInput(
        job_id=j["job_id"],
        factory_id=j["factory_id"],
        prompt=j["prompt"],
        vertical=j["vertical"],
        audience=j["audience"],
        proof_artifact=j["proof_artifact"],
        tenant_id=j.get("tenant_id", "labs-sandbox"),
    )


def _append_trace(state: MafState, node: str) -> tuple[list[str], list[str]]:
    nodes = list(state.get("nodes_executed") or [])
    trace = list(state.get("maf_trace") or [])
    nodes.append(node)
    trace.append(node)
    return nodes, trace


def offer_engineer_node(state: MafState) -> MafState:
    """MAF Executor: positioning, pricing, hero offer."""
    job = _job(state)
    nodes, trace = _append_trace(state, "offer_engineer")
    headline = f"Proof-backed {job.vertical.replace('_', ' ')} — {job.proof_artifact}"
    summary = (
        f"Offer for {job.audience}: documented service proof after every visit, "
        f"clear tiers, and mobile booking."
    )
    tiers = "Essential · Professional · Premium (monthly service plans)"
    return {
        **state,
        "nodes_executed": nodes,
        "maf_trace": trace,
        "offer_headline": headline,
        "offer_summary": summary,
        "pricing_tiers": tiers,
    }


def asset_landing_node(state: MafState) -> MafState:
    """MAF fan-out branch A: landing page structure + copy outline."""
    job = _job(state)
    nodes, trace = _append_trace(state, "asset_landing")
    outline = (
        f"Hero: {state.get('offer_headline', '')} · "
        f"Proof section: {job.proof_artifact} · CTA: Book service"
    )
    return {**state, "nodes_executed": nodes, "maf_trace": trace, "landing_outline": outline}


def asset_report_node(state: MafState) -> MafState:
    """MAF fan-out branch B: sample proof report template."""
    job = _job(state)
    nodes, trace = _append_trace(state, "asset_report")
    template = (
        f"{job.proof_artifact} template — visit date · checklist · photos · "
        f"chemical readings · next-service date"
    )
    return {**state, "nodes_executed": nodes, "maf_trace": trace, "report_template": template}


def assets_fan_in_node(state: MafState) -> MafState:
    """MAF fan-in: merge parallel asset branches."""
    nodes, trace = _append_trace(state, "assets_fan_in")
    urls = [
        "https://pureflow.sourcea.app/",
        "https://sourcea.app/sourcea/case-studies/pureflow",
    ]
    status = "PASS" if state.get("landing_outline") and state.get("report_template") else "BLOCK"
    return {
        **state,
        "nodes_executed": nodes,
        "maf_trace": trace,
        "artifact_urls": urls,
        "maf_internal_status": status,
    }


def maf_checkpoint_node(state: MafState) -> MafState:
    """MAF checkpointing — durable state id for replay orientation."""
    nodes, trace = _append_trace(state, "maf_checkpoint")
    ckpt = f"maf-ckpt-{uuid4().hex[:12]}"
    return {**state, "nodes_executed": nodes, "maf_trace": trace, "maf_ckpt_ref": ckpt}


def maf_observability_node(state: MafState) -> MafState:
    """MAF trace=True stand-in — feeds Proof Engine orientation fields."""
    nodes, trace = _append_trace(state, "maf_observability")
    return {**state, "nodes_executed": nodes, "maf_trace": trace}


def human_review_stub_node(state: MafState) -> MafState:
    """MAF false_branch orientation — human-in-the-loop when internal status BLOCK."""
    nodes, trace = _append_trace(state, "human_review_stub")
    return {**state, "nodes_executed": nodes, "maf_trace": trace}


def _route_after_fan_in(state: MafState) -> str:
    if state.get("maf_internal_status") == "PASS":
        return "maf_checkpoint"
    return "human_review_stub"


def build_maf_factory_workflow():
    graph = StateGraph(MafState)
    graph.add_node("offer_engineer", offer_engineer_node)
    graph.add_node("asset_landing", asset_landing_node)
    graph.add_node("asset_report", asset_report_node)
    graph.add_node("assets_fan_in", assets_fan_in_node)
    graph.add_node("maf_checkpoint", maf_checkpoint_node)
    graph.add_node("maf_observability", maf_observability_node)
    graph.add_node("human_review_stub", human_review_stub_node)

    graph.set_entry_point("offer_engineer")
    # Sequential fan-out sim (true parallel fan-out needs MAF SDK or LangGraph reducers)
    graph.add_edge("offer_engineer", "asset_landing")
    graph.add_edge("asset_landing", "asset_report")
    graph.add_edge("asset_report", "assets_fan_in")
    graph.add_conditional_edges("assets_fan_in", _route_after_fan_in)
    graph.add_edge("maf_checkpoint", "maf_observability")
    graph.add_edge("maf_observability", END)
    graph.add_edge("human_review_stub", END)
    return graph.compile()


# Back-compat alias
build_maf_workflow_graph = build_maf_factory_workflow


def run_maf_workflow(job: JobInput) -> JobState:
    app = build_maf_factory_workflow()
    initial: MafState = {"job": job.to_dict(), "nodes_executed": [], "maf_trace": []}
    final = app.invoke(initial)
    return JobState(
        job=job,
        offer_headline=final.get("offer_headline", ""),
        offer_summary=final.get("offer_summary", ""),
        gate_verdict="",
        gate_reasons=[],
        nodes_executed=list(final.get("nodes_executed") or []),
        artifact_urls=list(final.get("artifact_urls") or []),
    )


def maf_workflow_metadata(state: JobState, *, maf_trace: list[str] | None = None) -> dict[str, Any]:
    meta: dict[str, Any] = {
        "runtime_embed": "maf-hybrid-v1",
        "agent_framework": "maf-sim-v1",
        "maf_pattern": MAF_PATTERN_ID,
        "maf_sim_at": utc_now(),
    }
    if maf_trace:
        meta["maf_trace"] = maf_trace
    return meta


def run_maf_workflow_with_meta(job: JobInput) -> tuple[JobState, dict[str, Any]]:
    app = build_maf_factory_workflow()
    initial: MafState = {"job": job.to_dict(), "nodes_executed": [], "maf_trace": []}
    final = app.invoke(initial)
    state = JobState(
        job=job,
        offer_headline=final.get("offer_headline", ""),
        offer_summary=final.get("offer_summary", ""),
        gate_verdict="",
        gate_reasons=[],
        nodes_executed=list(final.get("nodes_executed") or []),
        artifact_urls=list(final.get("artifact_urls") or []),
    )
    meta = maf_workflow_metadata(
        state,
        maf_trace=list(final.get("maf_trace") or []),
    )
    meta["maf_ckpt_ref"] = final.get("maf_ckpt_ref", "")
    meta["maf_internal_status"] = final.get("maf_internal_status", "")
    meta["landing_outline"] = final.get("landing_outline", "")
    meta["report_template"] = final.get("report_template", "")
    return state, meta
