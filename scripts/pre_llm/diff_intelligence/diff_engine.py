"""D13 orchestration — git diff + D3 impact map before LLM."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.dependency_graph.store import load_canonical as load_d3
from pre_llm.context_ranking.store import load_canonical as load_d9
from pre_llm.validation_layer.validation_engine import run_validation_layer
from pre_llm.validation_layer.store import load_canonical as load_d12
from pre_llm.diff_intelligence.focus_reader import collect_focus_changes
from pre_llm.diff_intelligence.git_diff_reader import collect_git_changes
from pre_llm.diff_intelligence.impact_mapper import build_impact_map, enrich_changes_with_impact
from pre_llm.planning_engine.store import load_canonical as load_d10
from pre_llm.diff_intelligence.store import DIFF_SSOT_PATH, SCHEMA, load_canonical, write_canonical

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_DIFF_INTELLIGENCE_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def _packet_diff_from_canonical(canonical: dict[str, Any]) -> dict[str, Any]:
    return {
        "changes": [
            {
                "change_id": c.get("change_id"),
                "path": c.get("path"),
                "kind": c.get("kind"),
                "lines_added": c.get("lines_added"),
                "lines_removed": c.get("lines_removed"),
                "scope": c.get("scope"),
                "in_ranked_focus": c.get("in_ranked_focus"),
                "impact": c.get("impact"),
            }
            for c in (canonical.get("changes") or [])[:32]
        ],
        "impact_map": canonical.get("impact_map") or {},
        "producer": "D13",
        "git_scope": canonical.get("git_scope"),
        "diff_ready": canonical.get("diff_ready"),
    }


def run_diff_intelligence(
    *,
    text: str,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    commits_back: int = 3,
) -> dict:
    input_text = (text or "").strip()
    if not input_text:
        return {"ok": False, "error": "text required"}

    root = _repo_root(repo_root)
    tid = task_id or f"diff-intelligence:{root.name}"

    if not force_refresh:
        cached = load_canonical()
        if (
            cached
            and cached.get("input_text") == input_text
            and cached.get("repo_root") == str(root)
            and DIFF_SSOT_PATH.is_file()
        ):
            return {
                "ok": True,
                **cached,
                "cached": True,
                "packet_diff": _packet_diff_from_canonical(cached),
            }

    d12 = load_d12()
    if not d12 or d12.get("input_text") != input_text or not d12.get("validation_ready"):
        d12_live = run_validation_layer(
            text=input_text,
            repo_root=str(root),
            task_id=f"d13-{tid}",
            force_refresh=force_refresh,
        )
        if not d12_live.get("ok"):
            return {"ok": False, "error": "D12 validation layer required", "d12": d12_live}
        d12 = d12_live

    d3 = load_d3()
    if not d3 or not d3.get("dependency_ready"):
        return {"ok": False, "error": "D3 dependency graph required"}

    d9 = load_d9() or {}
    d10 = load_d10() or {}
    focus_paths = [e.get("path") for e in (d9.get("ranked_evidence") or []) if e.get("path")]

    raw_changes, git_scope = collect_git_changes(root, commits_back=commits_back)
    if not raw_changes:
        raw_changes = collect_focus_changes(d9=d9, d10=d10)
        if raw_changes:
            git_scope = "no_git+d9_focus" if git_scope == "no_git" else f"{git_scope}+d9_focus"
    changes = enrich_changes_with_impact(
        changes=raw_changes,
        d3=d3,
        repo_root=str(root),
        focus_paths=focus_paths,
    )
    impact_map = build_impact_map(changes)

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": tid,
        "repo_root": str(root),
        "input_text": input_text,
        "producer": "D13",
        "git_scope": git_scope,
        "commits_back": commits_back,
        "change_count": len(changes),
        "changes": changes,
        "impact_map": impact_map,
        "diff_ready": len(changes) > 0,
        "d12_ref": d12.get("generated_at"),
        "d3_ref": d3.get("generated_at"),
        "authority": "Semantic diff + D3 impact — read-only git, no LLM",
    }
    write_canonical(canonical=canonical, task_id=tid)

    return {
        "ok": True,
        **canonical,
        "cached": False,
        "packet_diff": _packet_diff_from_canonical(canonical),
    }
