"""Goal-class query templates — rule-based, no LLM."""
from __future__ import annotations

import re
from typing import Any

_GOAL_SUFFIXES: dict[str, tuple[str, ...]] = {
    "fix": ("validator failure", "dependency impact", "error signature"),
    "build": ("module scaffold", "API wire", "validate gate"),
    "refactor": ("module graph", "safe move order", "regression validator"),
    "debug": ("root cause trace", "call graph", "reproduce signal"),
    "audit": ("alignment drift", "locked law compare", "artifact inventory"),
    "explain": ("architecture overview", "symbol index", "dependency path"),
    "validate": ("validate-*.sh", "preflight substrate", "gate receipt"),
    "ship": ("hub rebuild", "validator PASS", "provenance record"),
    "explore": ("code index scan", "file locate", "symbol search"),
    "other": ("clarify intent", "gather context", "WTM step map"),
}


def _tokenize_paths(text: str) -> list[str]:
    found = re.findall(r"[\w./-]+\.(?:py|sh|md|json|js|ts|tsx)", text, re.I)
    dirs = re.findall(r"(?:scripts|pre_llm|knowledge-library|archive)/[\w./-]+", text, re.I)
    out: list[str] = []
    for item in found + dirs:
        if item not in out:
            out.append(item)
    return out[:6]


def _d_step_refs(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"\bD\d+(?:\.\d+)?\b", text, re.I)))[:4]


def build_query_variants(
    *,
    text: str,
    goal_class: str,
    symbols: list[str],
    decomposition_tree: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    base = (text or "").strip()
    if not base:
        return []

    queries: list[dict[str, Any]] = []
    queries.append(
        {
            "id": "primary",
            "text": base,
            "mode": "hybrid",
            "source": "user",
            "top_k": 8,
            "weight": 1.0,
        }
    )

    for i, suffix in enumerate(_GOAL_SUFFIXES.get(goal_class, _GOAL_SUFFIXES["other"])):
        queries.append(
            {
                "id": f"goal-{goal_class}-{i}",
                "text": f"{base} {suffix}".strip(),
                "mode": "dense",
                "source": "goal_template",
                "top_k": 6,
                "weight": 0.7,
            }
        )

    if symbols:
        sym_text = " ".join(symbols[:12])
        queries.append(
            {
                "id": "symbol-expansion",
                "text": sym_text,
                "mode": "sparse",
                "source": "d1_symbols",
                "top_k": 10,
                "weight": 0.85,
                "symbols": symbols[:12],
            }
        )

    for step in decomposition_tree:
        kind = step.get("kind") or ""
        if kind not in ("retrieve", "graph", "diagnose", "validate", "intent"):
            continue
        title = step.get("title") or step.get("id") or "step"
        queries.append(
            {
                "id": f"decomp-{step.get('id', title)}",
                "text": f"{base} — {title}",
                "mode": "dense" if kind == "retrieve" else "hybrid",
                "source": "d4_decomposition",
                "top_k": 5,
                "weight": 0.6,
                "step_kind": kind,
            }
        )

    for path in _tokenize_paths(base):
        queries.append(
            {
                "id": f"path-{path.replace('/', '-')[:40]}",
                "text": path,
                "mode": "sparse",
                "source": "path_token",
                "top_k": 4,
                "weight": 0.75,
            }
        )

    for dstep in _d_step_refs(base):
        queries.append(
            {
                "id": f"wtm-{dstep.lower()}",
                "text": f"{dstep} pre-LLM world model gate packet",
                "mode": "hybrid",
                "source": "wtm_ref",
                "top_k": 6,
                "weight": 0.8,
            }
        )

    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for q in queries:
        key = (q.get("text") or "").strip().lower()
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(q)
    return deduped
