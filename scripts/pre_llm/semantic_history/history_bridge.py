"""L5 semantic change history — git commits + path relevance (read-only)."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[3]


def _keywords(text: str) -> list[str]:
    return list(dict.fromkeys(re.findall(r"[a-z][a-z0-9_]{3,}", (text or "").lower())))[:10]


def build_semantic_history(*, query_text: str, repo_root: str | None = None, limit: int = 8) -> dict[str, Any]:
    from pre_llm.memory_git_bridge.git_reader import read_git_commits  # noqa: WPS433

    root = Path(repo_root or SOURCE_A).expanduser().resolve()
    needles = _keywords(query_text)
    commits = read_git_commits(root, limit=limit * 2)
    scored: list[tuple[int, dict]] = []
    for row in commits:
        hay = f"{row.get('summary') or ''} {row.get('sha') or ''}".lower()
        score = sum(1 for n in needles if n in hay) if needles else 1
        if score:
            scored.append((score, row))
    scored.sort(key=lambda x: (-x[0], x[1].get("timestamp") or ""), reverse=False)
    hits = [r for _, r in scored[:limit]]
    return {
        "ok": True,
        "producer": "L5",
        "repo_root": str(root),
        "commit_count": len(hits),
        "commits": hits,
        "query_keywords": needles,
    }
