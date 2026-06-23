#!/usr/bin/env python3
"""Single external cycle gate — max 1 cloud-drain request per 10 minutes.

Law: only one scheduler outside this system (e.g. CF cron */10).
Second request inside the window → latched HALT until manual gate reset.
No retries · no internal loops · no recursive HTTP back to self.
"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"

GATED_PATHS = frozenset(
    {
        "/api/cloud-drain/proceed/v1",
        "/api/cloud-drain/auto-tick/v1",
    }
)

SCHEMA = "cloud-drain-single-cycle-gate-v1"
CYCLE_SECONDS = int(os.environ.get("CLOUD_DRAIN_SINGLE_CYCLE_SECONDS", "600"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _parse_at(raw: str) -> datetime | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _gate_path() -> Path:
    if str(os.environ.get("FBE_MODE", "")).lower() == "headless" or os.environ.get("FBE_HOME", "").strip() == "/app":
        return Path("/app/receipts/cloud/cloud-drain-single-cycle-gate-v1.json")
    return SINA / "cloud-drain-single-cycle-gate-v1.json"


def _read_gate() -> dict[str, Any]:
    path = _gate_path()
    if not path.is_file():
        return {"schema": SCHEMA, "halted": False}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"schema": SCHEMA, "halted": False}


def _write_gate(row: dict[str, Any]) -> None:
    path = _gate_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def is_gated_path(path: str) -> bool:
    return path in GATED_PATHS


def halt_response(
    *,
    path: str,
    trigger_source: str,
    reason: str,
    last_at: str = "",
    seconds_since: float | None = None,
) -> dict[str, Any]:
    return {
        "ok": False,
        "schema": SCHEMA,
        "at": _now(),
        "decision": "halt_single_cycle",
        "halted": True,
        "reason": reason,
        "path": path,
        "trigger_source": trigger_source,
        "cycle_seconds": CYCLE_SECONDS,
        "last_request_at": last_at or None,
        "seconds_since_last": round(seconds_since, 1) if seconds_since is not None else None,
        "for_founder": {
            "show_this": (
                f"HALT — more than 1 cloud-drain request in {CYCLE_SECONDS // 60}m · "
                f"external scheduler only · reset gate logged to recover"
            ),
        },
        "gate_path": str(_gate_path()),
    }


def claim_or_halt(
    *,
    path: str,
    trigger_source: str = "unknown",
    after_pass: bool = False,
) -> dict[str, Any] | None:
    """Claim this cycle or return a halt payload. None means proceed."""
    if not is_gated_path(path):
        return None

    state = _read_gate()
    if after_pass:
        _write_gate(
            {
                **state,
                "schema": SCHEMA,
                "halted": False,
                "halt_reason": None,
                "halt_at": None,
                "last_completed_at": _now(),
                "last_completed_path": path,
                "last_completed_trigger_source": trigger_source,
                "cycle_seconds": CYCLE_SECONDS,
            }
        )
        return None

    if state.get("halted"):
        return halt_response(
            path=path,
            trigger_source=trigger_source,
            reason=str(state.get("halt_reason") or "latched_halt"),
            last_at=str(state.get("last_request_at") or ""),
        )

    last_at = str(state.get("last_request_at") or "")
    last_dt = _parse_at(last_at)
    now_dt = datetime.now(timezone.utc)
    if last_dt is not None:
        elapsed = (now_dt - last_dt).total_seconds()
        if elapsed < CYCLE_SECONDS:
            reason = "second_request_within_cycle_window"
            halt = halt_response(
                path=path,
                trigger_source=trigger_source,
                reason=reason,
                last_at=last_at,
                seconds_since=elapsed,
            )
            _write_gate(
                {
                    **state,
                    "schema": SCHEMA,
                    "halted": True,
                    "halt_reason": reason,
                    "halt_at": _now(),
                    "halt_path": path,
                    "halt_trigger_source": trigger_source,
                    "last_request_at": last_at,
                    "cycle_seconds": CYCLE_SECONDS,
                }
            )
            return halt

    _write_gate(
        {
            **state,
            "schema": SCHEMA,
            "halted": False,
            "halt_reason": None,
            "last_request_at": _now(),
            "last_path": path,
            "last_trigger_source": trigger_source,
            "cycle_seconds": CYCLE_SECONDS,
        }
    )
    return None


def gate_status() -> dict[str, Any]:
    state = _read_gate()
    last_dt = _parse_at(str(state.get("last_request_at") or ""))
    elapsed = None
    if last_dt is not None:
        elapsed = (datetime.now(timezone.utc) - last_dt).total_seconds()
    return {
        "schema": SCHEMA,
        "at": _now(),
        "halted": bool(state.get("halted")),
        "cycle_seconds": CYCLE_SECONDS,
        "last_request_at": state.get("last_request_at"),
        "last_path": state.get("last_path"),
        "seconds_since_last": round(elapsed, 1) if elapsed is not None else None,
        "gate_path": str(_gate_path()),
    }
