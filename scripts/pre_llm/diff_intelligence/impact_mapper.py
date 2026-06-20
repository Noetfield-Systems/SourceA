"""Map changed files to D3 dependency impact — no LLM."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pre_llm.dependency_graph.graph_engine import simulate_impact


def _norm_path(path: str, repo_root: str) -> str:
    p = Path(path)
    if p.is_absolute():
        try:
            return str(p.resolve().relative_to(Path(repo_root).resolve()))
        except ValueError:
            return path
    return path.replace("\\", "/")


def _severity(*, direct: int, transitive: int) -> str:
    if transitive >= 12 or direct >= 6:
        return "high"
    if transitive >= 4 or direct >= 2:
        return "medium"
    if direct >= 1 or transitive >= 1:
        return "low"
    return "none"


def enrich_changes_with_impact(
    *,
    changes: list[dict[str, Any]],
    d3: dict[str, Any],
    repo_root: str,
    focus_paths: list[str] | None = None,
) -> list[dict[str, Any]]:
    focus = {_norm_path(p, repo_root) for p in (focus_paths or []) if p}
    idx = d3.get("impact_index") or {}
    file_rev = idx.get("file_dependents") or {}
    out: list[dict[str, Any]] = []

    for raw in changes:
        rel = _norm_path(raw.get("path") or "", repo_root)
        impact = simulate_impact(target_type="file", target=rel, canonical=d3)
        upstream = sorted(set(file_rev.get(rel, [])))[:20]
        direct = impact.get("direct_dependents") or []
        transitive = impact.get("transitive_dependents") or []
        direct_n = int(impact.get("direct_dependent_count") or len(direct))
        trans_n = int(impact.get("transitive_dependent_count") or len(transitive))
        row = {
            **raw,
            "path": rel,
            "change_id": f"diff-{rel.replace('/', '-')[:120]}",
            "in_ranked_focus": rel in focus,
            "impact": {
                "upstream_files": upstream,
                "downstream_files": direct[:20],
                "transitive_files": transitive[:30],
                "direct_dependent_count": direct_n,
                "transitive_dependent_count": trans_n,
                "severity": _severity(direct=direct_n, transitive=trans_n),
            },
        }
        out.append(row)
    return out


def build_impact_map(changes: list[dict[str, Any]]) -> dict[str, Any]:
    modules_affected: set[str] = set()
    high: list[str] = []
    for c in changes:
        rel = c.get("path") or ""
        if rel.endswith(".py"):
            mod = Path(rel).with_suffix("").as_posix().replace("/", ".")
            if mod.startswith("scripts."):
                mod = mod[len("scripts.") :]
            modules_affected.add(mod)
        sev = (c.get("impact") or {}).get("severity")
        if sev == "high":
            high.append(rel)
    return {
        "files_changed": len(changes),
        "modules_affected": len(modules_affected),
        "high_impact_paths": high[:16],
        "focus_overlap": len([c for c in changes if c.get("in_ranked_focus")]),
    }
