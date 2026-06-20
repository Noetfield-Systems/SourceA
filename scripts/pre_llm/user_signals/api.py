"""L0/L1 hub API handlers."""
from __future__ import annotations

from typing import Any

from pre_llm.user_signals.store import hub_payload, record_hub_touch


def user_workspace_signals_v1_payload(body: dict | None = None) -> dict[str, Any]:
    body = body or {}
    if body.get("action") == "touch":
        record_hub_touch(
            hub_tab=str(body.get("hub_tab") or ""),
            active_repo=str(body.get("active_repo") or ""),
            active_thread=str(body.get("active_thread") or ""),
            loop_round=body.get("loop_round"),
            source=str(body.get("source") or "hub"),
        )
    if body.get("action") == "workspace":
        from pre_llm.user_signals.store import record_workspace_files  # noqa: WPS433

        files = body.get("open_files") or body.get("files") or []
        if isinstance(files, list):
            record_workspace_files([str(f) for f in files[:24]], source=str(body.get("source") or "hub"))
    return hub_payload()
