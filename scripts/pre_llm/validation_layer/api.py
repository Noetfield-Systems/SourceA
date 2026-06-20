"""Hub API — GET /api/validation-layer-v1"""
from __future__ import annotations

from pre_llm.validation_layer.validation_engine import run_validation_layer
from pre_llm.validation_layer.store import VALIDATION_SSOT_PATH, SCHEMA


def validation_layer_v1_payload(
    *,
    text: str = "",
    repo_root: str | None = None,
    task_id: str = "",
    force_refresh: bool = False,
) -> dict:
    result = run_validation_layer(
        text=text,
        repo_root=repo_root,
        task_id=task_id,
        force_refresh=force_refresh,
    )
    if not result.get("ok"):
        return result
    return {
        **result,
        "path": str(VALIDATION_SSOT_PATH),
        "schema": SCHEMA,
        "api": "/api/validation-layer-v1",
        "producer": "D12",
    }
