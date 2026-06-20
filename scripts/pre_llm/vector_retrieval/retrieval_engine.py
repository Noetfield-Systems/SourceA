"""D5 query orchestration."""
from __future__ import annotations

import os

from pre_llm.vector_retrieval.index_builder import run_full_index
from pre_llm.vector_retrieval.query_engine import search_chunks
from pre_llm.vector_retrieval.store import load_canonical


def run_retrieval(
    *,
    text: str,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    top_k: int = 8,
) -> dict:
    built = run_full_index(repo_root=repo_root, task_id=task_id, force_refresh=force_refresh)
    if not built.get("ok"):
        return built

    canonical = load_canonical()
    chunks = canonical.get("chunks") or []
    hybrid = os.environ.get("SINA_L8_HYBRID", "1").strip() not in ("0", "false", "no")
    hits = search_chunks(chunks, text, top_k=top_k, hybrid=hybrid)
    return {
        "ok": True,
        "schema": canonical.get("schema"),
        "generated_at": canonical.get("generated_at"),
        "repo_root": canonical.get("repo_root"),
        "task_id": task_id or canonical.get("task_id"),
        "query": text,
        "chunk_count": len(chunks),
        "retrieval_ready": bool(canonical.get("retrieval_ready")),
        "hits": hits,
        "packet_retrieval": {
            "chunks": [
                {
                    "chunk_id": h.get("chunk_id"),
                    "path": h.get("path"),
                    "kind": h.get("kind"),
                    "score": h.get("score"),
                    "excerpt": (h.get("text") or "")[:400],
                }
                for h in hits
            ],
            "queries": [{"text": text, "top_k": top_k}],
            "producer": "D5+L8" if hybrid else "D5",
        },
        "hybrid_retrieval": hybrid,
        "cached": built.get("cached", False),
    }
