#!/usr/bin/env python3
"""@evidence_capture — decorator for BLOCK → AEG forensic bundle.

Wrap any function that returns a critic_boot-shaped dict (verdict, ok, checks).
On BLOCK, runs capture → compile → publish via aeg_capture_v1.emit_block_evidence.

Example:
    @evidence_capture(terminal_command="python3 scripts/critic_boot_v1.py --json")
    def run_agent_session():
        return run_boot(...)
"""
from __future__ import annotations

import functools
import os
from collections.abc import Callable
from typing import Any, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def aeg_on_block_default() -> bool:
    if os.environ.get("AEG_CAPTURE") == "1":
        return False
    return os.environ.get("AEG_ON_BLOCK", "1").strip().lower() not in ("0", "false", "no")


def attach_block_evidence(
    row: dict[str, Any],
    *,
    terminal_command: str | None = None,
    skip_ui: bool = False,
    heal_boot: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Attach AEG manifest to a BLOCK row (idempotent if aeg already present)."""
    if row.get("aeg", {}).get("evidence_id"):
        return row
    if row.get("verdict") != "BLOCK" and row.get("ok"):
        return row
    try:
        from aeg_capture_v1 import emit_block_evidence  # noqa: WPS433

        row["aeg"] = emit_block_evidence(
            row,
            heal_boot=heal_boot,
            skip_ui=skip_ui,
            terminal_command=terminal_command,
        )
    except Exception as exc:
        row["aeg"] = {"ok": False, "error": str(exc)}
    return row


def evidence_capture(
    *,
    terminal_command: str | None = None,
    skip_ui: bool = False,
    on_block_only: bool = True,
    enabled: bool | None = None,
) -> Callable[[F], F]:
    """Decorator: after fn returns, emit AEG bundle when verdict is BLOCK."""

    def decorator(fn: F) -> F:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = fn(*args, **kwargs)
            if not isinstance(result, dict):
                return result
            use = enabled if enabled is not None else aeg_on_block_default()
            if not use:
                return result
            if on_block_only and result.get("verdict") != "BLOCK" and result.get("ok"):
                return result
            return attach_block_evidence(
                result,
                terminal_command=terminal_command,
                skip_ui=skip_ui,
            )

        return wrapper  # type: ignore[return-value]

    return decorator
