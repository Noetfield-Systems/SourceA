"""Hub API payloads — prompt_router + execution_kernel_v0."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _run_json(script: str, argv: list[str]) -> dict:
    cmd = [sys.executable, str(SCRIPTS / script), *argv]
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), check=False, timeout=180)
    if proc.returncode != 0:
        return {"ok": False, "error": (proc.stderr or proc.stdout or "failed").strip()[:500]}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": True, "raw": proc.stdout}


def prompt_router_v1_payload(
    *,
    keyword: str = "implement",
    lane: str = "sourcea",
    dry_run: bool = True,
    invoke_loop: bool = False,
) -> dict:
    argv = ["--keyword", keyword, "--lane", lane, "--json"]
    if dry_run:
        argv.append("--dry-run")
    if invoke_loop:
        argv.append("--invoke-loop")
    out = _run_json("prompt_router.py", argv)
    return {"schema": "prompt-router-v1", **out}


def execution_kernel_v1_payload(
    *,
    lane: str = "sourcea",
    keyword: str = "PLAN WITH NO ASF",
    invoke_loop: bool = False,
    use_spine_router: bool = False,
    execute: bool = False,
    task_id: str = "",
) -> dict:
    argv = [
        "--tick",
        "--lane",
        lane,
        "--keyword",
        keyword,
    ]
    if task_id:
        argv.extend(["--task-id", task_id])
    if execute or invoke_loop:
        argv.append("--execute")
        if invoke_loop:
            argv.append("--invoke-loop")
    else:
        argv.append("--dry-run")
    if use_spine_router:
        argv.append("--use-spine-router")
    out = _run_json("execution_kernel_v0.py", argv)
    return {"schema": "execution-kernel-v1", **out}


def execution_state_v1_payload(*, lane: str = "sourcea") -> dict:
    out = _run_json("execution_state_hub.py", ["status", "--lane", lane, "--json"])
    return {"schema": "execution-state-v1", **out}


def execution_scheduler_v1_payload(*, lane: str = "sourcea", force: bool = False, persist: bool = False) -> dict:
    argv = ["--next", "--lane", lane]
    if force:
        argv.append("--force")
    if persist:
        argv.append("--persist")
    out = _run_json("execution_scheduler.py", argv)
    return {"schema": "execution-scheduler-v1", **out}


def execution_state_v1_post(body: dict) -> dict:
    """POST /api/execution-state-v1 — mark_verifying | mark_done | mark_failed."""
    action = (body.get("action") or "").strip().lower()
    lane = (body.get("lane") or "sourcea").strip().lower()
    task_id = (body.get("task_id") or body.get("id") or "").strip()
    if not action:
        return {"ok": False, "error": "action required (mark_verifying|mark_done|mark_failed)"}
    if not task_id:
        return {"ok": False, "error": "task_id required"}

    if action == "mark_verifying":
        out = _run_json("execution_state_hub.py", ["mark-verifying", "--lane", lane, "--id", task_id])
    elif action == "mark_done":
        argv = ["mark-done", "--lane", lane, "--id", task_id]
        if body.get("verify_failed"):
            argv.append("--verify-failed")
        summary = (body.get("summary") or "").strip()
        if summary:
            argv.extend(["--summary", summary])
        out = _run_json("execution_state_hub.py", argv)
    elif action == "mark_failed":
        reason = (body.get("reason") or "").strip()
        argv = ["mark-failed", "--lane", lane, "--id", task_id]
        if reason:
            argv.extend(["--reason", reason])
        out = _run_json("execution_state_hub.py", argv)
    else:
        return {"ok": False, "error": f"unknown action: {action}"}
    return {"schema": "execution-state-v1", "action": action, **out}


def execution_state_machine_v1_payload() -> dict:
    import sys

    sys.path.insert(0, str(SCRIPTS))
    from execution_state_machine import contract_export  # noqa: WPS433

    return contract_export()
