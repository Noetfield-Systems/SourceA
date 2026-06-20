"""Provenance block for D15 assembled packet."""
from __future__ import annotations

from pathlib import Path
from typing import Any

from pre_llm.context_packet.schema import LAW_DOC, SHIPPED_PRODUCERS


def _artifact_map() -> dict[str, str]:
    from pre_llm.code_intelligence.store import CODE_INTEL_SSOT_PATH  # noqa: WPS433
    from pre_llm.context_compression.store import COMPRESSION_SSOT_PATH  # noqa: WPS433
    from pre_llm.context_ranking.store import RANKING_SSOT_PATH  # noqa: WPS433
    from pre_llm.dependency_graph.store import DEP_GRAPH_SSOT_PATH  # noqa: WPS433
    from pre_llm.diff_intelligence.store import DIFF_SSOT_PATH  # noqa: WPS433
    from pre_llm.graph_fusion.store import FUSION_SSOT_PATH  # noqa: WPS433
    from pre_llm.intent_engine.store import INTENT_SSOT_PATH  # noqa: WPS433
    from pre_llm.memory_git_bridge.store import BRIDGE_SSOT_PATH  # noqa: WPS433
    from pre_llm.planning_engine.store import PLANNING_SSOT_PATH  # noqa: WPS433
    from pre_llm.query_expansion.store import EXPANSION_SSOT_PATH  # noqa: WPS433
    from pre_llm.graph_reasoning.store import REASONING_SSOT_PATH  # noqa: WPS433
    from pre_llm.tool_router.store import ROUTER_SSOT_PATH  # noqa: WPS433
    from pre_llm.validation_layer.store import VALIDATION_SSOT_PATH  # noqa: WPS433
    from pre_llm.vector_retrieval.store import VECTOR_SSOT_PATH  # noqa: WPS433
    from pre_llm.context_packet.schema import PACKET_SSOT_PATH  # noqa: WPS433
    from pre_llm.packet_memory_merge.store import MERGE_SSOT_PATH  # noqa: WPS433
    from runtime.context_fabric.fabric_store import FABRIC_SSOT_PATH  # noqa: WPS433

    return {
        "D1": str(CODE_INTEL_SSOT_PATH),
        "D2": str(FUSION_SSOT_PATH),
        "D3": str(DEP_GRAPH_SSOT_PATH),
        "D4": str(INTENT_SSOT_PATH),
        "D5": str(VECTOR_SSOT_PATH),
        "D6": str(BRIDGE_SSOT_PATH),
        "D7": str(EXPANSION_SSOT_PATH),
        "D8": str(REASONING_SSOT_PATH),
        "D9": str(RANKING_SSOT_PATH),
        "D10": str(PLANNING_SSOT_PATH),
        "D11": str(ROUTER_SSOT_PATH),
        "D12": str(VALIDATION_SSOT_PATH),
        "D13": str(DIFF_SSOT_PATH),
        "D14": str(COMPRESSION_SSOT_PATH),
        "D15": str(PACKET_SSOT_PATH),
        "D16": str(MERGE_SSOT_PATH),
        "C5": str(FABRIC_SSOT_PATH),
    }


def build_provenance(
    *,
    task_id: str,
    input_text: str,
    repo_root: str,
    assembled_at: str,
) -> dict[str, Any]:
    steps = sorted(SHIPPED_PRODUCERS | {"D15"})
    artifacts = _artifact_map()
    present = {k: v for k, v in artifacts.items() if k in steps and Path(v).is_file()}
    return {
        "producer_steps": steps,
        "artifacts": present,
        "assembler": "D15",
        "task_id": task_id,
        "input_text": input_text[:500],
        "repo_root": repo_root,
        "assembled_at": assembled_at,
        "law_doc": LAW_DOC,
    }
