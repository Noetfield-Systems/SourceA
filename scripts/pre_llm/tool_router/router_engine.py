"""D11 orchestration — D10 plan → capability selection with policy."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.planning_engine.planning_engine import run_planning_engine
from pre_llm.planning_engine.store import load_canonical as load_d10
from pre_llm.tool_router.capability_catalog import capabilities_for_kind
from pre_llm.tool_router.policy_engine import evaluate_tool_policy
from pre_llm.tool_router.store import ROUTER_SSOT_PATH, SCHEMA, load_canonical, write_canonical

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_TOOL_ROUTER_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def _packet_tools_from_canonical(canonical: dict[str, Any]) -> dict[str, Any]:
    return {
        "selection": [
            {
                "plan_node_id": s.get("plan_node_id"),
                "capability_id": s.get("capability_id"),
                "tool_id": s.get("tool_id"),
                "permission": s.get("permission"),
                "cost_estimate": s.get("cost_estimate"),
                "allowed": s.get("allowed"),
                "policy_gate": s.get("policy_gate"),
            }
            for s in (canonical.get("selection") or [])
        ],
        "producer": "D11",
        "total_cost_estimate": canonical.get("total_cost_estimate"),
    }


def _build_selection(
    *,
    plan_nodes: list[dict[str, Any]],
    goal_class: str,
    gate_mode: str,
) -> list[dict[str, Any]]:
    selection: list[dict[str, Any]] = []
    for node in plan_nodes:
        if node.get("kind") == "fallback":
            caps = capabilities_for_kind("fallback")
        else:
            caps = capabilities_for_kind(node.get("kind") or "plan")
        for cap in caps[:2]:
            policy = evaluate_tool_policy(
                capability=cap,
                plan_node=node,
                goal_class=goal_class,
                gate_mode=gate_mode,
            )
            selection.append(
                {
                    "plan_node_id": node.get("id"),
                    "plan_step_kind": node.get("kind"),
                    "capability_id": cap.get("capability_id"),
                    "tool_id": cap.get("tool_id"),
                    "permission": policy.get("permission"),
                    "cost_estimate": policy.get("cost_estimate"),
                    "allowed": policy.get("allowed"),
                    "policy_gate": policy.get("policy_gate"),
                    "reasons": policy.get("reasons"),
                }
            )
    return selection


def run_tool_router(
    *,
    text: str,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    gate_mode: str = "shadow",
) -> dict:
    input_text = (text or "").strip()
    if not input_text:
        return {"ok": False, "error": "text required"}

    root = _repo_root(repo_root)
    tid = task_id or f"tool-router:{root.name}"

    if not force_refresh:
        cached = load_canonical()
        if (
            cached
            and cached.get("input_text") == input_text
            and cached.get("repo_root") == str(root)
            and ROUTER_SSOT_PATH.is_file()
        ):
            return {
                "ok": True,
                **cached,
                "cached": True,
                "packet_tools": _packet_tools_from_canonical(cached),
            }

    d10 = load_d10()
    if not d10 or d10.get("input_text") != input_text or not d10.get("plan_ready"):
        d10_live = run_planning_engine(text=input_text, repo_root=str(root), task_id=f"d11-{tid}", force_refresh=force_refresh)
        if not d10_live.get("ok"):
            return {"ok": False, "error": "D10 plan required", "d10": d10_live}
        graph = d10_live.get("graph") or {}
        goal_class = d10_live.get("goal_class") or "other"
        d10_ref = d10_live.get("generated_at")
    else:
        graph = d10.get("graph") or {}
        goal_class = d10.get("goal_class") or "other"
        d10_ref = d10.get("generated_at")

    nodes = graph.get("nodes") or []
    if len(nodes) < 3:
        return {"ok": False, "error": "plan graph too small", "node_count": len(nodes)}

    selection = _build_selection(plan_nodes=nodes, goal_class=goal_class, gate_mode=gate_mode)
    total_cost = sum(int(s.get("cost_estimate") or 0) for s in selection)
    allowed_count = sum(1 for s in selection if s.get("allowed"))

    router_ready = len(selection) >= 3 and allowed_count >= 2

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": tid,
        "repo_root": str(root),
        "input_text": input_text,
        "producer": "D11",
        "goal_class": goal_class,
        "gate_mode": gate_mode,
        "selection": selection,
        "selection_count": len(selection),
        "allowed_count": allowed_count,
        "total_cost_estimate": total_cost,
        "router_ready": router_ready,
        "d10_ref": d10_ref,
        "authority": "Pre-LLM capability selection — not C3 execution router",
    }
    write_canonical(canonical=canonical, task_id=tid)

    return {
        "ok": True,
        **canonical,
        "cached": False,
        "packet_tools": _packet_tools_from_canonical(canonical),
    }
