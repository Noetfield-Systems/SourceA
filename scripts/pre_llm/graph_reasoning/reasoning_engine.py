"""D8 orchestration — D3 graph → reasoning paths."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.code_intelligence.store import load_canonical as load_d1
from pre_llm.dependency_graph.graph_engine import run_dependency_graph, simulate_impact
from pre_llm.dependency_graph.store import load_canonical as load_d3
from pre_llm.graph_reasoning.seed_resolver import resolve_seeds
from pre_llm.graph_reasoning.store import REASONING_SSOT_PATH, SCHEMA, load_canonical, write_canonical
from pre_llm.graph_reasoning.traversal import forward_traversal, root_cause_trace

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_GRAPH_REASONING_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def _impact_path(*, seed_type: str, seed_value: str, d3: dict[str, Any]) -> dict[str, Any]:
    impact = simulate_impact(target_type=seed_type, target=seed_value, canonical=d3)
    nodes = [seed_value]
    nodes.extend(impact.get("direct_dependents") or [])
    nodes.extend(impact.get("transitive_dependents") or [])
    deduped: list[str] = []
    for n in nodes:
        if n not in deduped:
            deduped.append(n)
    return {
        "path_id": f"impact-{seed_type}-{seed_value.replace('/', '-')[:40]}",
        "kind": "impact",
        "seed": seed_value,
        "seed_type": seed_type,
        "nodes": deduped[:32],
        "edges": [
            {"from": seed_value, "to": d, "kind": "impacts"}
            for d in (impact.get("direct_dependents") or [])[:16]
        ],
        "direct_dependent_count": impact.get("direct_dependent_count", 0),
        "transitive_dependent_count": impact.get("transitive_dependent_count", 0),
        "summary": (
            f"Impact simulation {seed_type}:{seed_value} — "
            f"{impact.get('direct_dependent_count', 0)} direct · "
            f"{impact.get('transitive_dependent_count', 0)} transitive"
        ),
        "impact": impact,
    }


def _packet_reasoning_from_canonical(canonical: dict[str, Any]) -> dict[str, Any]:
    return {
        "paths": [
            {
                "path_id": p.get("path_id"),
                "kind": p.get("kind"),
                "seed": p.get("seed"),
                "seed_type": p.get("seed_type"),
                "node_count": p.get("node_count"),
                "summary": p.get("summary"),
            }
            for p in (canonical.get("paths") or [])
        ],
        "producer": "D8",
    }


def run_graph_reasoning(
    *,
    text: str = "",
    target: str = "",
    target_type: str = "file",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    root = _repo_root(repo_root)
    tid = task_id or f"graph-reasoning:{root.name}"
    input_text = (text or target or "").strip()

    if not force_refresh:
        cached = load_canonical()
        if (
            cached
            and cached.get("input_text") == input_text
            and cached.get("repo_root") == str(root)
            and REASONING_SSOT_PATH.is_file()
        ):
            return {
                "ok": True,
                **cached,
                "cached": True,
                "packet_reasoning": _packet_reasoning_from_canonical(cached),
            }

    d3_live = run_dependency_graph(repo_root=str(root), task_id=f"d8-{tid}", force_refresh=force_refresh)
    if not d3_live.get("ok"):
        return {"ok": False, "error": "D3 dependency graph required", "d3": d3_live}

    d3 = load_d3() or d3_live
    if not d3.get("dependency_ready"):
        return {"ok": False, "error": "D3 not ready"}

    d1 = load_d1()
    seeds = resolve_seeds(text=input_text, target=target, target_type=target_type, d1=d1, d3=d3)
    if not seeds:
        return {"ok": False, "error": "no seeds resolved"}

    paths: list[dict[str, Any]] = []
    for seed in seeds[:4]:
        stype = seed["type"]
        sval = seed["value"]
        paths.append(_impact_path(seed_type=stype, seed_value=sval, d3=d3))
        paths.append(root_cause_trace(target=sval, target_type=stype, d3=d3))
        if stype == "file":
            paths.append(forward_traversal(start_file=sval, d3=d3))

    kinds = {p.get("kind") for p in paths}
    reasoning_ready = len(paths) >= 2 and "impact" in kinds and ("root_cause" in kinds or "traversal" in kinds)

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": tid,
        "repo_root": str(root),
        "input_text": input_text,
        "producer": "D8",
        "seeds": seeds,
        "path_count": len(paths),
        "paths": paths,
        "reasoning_ready": reasoning_ready,
        "d3_ref": d3.get("generated_at"),
        "graph_stats": d3.get("graph_stats"),
    }
    write_canonical(canonical=canonical, task_id=tid)

    return {
        "ok": True,
        **canonical,
        "cached": False,
        "packet_reasoning": _packet_reasoning_from_canonical(canonical),
    }
