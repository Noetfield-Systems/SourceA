#!/usr/bin/env python3
"""Forge Prompt OS Compiler v3 — autonomous runtime (compile → execute → learn).

Direct execution without Cursor: prompt → task → swarm/kernel → deployment hint.
Receipt: ~/.sina/forge-prompt-os-runtime-latest-v3.json
Queue: ~/.sina/forge-prompt-os-runtime-queue-v3.json
Law: brain-os/law/enforcement/SOURCEA_FORGE_PROMPT_OS_COMPILER_V3_LOCKED_v1.md
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from forge_prompt_os_compiler_v2 import (  # noqa: WPS433
    compile_and_dispatch_hint as compile_and_dispatch_hint_v2,
    compile_prompt as compile_prompt_v2,
    record_execution_outcome,
    seed_learning_demo,
    _now,
)

SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-prompt-os-runtime-latest-v3.json"
RUNTIME_QUEUE = SINA / "forge-prompt-os-runtime-queue-v3.json"
SCHEMA = "forge-prompt-os-runtime-v3"
COMPILER_VERSION = "3.0.0"
MAX_QUEUE = 100


def route_execution(compiled: dict[str, Any]) -> dict[str, Any]:
    """Map compiled stack/intent → Forge executor."""
    stack = str(compiled.get("stackLevel") or "L3")
    intent = str(compiled.get("intent") or "general_build")
    mode = str(compiled.get("executionMode") or "single")

    if stack == "L7" or intent == "deployment":
        return {
            "executor": "cloud_swarm_deploy",
            "action": "agent_swarm_run",
            "swarm": True,
            "cloud": True,
            "deployment": True,
        }
    if mode == "swarm" or stack in ("L5", "L6"):
        return {
            "executor": "swarm",
            "action": "agent_swarm_run",
            "swarm": True,
            "cloud": False,
            "deployment": False,
        }
    if stack in ("L3", "L4"):
        return {
            "executor": "agent_dev",
            "action": "agent_dev_loop",
            "swarm": False,
            "cloud": False,
            "patch_only": stack == "L3",
            "deployment": False,
        }
    return {
        "executor": "agent_dev",
        "action": "agent_dev_loop",
        "swarm": False,
        "cloud": False,
        "patch_only": False,
        "deployment": False,
    }


def compile_prompt(
    *,
    raw: str,
    system_state: dict[str, Any] | None = None,
    workspace_path: str = "",
    adaptive: bool = True,
) -> dict[str, Any]:
    """v2 adaptive compile + v3 runtime envelope."""
    inner = compile_prompt_v2(
        raw=raw,
        system_state=system_state,
        workspace_path=workspace_path,
        adaptive=adaptive,
    )
    if not inner.get("ok"):
        return {**inner, "schema": SCHEMA, "version": COMPILER_VERSION}
    route = route_execution(inner)
    return {
        **inner,
        "schema": SCHEMA,
        "version": COMPILER_VERSION,
        "parent_schema": inner.get("schema"),
        "runtime_capable": True,
        "suggested_route": route,
    }


def compile_and_dispatch_hint(*, raw: str, workspace_path: str = "", adaptive: bool = True) -> dict[str, Any]:
    compiled = compile_prompt(raw=raw, workspace_path=workspace_path, adaptive=adaptive)
    if not compiled.get("ok"):
        return compiled
    route = compiled.get("suggested_route") or route_execution(compiled)
    return {
        **compiled,
        "dispatch_hint": {
            "action": "autonomous_run",
            "goal": raw,
            "workspace_path": workspace_path,
            "swarm": route.get("swarm", False),
            "cloud": route.get("cloud", False),
            "dry_run": True,
            "stackLevel": compiled.get("stackLevel"),
            "adaptive": adaptive,
            "executor": route.get("executor"),
        },
    }


def _execution_ok(result: dict[str, Any]) -> bool:
    if not result.get("ok"):
        return False
    state = str(result.get("state") or "").upper()
    if state in ("FAILED", "ERROR", "BLOCKED"):
        return False
    if state == "DONE":
        return True
    if result.get("done"):
        return True
    if result.get("agent") and result["agent"].get("done"):
        return True
    schema = str(result.get("schema") or "")
    if schema in ("forge-agent-kernel-swarm-v3", "forge-swarm-cloud-dispatch-v1"):
        return bool(result.get("ok"))
    return bool(result.get("ok"))


def _dispatch_execution(
    *,
    route: dict[str, Any],
    goal: str,
    workspace_path: str,
    dry_run: bool,
    cloud: bool,
    max_steps: int,
    max_tasks: int,
) -> dict[str, Any]:
    root = Path(workspace_path).expanduser().resolve()
    if not root.is_dir():
        return {"ok": False, "error": "invalid_workspace", "path": workspace_path}

    use_cloud = cloud or route.get("cloud", False)
    executor = route.get("executor", "agent_dev")

    if executor == "cloud_swarm_deploy" or (use_cloud and route.get("swarm")):
        from forge_swarm_blackboard_v1 import load_blackboard  # noqa: WPS433
        from forge_swarm_cloud_dispatch_v1 import dispatch_swarm_cloud  # noqa: WPS433

        return dispatch_swarm_cloud(
            goal=goal,
            workspace_path=str(root),
            parallel=True,
            planner_count=3,
            critic_count=3,
            blackboard_snapshot=load_blackboard(),
            dry_run=dry_run,
        )

    if executor == "swarm" or route.get("swarm"):
        from forge_agent_kernel_v3_swarm import run_swarm_loop  # noqa: WPS433

        return run_swarm_loop(
            goal=goal,
            workspace_path=str(root),
            max_tasks=max_tasks,
            max_steps_per_task=max(2, min(max_steps, 6)),
            dry_run=dry_run,
            parallel=True,
            parallel_build=True,
        )

    from forge_agent_kernel_v1 import run_agent_dev_loop  # noqa: WPS433

    return run_agent_dev_loop(
        goal=goal,
        workspace_path=str(root),
        max_steps=max_steps,
        dry_run=dry_run,
        patch_only=bool(route.get("patch_only")),
    )


def _deployment_phase(
    *,
    compiled: dict[str, Any],
    execution: dict[str, Any],
    dry_run: bool,
    cloud: bool,
    workspace_path: str,
) -> dict[str, Any] | None:
    route = compiled.get("suggested_route") or route_execution(compiled)
    if not route.get("deployment") and compiled.get("intent") != "deployment":
        return None
    return {
        "schema": "forge-prompt-os-deployment-phase-v3",
        "status": "queued_dry_run" if dry_run else "cloud_dispatch",
        "target": "cloud" if cloud or route.get("cloud") else "local",
        "stackLevel": compiled.get("stackLevel"),
        "execution_schema": execution.get("schema"),
        "cloud_status": execution.get("cloud_status") or execution.get("status"),
        "workspace_path": workspace_path,
        "at": _now(),
    }


def _append_queue(row: dict[str, Any]) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    queue: list[dict[str, Any]] = []
    if RUNTIME_QUEUE.is_file():
        try:
            queue = json.loads(RUNTIME_QUEUE.read_text(encoding="utf-8"))
            if not isinstance(queue, list):
                queue = []
        except (json.JSONDecodeError, OSError):
            queue = []
    queue.append(row)
    RUNTIME_QUEUE.write_text(json.dumps(queue[-MAX_QUEUE:], indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def autonomous_execute(
    *,
    raw: str,
    workspace_path: str,
    dry_run: bool = True,
    cloud: bool = False,
    adaptive: bool = True,
    max_steps: int = 6,
    max_tasks: int = 3,
    use_compiled_goal: bool = True,
) -> dict[str, Any]:
    """Full v3 loop: compile → route → execute → learn → deployment hint."""
    raw = (raw or "").strip()
    if not raw:
        return {"ok": False, "error": "empty_input", "schema": SCHEMA}
    if not workspace_path:
        return {"ok": False, "error": "workspace_required", "schema": SCHEMA}

    runtime_id = f"rt-{uuid.uuid4().hex[:10]}"
    compiled = compile_prompt(raw=raw, workspace_path=workspace_path, adaptive=adaptive)
    if not compiled.get("ok"):
        return compiled

    route = compiled.get("suggested_route") or route_execution(compiled)
    goal = str(compiled.get("cursor_mission") if use_compiled_goal else raw) or raw

    execution = _dispatch_execution(
        route=route,
        goal=goal,
        workspace_path=workspace_path,
        dry_run=dry_run,
        cloud=cloud,
        max_steps=max_steps,
        max_tasks=max_tasks,
    )

    deployment = _deployment_phase(
        compiled=compiled,
        execution=execution,
        dry_run=dry_run,
        cloud=cloud or bool(route.get("cloud")),
        workspace_path=workspace_path,
    )

    exec_ok = _execution_ok(execution)
    state = str(execution.get("state") or "")
    if not state and execution.get("swarm_id"):
        state = "DONE" if exec_ok else "FAILED"

    learning = record_execution_outcome(
        compiled=compiled,
        execution_ok=exec_ok,
        execution_state=state,
        run_id=runtime_id,
    )

    out: dict[str, Any] = {
        "ok": exec_ok,
        "schema": SCHEMA,
        "version": COMPILER_VERSION,
        "runtime_id": runtime_id,
        "autonomous": True,
        "dry_run": dry_run,
        "compiled": compiled,
        "route": route,
        "execution": execution,
        "deployment": deployment,
        "learning": learning,
        "founder_summary": _founder_summary(compiled, execution, exec_ok, deployment),
        "at": _now(),
    }

    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    _append_queue(
        {
            "runtime_id": runtime_id,
            "ok": exec_ok,
            "stack": compiled.get("stackLevel"),
            "intent": compiled.get("intent"),
            "executor": route.get("executor"),
            "dry_run": dry_run,
            "at": out["at"],
        }
    )
    return out


def _founder_summary(
    compiled: dict[str, Any],
    execution: dict[str, Any],
    ok: bool,
    deployment: dict[str, Any] | None,
) -> str:
    stack = compiled.get("stackLevel", "?")
    intent = compiled.get("intent", "build")
    status = "done" if ok else "blocked"
    base = f"Autonomous {intent} · {stack} · {status}"
    if deployment:
        return f"{base} · deploy {deployment.get('status', 'queued')}"
    schema = execution.get("schema", "")
    if schema == "forge-agent-kernel-swarm-v3":
        return f"{base} · swarm {execution.get('state', 'complete')}"
    return base


# Re-export for E2E
__all__ = [
    "SCHEMA",
    "COMPILER_VERSION",
    "compile_prompt",
    "compile_and_dispatch_hint",
    "autonomous_execute",
    "route_execution",
    "record_execution_outcome",
    "seed_learning_demo",
]
