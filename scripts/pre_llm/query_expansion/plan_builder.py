"""Declarative retrieval plan — MDP-style, diffable JSON."""
from __future__ import annotations

from typing import Any


def build_retrieval_plan(
    *,
    queries: list[dict[str, Any]],
    goal_class: str,
    repo_root: str,
) -> dict[str, Any]:
    dense = [q for q in queries if q.get("mode") in ("dense", "hybrid")]
    sparse = [q for q in queries if q.get("mode") == "sparse"]

    return {
        "schema": "retrieval-plan-v1",
        "goal_class": goal_class,
        "repo_root": repo_root,
        "stages": [
            {"id": "dense", "engine": "d5_vector", "queries": [q["id"] for q in dense], "top_k": 8},
            {"id": "sparse", "engine": "symbol_path_bm25", "queries": [q["id"] for q in sparse], "top_k": 6},
            {"id": "memory", "engine": "d6_bridge", "queries": [q["id"] for q in queries[:2]], "top_k": 6},
        ],
        "fuse": {"method": "rrf", "k": 60},
        "cap": {"per_corpus": 12, "token_budget": 4000, "max_queries": len(queries)},
        "sources": ["D5", "D6", "D1"],
        "producer": "D7",
    }
