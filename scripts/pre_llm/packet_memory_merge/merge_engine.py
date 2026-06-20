"""D16 — budget-aware memory writeback into assembled packet (no D14/D15 recompute)."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.context_assembly.store import load_assembly_meta, load_canonical, write_canonical
from pre_llm.context_packet.schema import SCHEMA, validate_packet
from pre_llm.memory_git_bridge.query_engine import filter_slots
from pre_llm.packet_memory_merge.budget_policy import prune_slots, resolve_memory_budget
from pre_llm.packet_memory_merge.memory_collector import (
    collect_b_layer_slots,
    collect_d6_slots,
    collect_l5_history_slots,
    merge_slot_lists,
)
from pre_llm.packet_memory_merge.store import MERGE_SSOT_PATH, SCHEMA as MERGE_SCHEMA, write_canonical as write_merge_ssot

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_MEMORY_MERGE_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def _ensure_provenance_d16(pkt: dict) -> None:
    prov = pkt.setdefault("provenance", {})
    steps = list(prov.get("producer_steps") or [])
    if "D16" not in steps:
        steps.append("D16")
        prov["producer_steps"] = sorted(set(steps))
    artifacts = dict(prov.get("artifacts") or {})
    artifacts["D16"] = str(MERGE_SSOT_PATH)
    prov["artifacts"] = artifacts
    prov["memory_merge_at"] = _now()


def run_memory_merge_writeback(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    packet: dict | None = None,
) -> dict[str, Any]:
    """Write unified memory into packet.memory — strict writeback only."""
    input_text = (text or "").strip()
    root = _repo_root(repo_root)
    tid = task_id or f"memory-merge:{root.name}"

    pkt = packet or load_canonical()
    if not pkt or pkt.get("schema") != SCHEMA:
        return {"ok": False, "error": "D15 assembled packet required", "producer": "D16"}

    packet_query = str(pkt.get("input_text") or "").strip()
    query = input_text.strip() if input_text.strip() else packet_query
    # D16 ranks against the assembled packet task — not stray hub probe strings.
    rank_query = packet_query or query
    if not force_refresh:
        merge_cached = (pkt.get("memory") or {}).get("merge_ready")
        if merge_cached and MERGE_SSOT_PATH.is_file():
            from pre_llm.packet_memory_merge.store import load_canonical as load_merge_ssot  # noqa: WPS433

            merge_doc = load_merge_ssot()
            check = validate_packet(pkt)
            return {
                "ok": True,
                "schema": SCHEMA,
                "packet": pkt,
                "validation": check,
                "merge": merge_doc or {"merge_ready": True, "cached": True},
                "packet_memory": pkt.get("memory"),
                "cached": True,
                "path": str(MERGE_SSOT_PATH),
                "producer": "D16",
            }

    existing_slots = list((pkt.get("memory") or {}).get("slots") or [])

    d6_slots = collect_d6_slots(
        text=rank_query,
        repo_root=str(root),
        task_id=f"d16-{tid}",
        force_refresh=force_refresh,
    )
    b_slots = collect_b_layer_slots(limit=10)
    l5_slots = collect_l5_history_slots(text=rank_query, repo_root=str(root), limit=6)
    combined = merge_slot_lists(d6_slots, b_slots, l5_slots)
    ranked = filter_slots(combined, rank_query, top_k=24) if rank_query else combined

    max_slots, char_budget = resolve_memory_budget(packet=pkt)
    pruned = prune_slots(ranked, max_slots=max_slots, char_budget=char_budget)
    if existing_slots and len(pruned) < len(existing_slots) and not force_refresh:
        pruned = existing_slots

    sources_merged = sorted({s.get("source_plane") or s.get("producer") or "unknown" for s in pruned})
    pkt["memory"] = {
        "slots": pruned,
        "slot_count": len(pruned),
        "producer": "D6,L5,D16",
        "merge_ready": len(pruned) >= 1,
        "sources_merged": sources_merged,
        "budget": {"max_slots": max_slots, "char_budget": char_budget, "slots_used": len(pruned)},
        "read_only": True,
        "law": "B-layer historical truth · D6 retrieval feed · D16 packet export only",
    }
    _ensure_provenance_d16(pkt)

    check = validate_packet(pkt)
    pkt["readiness"] = {
        **(pkt.get("readiness") or {}),
        "score": check.get("readiness_score"),
        "gate_eligible": check.get("gate_eligible"),
        "missing_for_gate": check.get("missing_for_gate"),
        "memory_merge_ready": bool(pkt["memory"]["merge_ready"]),
    }

    merged_at = _now()
    assembly = load_assembly_meta() or {}
    assembly["memory_merge_at"] = merged_at
    assembly["memory_merge_ready"] = pkt["memory"]["merge_ready"]
    write_canonical(packet=pkt, assembly=assembly, task_id=tid)

    merge_doc = {
        "schema": MERGE_SCHEMA,
        "generated_at": merged_at,
        "task_id": tid,
        "repo_root": str(root),
        "input_text": rank_query[:500],
        "producer": "D16",
        "merge_ready": pkt["memory"]["merge_ready"],
        "slot_count": len(pruned),
        "sources_merged": sources_merged,
        "budget": pkt["memory"]["budget"],
        "read_only": True,
        "pipeline_law": "D14 compress → D15 assemble → D16 writeback only",
    }
    write_merge_ssot(canonical=merge_doc, task_id=tid)

    return {
        "ok": True,
        "schema": SCHEMA,
        "packet": pkt,
        "validation": check,
        "merge": merge_doc,
        "packet_memory": pkt.get("memory"),
        "cached": False,
        "path": str(MERGE_SSOT_PATH),
        "producer": "D16",
    }
