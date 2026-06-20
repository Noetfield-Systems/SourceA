"""D6 query orchestration."""
from __future__ import annotations

from pre_llm.memory_git_bridge.bridge_builder import build_bridge_index
from pre_llm.memory_git_bridge.query_engine import filter_slots
from pre_llm.memory_git_bridge.store import load_canonical


def run_bridge(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    top_k: int = 12,
) -> dict:
    built = build_bridge_index(repo_root=repo_root, task_id=task_id, force_refresh=force_refresh)
    if not built.get("ok"):
        return built

    canonical = load_canonical()
    all_slots = canonical.get("slots") or []
    hits = filter_slots(all_slots, text, top_k=top_k)

    return {
        "ok": True,
        "schema": canonical.get("schema"),
        "generated_at": canonical.get("generated_at"),
        "repo_root": canonical.get("repo_root"),
        "task_id": task_id or canonical.get("task_id"),
        "query": text,
        "slot_count": len(all_slots),
        "bridge_ready": bool(canonical.get("bridge_ready")),
        "git_available": bool(canonical.get("git_available")),
        "memory_role": canonical.get("memory_role"),
        "read_only": True,
        "hits": hits,
        "sources": canonical.get("sources") or {},
        "packet_memory": {
            "slots": [
                {
                    "slot_id": h.get("slot_id"),
                    "kind": h.get("kind"),
                    "task_id": h.get("task_id"),
                    "timestamp": h.get("timestamp"),
                    "summary": h.get("summary"),
                    "path": h.get("path"),
                    "excerpt": (h.get("excerpt") or "")[:400],
                    "score": h.get("score"),
                }
                for h in hits
            ],
            "producer": "D6",
        },
        "retrieval_feed": [
            {
                "chunk_id": h.get("slot_id"),
                "path": h.get("path"),
                "kind": h.get("kind"),
                "excerpt": (h.get("excerpt") or h.get("summary") or "")[:400],
                "score": h.get("score"),
            }
            for h in hits
        ],
        "cached": built.get("cached", False),
    }
