#!/usr/bin/env python3
"""Signal Factory cloud tick — Railway FBE body (synthetic queue only)."""
from __future__ import annotations

from typing import Any


def run_cloud_signal_factory_tick(body: dict[str, Any]) -> dict[str, Any]:
    from signal_factory_tick_v1 import run_tick  # noqa: WPS433

    max_batch = int(body.get("max_batch") or 5)
    trigger = str(body.get("trigger_source") or "cloud_http")
    return run_tick(write=True, max_batch=max_batch, trigger_source=trigger, cloud_primary=True)
