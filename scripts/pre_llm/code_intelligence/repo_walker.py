"""Scan repo recursively — raw file paths only."""
from __future__ import annotations

from pathlib import Path

from pre_llm.code_intelligence.store import SKIP_DIR_NAMES


def _skip_dir(name: str) -> bool:
    return name in SKIP_DIR_NAMES or (name.startswith(".") and name != ".github")


def walk_repo(repo_root: Path) -> list[str]:
    repo_root = repo_root.resolve()
    paths: list[str] = []
    for path in sorted(repo_root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(repo_root)
        if any(_skip_dir(part) for part in rel.parts[:-1]):
            continue
        paths.append(rel.as_posix())
    return paths
