"""Rule-based relevance scoring — intent + graph + retrieval + noise filter.

D9 blend weights (sum=1.0): intent 0.26 · overlap 0.22 · retrieval 0.28 · graph 0.12 · hybrid_sem 0.12
D5 hybrid retrieval (query_engine via embedding_provider): token 0.55 · semantic 0.45
"""
from __future__ import annotations

import re
from typing import Any

_GOAL_KEYWORDS: dict[str, tuple[str, ...]] = {
    "fix": ("fix", "error", "fail", "bug", "repair", "validate"),
    "build": ("build", "pre_llm", "api", "scaffold", "ship", "module"),
    "validate": ("validate", "gate", "smoke", "pass", "receipt"),
    "debug": ("debug", "trace", "root", "cause", "graph"),
    "ship": ("ship", "hub", "validator", "deploy"),
    "audit": ("audit", "alignment", "drift", "law"),
    "explain": ("explain", "essay", "doc", "overview"),
    "refactor": ("refactor", "graph", "module", "deps"),
    "explore": ("search", "index", "find", "retrieval"),
    "other": ("context", "packet", "intent"),
}

_NOISE_PATHS = ("/node_modules/", "/.git/", "/__pycache__/", ".pyc")


def _intent_score(*, goal_class: str, hay: str) -> float:
    keys = _GOAL_KEYWORDS.get(goal_class, _GOAL_KEYWORDS["other"])
    norm = hay.lower()
    hits = sum(1 for k in keys if k in norm)
    return min(1.0, hits / max(len(keys) * 0.35, 1))


def _text_overlap(query: str, hay: str) -> float:
    q = (query or "").lower()
    if not q:
        return 0.0
    tokens = [t for t in re.findall(r"[a-z0-9_./-]{3,}", q) if len(t) > 2]
    if not tokens:
        return 0.0
    norm = hay.lower()
    return sum(1 for t in tokens if t in norm) / len(tokens)


def _graph_score(*, path: str, graph_nodes: set[str]) -> float:
    if not path or not graph_nodes:
        return 0.0
    if path in graph_nodes:
        return 1.0
    base = path.rsplit("/", 1)[-1]
    for node in graph_nodes:
        if base and base in node:
            return 0.6
    return 0.0


def _is_noise(item: dict[str, Any]) -> bool:
    path = (item.get("path") or "").lower()
    return any(n in path for n in _NOISE_PATHS)


def _feedback_boost(path: str) -> float:
    try:
        from execution_intelligence.feedback_loop.loop_engine import read_signals  # noqa: WPS433

        boost = 0.0
        for sig in read_signals(limit=40):
            target = str(sig.get("target") or sig.get("path") or "")
            if target and path and target in path:
                boost += 0.08
        return min(0.25, boost)
    except Exception:
        return 0.0


def rank_evidence(
    *,
    candidates: list[dict[str, Any]],
    goal_class: str,
    query_text: str,
    graph_nodes: set[str],
    top_k: int = 16,
    min_score: float = 0.18,
) -> list[dict[str, Any]]:
    scored: list[dict[str, Any]] = []

    for item in candidates:
        if _is_noise(item):
            continue
        hay = " ".join(
            str(item.get(k) or "")
            for k in ("path", "summary", "symbol", "kind", "path_kind", "slot_kind")
        )
        intent = _intent_score(goal_class=goal_class, hay=hay)
        overlap = _text_overlap(query_text, hay)
        retrieval = min(1.0, float(item.get("base_score") or 0.0))
        graph = _graph_score(path=item.get("path") or "", graph_nodes=graph_nodes)

        if item.get("source_step") == "D8":
            graph = max(graph, 0.5)
        if item.get("kind") == "memory_slot":
            retrieval = max(retrieval, 0.25)

        hybrid_sem = retrieval if item.get("source_step") == "D5" else 0.0
        feedback = _feedback_boost(item.get("path") or "")
        total = round(
            0.26 * intent + 0.22 * overlap + 0.28 * retrieval + 0.12 * graph + 0.12 * hybrid_sem + feedback,
            4,
        )
        if total < min_score:
            continue

        scored.append(
            {
                **item,
                "score": total,
                "signals": {
                    "intent": round(intent, 3),
                    "query_overlap": round(overlap, 3),
                    "retrieval": round(retrieval, 3),
                    "graph": round(graph, 3),
                },
            }
        )

    scored.sort(key=lambda x: (-x["score"], x.get("evidence_id") or ""))

    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for row in scored:
        key = (row.get("path") or row.get("evidence_id") or "").lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(row)
        if len(deduped) >= top_k:
            break

    for i, row in enumerate(deduped):
        row["rank"] = i + 1

    return deduped
