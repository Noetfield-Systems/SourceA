"""D15 orchestration — compile full LLM context packet."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.context_assembly.constraints_builder import build_constraints
from pre_llm.context_assembly.provenance_builder import build_provenance
from pre_llm.context_assembly.store import ASSEMBLY_SCHEMA, PACKET_SSOT_PATH, load_canonical, write_canonical
from pre_llm.context_compression.compression_engine import run_context_compression
from pre_llm.context_compression.store import load_canonical as load_d14
from pre_llm.context_packet.schema import (
    SCHEMA,
    empty_packet_template,
    hydrate_from_disk_substrate,
    validate_packet,
)
from pre_llm.intent_engine.intent_engine import analyze_intent
from pre_llm.intent_engine.store import load_canonical as load_d4
from pre_llm.tool_router.store import load_canonical as load_d11
from pre_llm.validation_layer.store import load_canonical as load_d12

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_CONTEXT_ASSEMBLY_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def assemble_packet(
    *,
    text: str,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Merge D1–D14 substrates into gate-checked packet (no LLM)."""
    input_text = (text or "").strip()
    if not input_text:
        return {"ok": False, "error": "text required"}

    root = _repo_root(repo_root)
    tid = task_id or f"context-assembly:{root.name}"

    d14 = load_d14()
    if force_refresh or not d14 or d14.get("input_text") != input_text or not d14.get("compression_ready"):
        d14_live = run_context_compression(
            text=input_text,
            repo_root=str(root),
            task_id=f"d15-{tid}",
            force_refresh=force_refresh,
        )
        if not d14_live.get("ok"):
            return {"ok": False, "error": "D14 context compression required", "d14": d14_live}
        d14 = d14_live

    d4 = load_d4()
    if force_refresh or not d4 or d4.get("input_text") != input_text or not d4.get("intent_ready"):
        intent_live = analyze_intent(text=input_text, repo_root=str(root), task_id=f"d15-{tid}")
        if not intent_live.get("ok"):
            return {"ok": False, "error": "D4 intent engine required", "d4": intent_live}

    d12 = load_d12()
    d11 = load_d11()

    pkt = empty_packet_template(task_id=tid, repo_root=str(root))
    pkt["generated_at"] = _now()
    pkt["input_text"] = input_text
    pkt = hydrate_from_disk_substrate(pkt)
    try:
        from pre_llm.user_signals.store import packet_workspace_slice  # noqa: WPS433

        pkt["workspace"] = {**(pkt.get("workspace") or {}), **packet_workspace_slice()}
    except Exception:
        pass

    assembled_at = _now()
    pkt["constraints"] = build_constraints(d11=d11, d12=d12)
    try:
        from pre_llm.context_assembly.task_grounding import build_grounding_block  # noqa: WPS433

        pkt["retrieval"] = {
            **(pkt.get("retrieval") or {}),
            "task_grounding": build_grounding_block(query_text=input_text),
        }
    except Exception:
        pass
    pkt["provenance"] = build_provenance(
        task_id=tid,
        input_text=input_text,
        repo_root=str(root),
        assembled_at=assembled_at,
    )

    check = validate_packet(pkt)

    from pre_llm.packet_memory_merge.merge_engine import run_memory_merge_writeback  # noqa: WPS433

    merge = run_memory_merge_writeback(
        text=input_text,
        repo_root=str(root),
        task_id=tid,
        force_refresh=force_refresh,
        packet=pkt,
    )
    if merge.get("ok") and merge.get("packet"):
        pkt = merge["packet"]
        check = merge.get("validation") or validate_packet(pkt)

    pkt["readiness"] = {
        "score": check.get("readiness_score"),
        "gate_eligible": check.get("gate_eligible"),
        "missing_for_gate": check.get("missing_for_gate"),
        "required_fields_ok": check.get("gate_eligible"),
        "producer_steps": pkt.get("provenance", {}).get("producer_steps"),
        "memory_merge_ready": (pkt.get("memory") or {}).get("merge_ready"),
    }

    assembly = {
        "schema": ASSEMBLY_SCHEMA,
        "assembled_at": assembled_at,
        "assembler": "D15",
        "assembly_ready": bool(check.get("gate_eligible")),
        "readiness_score": check.get("readiness_score"),
        "missing_for_gate": check.get("missing_for_gate"),
        "d14_ref": d14.get("generated_at"),
        "memory_merge_ready": (pkt.get("memory") or {}).get("merge_ready"),
        "d16_ref": (merge.get("merge") or {}).get("generated_at") if merge.get("ok") else None,
    }

    write_canonical(packet=pkt, assembly=assembly, task_id=tid)

    return {
        "ok": True,
        "schema": SCHEMA,
        "packet": pkt,
        "validation": check,
        "assembly": assembly,
        "path": str(PACKET_SSOT_PATH),
    }


def run_context_assembly(
    *,
    text: str,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict[str, Any]:
    input_text = (text or "").strip()
    if not input_text:
        return {"ok": False, "error": "text required"}

    root = _repo_root(repo_root)
    tid = task_id or f"context-assembly:{root.name}"

    if not force_refresh:
        cached = load_canonical()
        meta_path = PACKET_SSOT_PATH
        if (
            cached
            and cached.get("input_text") == input_text
            and cached.get("repo_root") == str(root)
            and meta_path.is_file()
            and (cached.get("memory") or {}).get("merge_ready")
        ):
            check = validate_packet(cached)
            return {
                "ok": True,
                "schema": SCHEMA,
                "packet": cached,
                "validation": check,
                "assembly": {"assembly_ready": check.get("gate_eligible"), "cached": True},
                "cached": True,
                "path": str(meta_path),
                "producer": "D15",
            }

    built = assemble_packet(
        text=input_text,
        repo_root=str(root),
        task_id=tid,
        force_refresh=force_refresh,
    )
    if not built.get("ok"):
        return built
    built["cached"] = False
    built["producer"] = "D15"
    return built
