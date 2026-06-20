"""Hub API — GET /api/diff-intelligence-v1"""
from __future__ import annotations

from pre_llm.diff_intelligence.diff_engine import run_diff_intelligence
from pre_llm.diff_intelligence.store import DIFF_SSOT_PATH, SCHEMA


def diff_intelligence_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    commits_back: int = 3,
) -> dict:
    result = run_diff_intelligence(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
        commits_back=commits_back,
    )
    if not result.get("ok"):
        return result
    return {
        **result,
        "path": str(DIFF_SSOT_PATH),
        "schema": SCHEMA,
        "api": "/api/diff-intelligence-v1",
        "producer": "D13",
    }
