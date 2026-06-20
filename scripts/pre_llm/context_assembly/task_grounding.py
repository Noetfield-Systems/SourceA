"""D15 task grounding — repo paths + snippets from query keywords (no LLM)."""
from __future__ import annotations

import re
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[3]
SCRIPTS = SOURCE_A / "scripts"


def _keywords(text: str) -> list[str]:
    raw = re.findall(r"[a-z][a-z0-9_]{3,}", (text or "").lower())
    return list(dict.fromkeys(raw))[:12]


def _snippet(path: Path, needles: list[str], *, max_chars: int = 800) -> str:
    if not path.is_file():
        return ""
    try:
        body = path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""
    low = body.lower()
    idx = 0
    for n in needles:
        pos = low.find(n.lower())
        if pos >= 0:
            idx = pos
            break
    return body[max(0, idx - 120) : idx + max_chars].strip()


def find_paths_for_query(text: str, *, limit: int = 8) -> list[str]:
    needles = _keywords(text)
    if not needles:
        return []
    hits: list[tuple[int, str]] = []
    for py in SCRIPTS.rglob("*.py"):
        if "node_modules" in py.parts or "__pycache__" in py.parts:
            continue
        try:
            sample = py.read_text(encoding="utf-8", errors="replace")[:8000].lower()
        except OSError:
            continue
        score = sum(1 for n in needles if n in sample)
        if score:
            rel = py.relative_to(SOURCE_A).as_posix()
            hits.append((score, rel))
    hits.sort(key=lambda x: (-x[0], x[1]))
    return [h[1] for h in hits[:limit]]


def build_grounding_block(*, query_text: str) -> dict:
    needles = _keywords(query_text)
    paths = find_paths_for_query(query_text)
    snippets = []
    for rel in paths[:5]:
        snip = _snippet(SOURCE_A / rel, needles)
        if snip:
            snippets.append({"path": rel, "snippet": snip})
    return {
        "keywords": needles,
        "paths": paths,
        "snippets": snippets,
        "producer": "D15-task-grounding",
    }
