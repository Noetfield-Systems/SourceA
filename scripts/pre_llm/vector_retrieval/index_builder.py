"""Build D5 vector index from D1 + docs."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path

from pre_llm.code_intelligence.store import load_canonical as load_d1
from pre_llm.vector_retrieval.chunk_builder import build_all_chunks
from pre_llm.vector_retrieval.store import SCHEMA, VECTOR_SSOT_PATH, load_canonical, write_canonical

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_VECTOR_INDEX_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def run_full_index(
    *,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    root = _repo_root(repo_root)
    tid = task_id or f"vector-index:{root.name}"

    if not force_refresh:
        cached = load_canonical()
        if cached and cached.get("repo_root") == str(root) and VECTOR_SSOT_PATH.is_file():
            return {"ok": True, **cached, "cached": True}

    d1 = load_d1()
    if not d1:
        return {"ok": False, "error": "D1 code_intelligence_v1.json required — run D1 index first"}

    chunks = build_all_chunks(d1=d1, repo_root=root)
    if not chunks:
        return {"ok": False, "error": "no chunks built"}

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": tid,
        "repo_root": str(root),
        "producer": "D5",
        "chunk_count": len(chunks),
        "chunks": chunks,
        "retrieval_ready": len(chunks) >= 10,
        "method": "token_overlap_v1",
        "d1_ref": d1.get("generated_at"),
    }
    write_canonical(canonical=canonical, task_id=tid)
    return {"ok": True, **canonical, "cached": False}
