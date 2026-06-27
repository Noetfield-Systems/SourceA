#!/usr/bin/env python3
"""Forge Terminal telemetry + failure library (P2/P3 — append-only JSONL, no new kernel)."""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
TELEMETRY = SINA / "forge-terminal-telemetry-v1.jsonl"
FAILURES = SINA / "forge-terminal-failures-v1.jsonl"

PORTFOLIO_PATTERNS: tuple[tuple[re.Pattern[str], str], ...] = (
    (re.compile(r"\bvirelux\b", re.I), "VIRELUX"),
    (re.compile(r"\bnoetfield\b", re.I), "Noetfield"),
    (re.compile(r"\bwitness\s*bc\b|\bwitnessbc\b", re.I), "WitnessBC"),
    (re.compile(r"\b777\b|\b777\s+foundation\b", re.I), "777 Foundation"),
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _append(path: Path, row: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def detect_portfolio(text: str) -> str | None:
    blob = text or ""
    for pat, label in PORTFOLIO_PATTERNS:
        if pat.search(blob):
            return label
    return None


def log_event(
    event: str,
    *,
    run_id: str = "",
    success: bool | None = None,
    elapsed_ms: float | None = None,
    model: str | None = None,
    provider: str | None = None,
    decision: str | None = None,
    cost_usd: float | None = None,
    portfolio: str | None = None,
    plane: str | None = None,
    error: str | None = None,
    extra: dict[str, Any] | None = None,
) -> None:
    row: dict[str, Any] = {
        "schema": "forge-terminal-telemetry-v1",
        "at": _now(),
        "event": event,
        "run_id": run_id or None,
        "success": success,
    }
    if elapsed_ms is not None:
        row["elapsed_ms"] = round(elapsed_ms, 1)
    if model:
        row["model"] = model
    if provider:
        row["provider"] = provider
    if decision:
        row["decision"] = decision
    if cost_usd is not None:
        row["cost_usd"] = cost_usd
    if portfolio:
        row["portfolio"] = portfolio
    if plane:
        row["plane"] = plane
    if error:
        row["error"] = error[:500]
    if extra:
        row["extra"] = extra
    _append(TELEMETRY, row)


def log_failure(
    *,
    run_id: str,
    stage: str,
    founder_input: str = "",
    decision: str = "",
    plane: str = "",
    error: str = "",
    cloud_raw: dict[str, Any] | None = None,
) -> None:
    row = {
        "schema": "forge-terminal-failure-v1",
        "at": _now(),
        "run_id": run_id,
        "stage": stage,
        "portfolio": detect_portfolio(founder_input),
        "decision": decision or None,
        "plane": plane or None,
        "error": (error or "unknown")[:500],
        "founder_preview": (founder_input or "")[:200],
        "cloud_raw": cloud_raw or None,
    }
    _append(FAILURES, row)
    log_event(
        "failure_recorded",
        run_id=run_id,
        success=False,
        decision=decision,
        plane=plane,
        error=error,
        portfolio=row.get("portfolio"),
        extra={"stage": stage},
    )


def summary(*, tail: int = 20) -> dict[str, Any]:
    rows: list[dict] = []
    if TELEMETRY.is_file():
        for line in TELEMETRY.read_text(encoding="utf-8", errors="replace").splitlines()[-tail:]:
            line = line.strip()
            if not line:
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    failures = 0
    if FAILURES.is_file():
        failures = sum(1 for ln in FAILURES.read_text(encoding="utf-8").splitlines() if ln.strip())
    runs = [r for r in rows if r.get("event") == "run"]
    execs = [r for r in rows if r.get("event") in ("execute_cloud", "execute_cursor")]
    return {
        "telemetry_path": str(TELEMETRY),
        "failures_path": str(FAILURES),
        "recent_events": len(rows),
        "failure_count": failures,
        "recent_runs": len(runs),
        "recent_executions": len(execs),
        "last": rows[-1] if rows else None,
    }
