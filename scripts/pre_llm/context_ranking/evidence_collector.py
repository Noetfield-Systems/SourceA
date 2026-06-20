"""Gather rankable evidence from D5–D8 substrates."""
from __future__ import annotations

from typing import Any


def _chunk_candidates(d5_hits: list[dict]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for h in d5_hits:
        cid = h.get("chunk_id") or h.get("path") or ""
        out.append(
            {
                "evidence_id": f"d5-{cid}",
                "kind": "retrieval_chunk",
                "source_step": "D5",
                "path": h.get("path") or "",
                "summary": (h.get("excerpt") or h.get("text") or "")[:300],
                "base_score": float(h.get("score") or 0.0),
                "chunk_id": cid,
            }
        )
    return out


def _memory_candidates(slots: list[dict]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for s in slots:
        sid = s.get("slot_id") or ""
        out.append(
            {
                "evidence_id": f"d6-{sid}",
                "kind": "memory_slot",
                "source_step": "D6",
                "path": s.get("path") or "",
                "summary": s.get("summary") or (s.get("excerpt") or "")[:300],
                "base_score": float(s.get("score") or 0.3),
                "slot_kind": s.get("kind"),
                "timestamp": s.get("timestamp"),
            }
        )
    return out


def _reasoning_candidates(paths: list[dict]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for p in paths:
        pid = p.get("path_id") or ""
        out.append(
            {
                "evidence_id": f"d8-{pid}",
                "kind": "reasoning_path",
                "source_step": "D8",
                "path": p.get("seed") or "",
                "summary": p.get("summary") or "",
                "base_score": 0.4,
                "path_kind": p.get("kind"),
                "node_count": p.get("node_count", 0),
                "graph_nodes": p.get("nodes") or [],
            }
        )
    return out


def _symbol_candidates(symbols: list[str], d1: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not d1:
        return []
    sym_map = d1.get("symbols") or {}
    out: list[dict[str, Any]] = []
    for name in symbols[:12]:
        meta = sym_map.get(name) if isinstance(sym_map, dict) else {}
        refs = (meta.get("references") or []) if isinstance(meta, dict) else []
        path = refs[0].get("file") if refs else ""
        out.append(
            {
                "evidence_id": f"d1-sym-{name}",
                "kind": "symbol",
                "source_step": "D1",
                "path": path or "",
                "summary": f"symbol {name}",
                "base_score": 0.35,
                "symbol": name,
            }
        )
    return out


def collect_evidence(
    *,
    d5_hits: list[dict],
    d6_slots: list[dict],
    d8_paths: list[dict],
    symbols: list[str],
    d1: dict[str, Any] | None,
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    items.extend(_chunk_candidates(d5_hits))
    items.extend(_memory_candidates(d6_slots))
    items.extend(_reasoning_candidates(d8_paths))
    items.extend(_symbol_candidates(symbols, d1))
    return items
