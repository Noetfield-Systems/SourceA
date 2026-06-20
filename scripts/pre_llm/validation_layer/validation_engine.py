"""D12 orchestration — full pre-LLM validation."""
from __future__ import annotations

import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pre_llm.dependency_graph.store import load_canonical as load_d3
from pre_llm.context_ranking.store import load_canonical as load_d9
from pre_llm.planning_engine.store import load_canonical as load_d10
from pre_llm.tool_router.router_engine import run_tool_router
from pre_llm.tool_router.store import load_canonical as load_d11
from pre_llm.validation_layer.check_runner import run_all_checks
from pre_llm.validation_layer.store import VALIDATION_SSOT_PATH, SCHEMA, load_canonical, write_canonical

SOURCE_A = Path(__file__).resolve().parents[3]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _repo_root(explicit: str | None = None) -> Path:
    raw = explicit or os.environ.get("SINA_VALIDATION_LAYER_ROOT") or str(SOURCE_A)
    return Path(raw).expanduser().resolve()


def _packet_validation_from_canonical(canonical: dict[str, Any]) -> dict[str, Any]:
    return {
        "checks": [
            {
                "id": c.get("id"),
                "category": c.get("category"),
                "status": c.get("status"),
                "severity": c.get("severity"),
                "detail": c.get("detail"),
            }
            for c in (canonical.get("checks") or [])
        ],
        "producer": "D12",
        "validation_ready": canonical.get("validation_ready"),
        "dry_run": canonical.get("dry_run"),
    }


def run_validation_layer(
    *,
    text: str,
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    input_text = (text or "").strip()
    if not input_text:
        return {"ok": False, "error": "text required"}

    root = _repo_root(repo_root)
    tid = task_id or f"validation-layer:{root.name}"

    if not force_refresh:
        cached = load_canonical()
        if (
            cached
            and cached.get("input_text") == input_text
            and cached.get("repo_root") == str(root)
            and VALIDATION_SSOT_PATH.is_file()
        ):
            return {
                "ok": True,
                **cached,
                "cached": True,
                "packet_validation": _packet_validation_from_canonical(cached),
            }

    d11 = load_d11()
    if not d11 or d11.get("input_text") != input_text or not d11.get("router_ready"):
        d11_live = run_tool_router(text=input_text, repo_root=str(root), task_id=f"d12-{tid}", force_refresh=force_refresh)
        if not d11_live.get("ok"):
            return {"ok": False, "error": "D11 tool router required", "d11": d11_live}
        d11 = d11_live

    d10 = load_d10() or {}
    d9 = load_d9() or {}
    d3 = load_d3() or {}

    if not d10.get("plan_ready") or not d11.get("router_ready"):
        return {"ok": False, "error": "D10/D11 substrates not ready"}

    check_result = run_all_checks(
        task_id=tid,
        repo_root=root,
        d3=d3,
        d9=d9,
        d10=d10,
        d11=d11,
    )

    canonical = {
        "schema": SCHEMA,
        "generated_at": _now(),
        "task_id": tid,
        "repo_root": str(root),
        "input_text": input_text,
        "producer": "D12",
        **check_result,
        "d11_ref": d11.get("generated_at"),
        "authority": "Pre-LLM dry-run + safety — beyond C2 runtime verify",
    }
    write_canonical(canonical=canonical, task_id=tid)

    return {
        "ok": True,
        **canonical,
        "cached": False,
        "packet_validation": _packet_validation_from_canonical(canonical),
    }
