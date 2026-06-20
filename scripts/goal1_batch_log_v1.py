#!/usr/bin/env python3
"""Goal 1 batch log — AGENT START/DONE receipts + 10/10 broker gate.

TRACE: AUTO-TRACE-WORKER-BATCH-LOG-v1.0 · agent Auto
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

import os

BATCH_LOG = Path(
    os.environ.get("SINA_GOAL1_BATCH_LOG")
    or str(Path.home() / ".sina" / "goal1-worker-batch-latest.log")
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def agent_done_lines(text: str) -> list[str]:
    return [
        ln
        for ln in (text or "").splitlines()
        if "AGENT DONE" in ln
        and "post-pack-hygiene" not in ln
        and "sa-TEST-GATE" not in ln
        and "sa-TEST" not in ln
        and "chars=42" not in ln  # validator harness pollution — not real worker turns
    ]


def log_agent_start(
    *,
    sa_id: str,
    queue_role: str = "",
    queue_pos: int | str = "",
    queue_total: int | str = "",
) -> None:
    BATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    q = f" queue={queue_pos}/{queue_total}" if queue_pos and queue_total else ""
    role = queue_role or "turn"
    with BATCH_LOG.open("a", encoding="utf-8") as fh:
        fh.write(f"[{_now()}] AGENT START {sa_id} {role}{q}\n")


def log_agent_done(
    *,
    exit_code: int,
    broker_ok: bool,
    advance_ok: bool | None = None,
    report_ok: bool | None = None,
    chars: int = 0,
) -> None:
    broker = "yes" if broker_ok else "no"
    advance = (
        "yes"
        if advance_ok is True
        else "no"
        if advance_ok is False
        else "skip"
    )
    report = (
        "yes"
        if report_ok is True
        else "no"
        if report_ok is False
        else "skip"
    )
    BATCH_LOG.parent.mkdir(parents=True, exist_ok=True)
    with BATCH_LOG.open("a", encoding="utf-8") as fh:
        fh.write(
            f"[{_now()}] AGENT DONE exit={exit_code} broker={broker} "
            f"advance={advance} report={report} chars={chars}\n"
        )


def broker_yes_gate(*, need: int = 10) -> dict:
    """Last N non-hygiene AGENT DONE lines must be exit=0 broker=yes."""
    if not BATCH_LOG.is_file():
        return {"ok": False, "count": 0, "need": need, "error": "batch_log_missing"}
    lines = agent_done_lines(BATCH_LOG.read_text(encoding="utf-8", errors="replace"))
    tail = lines[-need:] if len(lines) >= need else lines
    good = [
        ln
        for ln in tail
        if "exit=0" in ln and "broker=yes" in ln
    ]
    ok = len(lines) >= need and len(good) == len(tail) == need
    return {
        "ok": ok,
        "count": len(good),
        "need": need,
        "total_done_lines": len(lines),
        "last": tail[-1] if tail else None,
        "blocker": None if ok else f"need {need} trailing AGENT DONE exit=0 broker=yes; have {len(good)}/{need}",
    }


def consecutive_broker_no_streak() -> int:
    if not BATCH_LOG.is_file():
        return 0
    lines = agent_done_lines(BATCH_LOG.read_text(encoding="utf-8", errors="replace"))
    streak = 0
    for ln in reversed(lines):
        if "broker=no" in ln:
            streak += 1
        elif "broker=yes" in ln:
            break
        else:
            break
    return streak
