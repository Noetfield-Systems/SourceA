"""Non-git fallback — infer change focus from D9/D10 substrates."""
from __future__ import annotations

from typing import Any


def _looks_like_file_path(path: str) -> bool:
    p = (path or "").strip()
    if not p or " " in p:
        return False
    if p.startswith("d1-sym") or p.startswith("d5-doc:"):
        return False
    return "/" in p or p.endswith((".py", ".md", ".json", ".sh", ".js", ".ts"))


def collect_focus_changes(
    *,
    d9: dict[str, Any],
    d10: dict[str, Any] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    out: list[dict[str, Any]] = []

    for row in (d9.get("ranked_evidence") or []):
        path = (row.get("path") or "").strip()
        if not _looks_like_file_path(path) or path in seen:
            continue
        seen.add(path)
        out.append(
            {
                "path": path,
                "kind": "semantic_focus",
                "lines_added": 0,
                "lines_removed": 0,
                "binary": False,
                "scope": "d9_ranked_focus",
                "focus_score": row.get("score"),
                "focus_rank": row.get("rank"),
            }
        )
        if len(out) >= limit:
            return out

    graph = (d10 or {}).get("graph") or {}
    for node in graph.get("nodes") or []:
        for ref in node.get("evidence_refs") or []:
            path = str(ref).strip()
            if not _looks_like_file_path(path) or path in seen:
                continue
            seen.add(path)
            out.append(
                {
                    "path": path,
                    "kind": "semantic_focus",
                    "lines_added": 0,
                    "lines_removed": 0,
                    "binary": False,
                    "scope": "d10_plan_evidence",
                }
            )
            if len(out) >= limit:
                return out
    return out
