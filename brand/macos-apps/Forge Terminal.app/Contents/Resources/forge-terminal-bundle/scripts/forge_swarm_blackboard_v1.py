#!/usr/bin/env python3
"""Forge Swarm Blackboard v1 — shared memory for parallel agent coordination."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
BOARD_PATH = SINA / "forge-swarm-blackboard-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_blackboard(*, goal: str, workspace_path: str) -> dict[str, Any]:
    return {
        "schema": "forge-swarm-blackboard-v1",
        "goal": goal,
        "workspace_path": workspace_path,
        "goals": [goal],
        "tasks": [],
        "artifacts": [],
        "repo_state": {},
        "repo_graph": {"nodes": [], "edges": []},
        "logs": [],
        "planner_votes": [],
        "critic_verdicts": [],
        "task_economy": [],
        "agent_bids": [],
        "round": 0,
        "at": _now(),
    }


def save_blackboard(board: dict[str, Any]) -> None:
    board["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    BOARD_PATH.write_text(json.dumps(board, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_blackboard() -> dict[str, Any]:
    try:
        return json.loads(BOARD_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def merge_plans(plans: list[dict[str, Any]], *, max_tasks: int = 8) -> list[str]:
    """Dedupe and rank tasks from parallel planner outputs."""
    scored: dict[str, float] = {}
    for i, plan in enumerate(plans):
        tasks = plan.get("tasks") or []
        if isinstance(tasks, str):
            tasks = [tasks]
        for j, task in enumerate(tasks):
            key = str(task).strip()
            if not key:
                continue
            scored[key] = scored.get(key, 0.0) + (3 - i * 0.1) + (6 - j) * 0.05
    ordered = sorted(scored.keys(), key=lambda k: scored[k], reverse=True)
    return ordered[:max_tasks]


def aggregate_critic_verdicts(verdicts: list[dict[str, Any]]) -> dict[str, Any]:
    """Majority vote + mean score from parallel critics."""
    if not verdicts:
        return {"approved": True, "score": 1.0, "method": "empty"}
    approved_votes = sum(1 for v in verdicts if v.get("approved"))
    scores = [float(v.get("score") or (1.0 if v.get("approved") else 0.0)) for v in verdicts]
    mean_score = sum(scores) / max(len(scores), 1)
    approved = approved_votes >= max(1, len(verdicts) // 2 + len(verdicts) % 2)
    issues: list[str] = []
    for v in verdicts:
        issues.extend(v.get("issues") or [])
    return {
        "approved": approved,
        "score": round(mean_score, 3),
        "votes": len(verdicts),
        "approved_votes": approved_votes,
        "issues": issues[:12],
    }


def build_repo_graph_light(*, workspace: Path, intel: dict[str, Any]) -> dict[str, Any]:
    """Light dependency graph from code intel or file list."""
    edges: list[list[str]] = []
    nodes: list[str] = []
    try:
        from pre_llm.code_intelligence.index_builder import run_full_index  # noqa: WPS433

        idx = run_full_index(repo_root=str(workspace), task_id=f"forge-graph:{workspace.name}")
        for e in (idx.get("module_graph") or idx.get("imports_graph") or [])[:200]:
            fr = e.get("from") or e.get("source")
            to = e.get("to") or e.get("target")
            if fr and to:
                nodes.extend([str(fr), str(to)])
                edges.append([str(fr), str(to)])
    except Exception:
        pass
    if not nodes:
        for f in (intel.get("files") if isinstance(intel.get("files"), list) else [])[:40]:
            nodes.append(str(f))
    nodes = sorted(set(nodes))[:120]
    return {"nodes": nodes, "edges": edges[:200]}


MAX_COST_PER_TASK = 10.0


def estimate_task_value(*, goal: str, repo_graph: dict[str, Any], founder_priority: bool = False) -> float:
    """Heuristic task value score."""
    nodes = len((repo_graph or {}).get("nodes") or [])
    base = 1.0 + min(nodes, 50) * 0.02
    if founder_priority:
        base += 2.0
    if len(goal) > 100:
        base += 0.5
    return round(base, 2)


def estimate_task_cost(*, task_text: str, repo_graph: dict[str, Any]) -> float:
    edges = len((repo_graph or {}).get("edges") or [])
    cost = 1.0 + min(edges, 100) * 0.01 + len(task_text) * 0.001
    return round(min(cost, MAX_COST_PER_TASK), 2)


def build_task_economy(*, tasks: list[str], goal: str, repo_graph: dict[str, Any]) -> list[dict[str, Any]]:
    """Build task economy entries with value/cost/priority."""
    economy: list[dict[str, Any]] = []
    for i, task in enumerate(tasks):
        economy.append({
            "id": f"task-{i + 1}",
            "goal": task,
            "value": estimate_task_value(goal=task, repo_graph=repo_graph),
            "cost_estimate": estimate_task_cost(task_text=task, repo_graph=repo_graph),
            "priority": i + 1,
            "status": "open",
        })
    return economy


def select_agent_for_task(task: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    """Lowest cost × highest reputation bid wins."""
    agents = [a for a in (registry.get("agents") or []) if a.get("role") == "builder"]
    if not agents:
        return {"agent_id": "builder-001", "bid": 1.0, "confidence": 0.5}
    best = None
    best_score = -1.0
    cost = float(task.get("cost_estimate") or 1.0)
    for agent in agents:
        rep = float(agent.get("reputation") or 0.5)
        eff = float(agent.get("cost_efficiency") or 1.0)
        score = rep * eff / max(cost, 0.1)
        if score > best_score:
            best_score = score
            best = agent
    return {
        "agent_id": best["id"] if best else "builder-001",
        "bid": round(cost / max(float(best.get("cost_efficiency") or 1.0) if best else 1.0, 0.1), 3),
        "confidence": round(float(best.get("reputation") or 0.5) if best else 0.5, 3),
    }


def collect_agent_bids(tasks: list[dict[str, Any]], registry: dict[str, Any]) -> list[dict[str, Any]]:
    return [{"task_id": t.get("id"), **select_agent_for_task(t, registry)} for t in tasks]
