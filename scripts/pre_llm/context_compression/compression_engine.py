"""D14 orchestration — compress ranked evidence under token budget."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.context_compression.budget_policy import resolve_token_limit
from pre_llm.context_compression.compressor import compress_substrates
from pre_llm.context_compression.store import COMPRESSION_SSOT_PATH, SCHEMA, load_canonical, write_canonical
from pre_llm.context_ranking.store import load_canonical as load_d9
from pre_llm.planning_engine.planning_engine import run_planning_engine
from pre_llm.diff_intelligence.diff_engine import run_diff_intelligence
from pre_llm.diff_intelligence.store import load_canonical as load_d13
from pre_llm.intent_engine.store import load_canonical as load_d4
from pre_llm.planning_engine.store import load_canonical as load_d10
from pre_llm.validation_layer.store import load_canonical as load_d12

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_CONTEXT_COMPRESSION_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def _packet_compression_from_canonical(canonical: dict[str, Any]) -> dict[str, Any]:
    return {
        "budget": canonical.get("budget") or {},
        "layers": canonical.get("layers") or [],
        "packed_evidence": canonical.get("packed_evidence") or [],
        "producer": "D14",
        "compression_ready": canonical.get("compression_ready"),
    }


def _packet_compressed_context_from_canonical(canonical: dict[str, Any]) -> dict[str, Any]:
    return {
        "narrative": canonical.get("narrative") or "",
        "sections": [layer.get("layer") for layer in (canonical.get("layers") or []) if layer.get("layer")],
        "producer": "D14",
    }


def run_context_compression(
    *,
    text: str,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
    token_limit: int | None = None,
) -> dict:
    input_text = (text or "").strip()
    if not input_text:
        return {"ok": False, "error": "text required"}

    root = _repo_root(repo_root)
    tid = task_id or f"context-compression:{root.name}"

    if not force_refresh:
        cached = load_canonical()
        if (
            cached
            and cached.get("input_text") == input_text
            and cached.get("repo_root") == str(root)
            and COMPRESSION_SSOT_PATH.is_file()
        ):
            return {
                "ok": True,
                **cached,
                "cached": True,
                "packet_compression": _packet_compression_from_canonical(cached),
                "packet_compressed_context": _packet_compressed_context_from_canonical(cached),
            }

    d13 = load_d13()
    if not d13 or d13.get("input_text") != input_text or not d13.get("diff_ready"):
        d13_live = run_diff_intelligence(
            text=input_text,
            repo_root=str(root),
            task_id=f"d14-{tid}",
            force_refresh=force_refresh,
        )
        if not d13_live.get("ok"):
            return {"ok": False, "error": "D13 diff intelligence required", "d13": d13_live}
        d13 = d13_live

    d9 = load_d9()
    d10 = load_d10()
    d4 = load_d4()
    d12 = load_d12()

    need_plan = (
        force_refresh
        or not d9
        or d9.get("input_text") != input_text
        or not d9.get("ranking_ready")
        or not (d9.get("ranked_evidence") or [])
        or not d10
        or d10.get("input_text") != input_text
        or not d10.get("plan_ready")
    )
    if need_plan:
        d10_live = run_planning_engine(
            text=input_text,
            repo_root=str(root),
            task_id=f"d14-{tid}",
            force_refresh=force_refresh,
        )
        if not d10_live.get("ok"):
            return {"ok": False, "error": "D10 planning engine required", "d10": d10_live}
        d10 = d10_live
        d9 = load_d9()

    if not d9 or not d9.get("ranking_ready") or not (d9.get("ranked_evidence") or []):
        return {"ok": False, "error": "D9 context ranking required"}
    if not d10 or not d10.get("plan_ready"):
        return {"ok": False, "error": "D10 planning engine required"}

    goal_class = d4.get("goal_class") if d4 else d9.get("goal_class") or "other"
    limit = resolve_token_limit(goal_class=goal_class, explicit=token_limit)

    result = compress_substrates(
        input_text=input_text,
        token_limit=limit,
        d4=d4 or {},
        d9=d9,
        d10=d10,
        d12=d12 or {},
        d13=d13,
    )

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": tid,
        "repo_root": str(root),
        "input_text": input_text,
        "producer": "D14",
        "goal_class": goal_class,
        **result,
        "d13_ref": d13.get("generated_at"),
        "d9_ref": d9.get("generated_at"),
        "d10_ref": d10.get("generated_at"),
        "authority": "Compress ranked evidence only — no re-rank, no LLM",
    }
    write_canonical(canonical=canonical, task_id=tid)

    return {
        "ok": True,
        **canonical,
        "cached": False,
        "packet_compression": _packet_compression_from_canonical(canonical),
        "packet_compressed_context": _packet_compressed_context_from_canonical(canonical),
    }
