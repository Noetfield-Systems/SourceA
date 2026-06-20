"""Filter walk output to valid source files."""
from __future__ import annotations

from pathlib import Path

from pre_llm.code_intelligence.store import (
    MANDATORY_EXTENSIONS,
    MAX_FILE_BYTES,
    OPTIONAL_EXTENSIONS,
    SKIP_FILE_SUFFIXES,
)


def discover_files(repo_root: Path, paths: list[str]) -> list[str]:
    repo_root = repo_root.resolve()
    allowed = MANDATORY_EXTENSIONS | OPTIONAL_EXTENSIONS
    out: list[str] = []
    for rel in paths:
        suffix = Path(rel).suffix.lower()
        if suffix not in allowed and suffix not in {".sh", ".md", ".json", ".yaml", ".yml"}:
            continue
        if suffix in SKIP_FILE_SUFFIXES:
            continue
        full = repo_root / rel
        try:
            if full.stat().st_size > MAX_FILE_BYTES:
                continue
        except OSError:
            continue
        out.append(rel)
    return out
