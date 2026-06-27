"""LangGraph gate — intake → plan → validate → receipt."""
from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from factory_runtime_spike.types_v1 import FORBIDDEN_PROMPT_MARKERS, JobInput, JobState


class GraphState(TypedDict, total=False):
    job: dict[str, Any]
    offer_headline: str
    offer_summary: str
    gate_verdict: str
    gate_reasons: list[str]
    nodes_executed: list[str]
    artifact_urls: list[str]


def _job_from_state(state: GraphState) -> JobInput:
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


def intake_node(state: GraphState) -> GraphState:
    job = _job_from_state(state)
    nodes = list(state.get("nodes_executed") or [])
    nodes.append("intake")
    reasons: list[str] = []
    verdict = "PASS"
    if len(job.prompt.strip()) < 40:
        verdict = "BLOCK"
        reasons.append("prompt_too_short")
    for marker in FORBIDDEN_PROMPT_MARKERS:
        if marker in job.prompt:
            verdict = "BLOCK"
            reasons.append(f"forbidden_marker:{marker}")
    return {
        **state,
        "nodes_executed": nodes,
        "gate_verdict": verdict,
        "gate_reasons": reasons,
    }


def plan_node(state: GraphState) -> GraphState:
    job = _job_from_state(state)
    nodes = list(state.get("nodes_executed") or [])
    nodes.append("plan")
    headline = f"Proof-backed {job.vertical.replace('_', ' ')} — {job.proof_artifact}"
    summary = (
        f"Offer for {job.audience}: documented service proof after every visit, "
        f"clear tiers, and mobile booking."
    )
    return {
        **state,
        "nodes_executed": nodes,
        "offer_headline": headline,
        "offer_summary": summary,
        "artifact_urls": [
            "https://pureflow.sourcea.app/",
            "https://sourcea.app/sourcea/case-studies/pureflow",
        ],
    }


def validate_node(state: GraphState) -> GraphState:
    nodes = list(state.get("nodes_executed") or [])
    nodes.append("validate_gate")
    reasons = list(state.get("gate_reasons") or [])
    verdict = state.get("gate_verdict") or "PASS"
    if not state.get("offer_headline"):
        verdict = "BLOCK"
        reasons.append("missing_offer_headline")
    if not state.get("artifact_urls"):
        verdict = "BLOCK"
        reasons.append("missing_artifact_urls")
    return {
        **state,
        "nodes_executed": nodes,
        "gate_verdict": verdict,
        "gate_reasons": reasons,
    }


def receipt_node(state: GraphState) -> GraphState:
    nodes = list(state.get("nodes_executed") or [])
    nodes.append("receipt")
    return {**state, "nodes_executed": nodes}


def build_factory_gate_graph():
    graph = StateGraph(GraphState)
    graph.add_node("intake", intake_node)
    graph.add_node("plan", plan_node)
    graph.add_node("validate_gate", validate_node)
    graph.add_node("receipt", receipt_node)
    graph.set_entry_point("intake")
    graph.add_edge("intake", "plan")
    graph.add_edge("plan", "validate_gate")
    graph.add_edge("validate_gate", "receipt")
    graph.add_edge("receipt", END)
    return graph.compile()


def run_civilization_gate(swarm_receipt: dict[str, Any]) -> dict[str, Any]:
    """Bridge Forge swarm/civilization receipt → LangGraph-style PASS/BLOCK verdict."""
    state = str(swarm_receipt.get("state") or "")
    ok = bool(swarm_receipt.get("ok"))
    critic = swarm_receipt.get("critic_aggregate") or {}
    if ok and state == "DONE" and critic.get("approved", True):
        lg_verdict = "PASS"
    elif state == "FAILED" or not ok:
        lg_verdict = "BLOCK"
    else:
        lg_verdict = "ADVISORY"
    return {
        "gate_verdict": lg_verdict,
        "gate_reasons": [
            f"swarm_state:{state}",
            f"critic_approved:{critic.get('approved')}",
            f"score:{critic.get('score')}",
        ],
        "swarm_id": swarm_receipt.get("swarm_id"),
        "schema": "forge-civilization-langgraph-bridge-v1",
    }


def run_advisor_gate(advisor_receipt: dict[str, Any]) -> dict[str, Any]:
    """Bridge Forge advisor receipt → LangGraph-style PASS/BLOCK verdict."""
    gate = advisor_receipt.get("quality_gate") or {}
    verdict = gate.get("verdict") or "SKIP"
    if verdict == "PASS" and gate.get("execution_allowed"):
        lg_verdict = "PASS"
    elif verdict in ("REVISE", "REJECT"):
        lg_verdict = "BLOCK"
    else:
        lg_verdict = "ADVISORY"
    agent_ok = bool((advisor_receipt.get("agent") or {}).get("ok"))
    if not agent_ok:
        lg_verdict = "BLOCK"
    return {
        "gate_verdict": lg_verdict,
        "gate_reasons": [f"forge_quality:{verdict}", f"agent_ok:{agent_ok}"],
        "advisor_id": advisor_receipt.get("advisor_id"),
        "schema": "forge-advisor-langgraph-bridge-v1",
    }


def run_langgraph_gate(job: JobInput) -> JobState:
    initial = JobState(job=job)
    app = build_factory_gate_graph()
    final = app.invoke(initial.to_graph_state())
    return JobState(
        job=job,
        offer_headline=final.get("offer_headline", ""),
        offer_summary=final.get("offer_summary", ""),
        gate_verdict=final.get("gate_verdict", "BLOCK"),
        gate_reasons=list(final.get("gate_reasons") or []),
        nodes_executed=list(final.get("nodes_executed") or []),
        artifact_urls=list(final.get("artifact_urls") or []),
    )


def run_validate_and_receipt_nodes(state: JobState) -> JobState:
    """SourceA gate only — after MAF or external plan draft."""
    gs = state.to_graph_state()
    gs = validate_node(gs)
    gs = receipt_node(gs)
    return JobState(
        job=state.job,
        offer_headline=gs.get("offer_headline", state.offer_headline),
        offer_summary=gs.get("offer_summary", state.offer_summary),
        gate_verdict=gs.get("gate_verdict", "BLOCK"),
        gate_reasons=list(gs.get("gate_reasons") or []),
        nodes_executed=list(gs.get("nodes_executed") or []),
        artifact_urls=list(gs.get("artifact_urls") or []),
    )
