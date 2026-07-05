#!/usr/bin/env python3
"""Railway scheduled loop wrappers — repo-health, security, determinism."""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_py(script: str, *args: str) -> tuple[int, dict[str, Any]]:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts" / script), *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    out = (proc.stdout or "").strip()
    try:
        row = json.loads(out) if out else {}
    except json.JSONDecodeError:
        row = {"ok": False, "error": "json_parse_fail", "raw": out[:400]}
    if proc.returncode != 0 and row.get("ok") is not False:
        row["ok"] = False
        row["exit_code"] = proc.returncode
    return proc.returncode, row


def run_cloud_repo_health_daily(body: dict[str, Any]) -> dict[str, Any]:
    from gha_repo_health_sweep_v1 import run_sweep  # noqa: WPS433

    insert = body.get("insert", True) is not False
    row = run_sweep(insert=insert)
    return {**row, "trigger_source": body.get("trigger_source", "cloudflare_cron")}


def run_cloud_security_sweep_weekly(body: dict[str, Any]) -> dict[str, Any]:
    from gha_security_sweep_v1 import run_sweep  # noqa: WPS433

    insert = body.get("insert", True) is not False
    row = run_sweep(insert=insert)
    return {**row, "trigger_source": body.get("trigger_source", "cloudflare_cron")}


def run_cloud_determinism_gate(body: dict[str, Any]) -> dict[str, Any]:
    steps: list[dict[str, Any]] = []
    ok = True

    for label, script, args in (
        ("locked_definitions_anatomy", "validate_locked_definitions_anatomy_v1.py", ("--json",)),
        ("trigger_registry_sweep", "sandbox_health_sweep_v1.py", ("--json",)),
        ("autorun_determinism", "verify_autorun_determinism_v1.py", ("--json",)),
    ):
        code, row = _run_py(script, *args)
        step_ok = code == 0 and bool(row.get("ok", code == 0))
        steps.append({"step": label, "ok": step_ok, "exit": code, "report_line": row.get("report_line")})
        ok = ok and step_ok

    return {
        "schema": "determinism-gate-cloud-tick-v1",
        "ok": ok,
        "at": _now(),
        "steps": steps,
        "report_line": f"determinism_gate_cloud · {'PASS' if ok else 'FAIL'}",
        "trigger_source": body.get("trigger_source", "cloudflare_cron"),
    }
