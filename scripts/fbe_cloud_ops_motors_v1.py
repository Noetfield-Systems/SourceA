#!/usr/bin/env python3
"""Cloud wrappers — Gmail sweep, SF triage, Kaizen nightly, ops heartbeat."""
from __future__ import annotations

from typing import Any


def run_cloud_gmail_sweep(body: dict[str, Any]) -> dict[str, Any]:
    from gmail_inbox_sweep_v1 import run_sweep  # noqa: WPS433

    return run_sweep(max_per_mailbox=int(body.get("max_per_mailbox") or 25))


def run_cloud_signal_factory_triage(body: dict[str, Any]) -> dict[str, Any]:
    from signal_factory_triage_v1 import run_triage  # noqa: WPS433

    return run_triage(
        max_batch=int(body.get("max_batch") or 10),
        notify=body.get("notify", True) is not False,
    )


def run_cloud_kaizen_nightly(body: dict[str, Any]) -> dict[str, Any]:
    from kaizen_nightly_tick_v1 import run_nightly  # noqa: WPS433

    return run_nightly()


def run_cloud_ops_heartbeat(body: dict[str, Any]) -> dict[str, Any]:
    from daily_ops_heartbeat_v1 import run_heartbeat  # noqa: WPS433

    return run_heartbeat(notify=body.get("notify", True) is not False)
