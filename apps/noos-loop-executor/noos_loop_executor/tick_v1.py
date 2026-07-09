"""Bounded one-tick NOOS loop runner — no daemon, max wall clock."""
from __future__ import annotations

import json
import os
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(os.environ.get("NOOS_EXECUTOR_ROOT", "/app"))
MAX_WALL_SECONDS = int(os.environ.get("NOOS_TICK_MAX_SECONDS", "120"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_bounded_tick(body: dict[str, Any] | None = None) -> dict[str, Any]:
    body = body or {}
    receipt_id = f"noos-tick-{uuid.uuid4().hex[:12]}"
    started = _now()
    trigger = str(body.get("trigger_source") or "fly_http_loop")
    steps: list[dict[str, Any]] = []

    sweep_script = ROOT / "scripts" / "sandbox_health_sweep_v1.py"
    if not sweep_script.is_file():
        return {
            "ok": False,
            "schema": "noos-loop-tick-receipt-v1",
            "receipt_id": receipt_id,
            "started_at": started,
            "finished_at": _now(),
            "error": "missing_sandbox_health_sweep",
            "steps": steps,
        }

    try:
        proc = subprocess.run(
            [sys.executable, str(sweep_script), "--json"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=MAX_WALL_SECONDS,
        )
        sweep_row: dict[str, Any] = {}
        if proc.stdout.strip():
            try:
                sweep_row = json.loads(proc.stdout)
            except json.JSONDecodeError:
                sweep_row = {"parse_error": True, "stdout_head": proc.stdout[:400]}
        steps.append(
            {
                "step": "trigger_registry_sweep",
                "ok": proc.returncode == 0 and bool(sweep_row.get("ok")),
                "exit_code": proc.returncode,
                "stderr_head": (proc.stderr or "")[:300] or None,
                "sweep": sweep_row,
            }
        )
    except subprocess.TimeoutExpired:
        return {
            "ok": False,
            "schema": "noos-loop-tick-receipt-v1",
            "receipt_id": receipt_id,
            "started_at": started,
            "finished_at": _now(),
            "error": "tick_timeout",
            "max_wall_seconds": MAX_WALL_SECONDS,
            "steps": steps,
        }

    ok = all(s.get("ok") for s in steps)
    return {
        "ok": ok,
        "schema": "noos-loop-tick-receipt-v1",
        "receipt_id": receipt_id,
        "started_at": started,
        "finished_at": _now(),
        "trigger_source": trigger,
        "execution_mode": "BOUNDED_ONE_TICK",
        "bounded": True,
        "max_wall_seconds": MAX_WALL_SECONDS,
        "steps": steps,
        "decision": "PASS" if ok else "FAIL_WITH_RECEIPT",
    }
