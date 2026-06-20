#!/usr/bin/env python3
"""Execution kernel v1 — scheduler → state machine → prompt_router → receipt."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

SPINE_KEYWORD_MAP = {
    "code_writer": "implement",
    "code_reader": "debug",
    "linter": "fix",
    "researcher": "debug",
    "planner": "implement",
}


def _run_router(
    *,
    keyword: str,
    lane: str,
    task_id: str,
    invoke_loop: bool,
    dry_run: bool,
) -> dict[str, Any]:
    cmd = [
        sys.executable,
        str(SCRIPTS / "prompt_router.py"),
        "--keyword",
        keyword,
        "--lane",
        lane,
        "--json",
    ]
    if task_id:
        cmd.extend(["--task-id", task_id])
    if dry_run:
        cmd.append("--dry-run")
    if invoke_loop:
        cmd.append("--invoke-loop")
    proc = subprocess.run(cmd, capture_output=True, text=True, cwd=str(ROOT), check=False)
    if proc.returncode != 0:
        return {"ok": False, "error": proc.stderr or proc.stdout or "router failed"}
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"ok": False, "error": "invalid router json", "raw": proc.stdout[:500]}


def _spine_keyword(*, goal_tool_id: str = "pos-run", task_id: str = "") -> str | None:
    try:
        from runtime.execution_router.api import execution_router_v1_payload  # noqa: WPS433

        payload = execution_router_v1_payload(goal_tool_id=goal_tool_id, task_id=task_id)
    except Exception:
        return None
    if not payload.get("ok"):
        return None
    step = payload.get("next_step") or {}
    tool_id = (step.get("tool_id") or step.get("agent_type") or "").lower()
    for key, kw in SPINE_KEYWORD_MAP.items():
        if key in tool_id:
            return kw
    routing = payload.get("routing_decision") or ""
    if routing in ("block", "wait"):
        return None
    return "implement"


def tick(
    *,
    lane: str = "sourcea",
    keyword: str = "PLAN WITH NO ASF",
    invoke_loop: bool = False,
    dry_run: bool = True,
    use_spine_router: bool = False,
    goal_tool_id: str = "pos-run",
    task_id: str = "",
    skip_scheduler: bool = False,
) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from execution_scheduler import persist_scheduled, schedule_next  # noqa: WPS433
    from execution_state_hub import mark_running, mark_verifying, status_payload  # noqa: WPS433

    st = status_payload(lane=lane)
    if st.get("loop_active") and invoke_loop:
        return {"ok": False, "error": "agent loop already active", "status": st}

    scheduled: dict[str, Any] | None = None
    pick_id = task_id
    if not skip_scheduler and not pick_id:
        scheduled = schedule_next(lane=lane)
        if not scheduled.get("ok"):
            return scheduled
        pick_id = scheduled.get("task_id") or ""
        if not scheduled.get("idle"):
            persist_scheduled(
                lane=lane,
                task_id=pick_id,
                from_state=scheduled.get("transition", {}).get("from", "queued"),
            )

    kw = keyword
    if use_spine_router:
        spine_kw = _spine_keyword(goal_tool_id=goal_tool_id, task_id=pick_id)
        if spine_kw:
            kw = spine_kw

    router = _run_router(keyword=kw, lane=lane, task_id=pick_id, invoke_loop=invoke_loop, dry_run=dry_run)
    if router.get("error") and not router.get("prompt"):
        return {"ok": False, "error": router.get("error"), "scheduled": scheduled}

    meta = router.get("meta") or {}
    verify_result: dict[str, Any] | None = None
    idle_task = pick_id == "registry-exhausted-idle" or bool(scheduled and scheduled.get("idle"))
    if pick_id and not idle_task:
        run_result = mark_running(lane=lane, task_id=pick_id)
        if not run_result.get("ok"):
            return {"ok": False, "error": run_result.get("error"), "scheduled": scheduled}

    router_ok = not router.get("error") and bool(router.get("prompt") or router.get("loop"))
    if pick_id and router_ok and not dry_run and not idle_task:
        verify_result = mark_verifying(lane=lane, task_id=pick_id)
        if not verify_result.get("ok"):
            return {"ok": False, "error": verify_result.get("error"), "scheduled": scheduled}

    state_transition = None
    if pick_id:
        state_transition = "scheduled→running"
        if verify_result and verify_result.get("ok"):
            state_transition = "running→verifying"

    receipt = {
        "ok": True,
        "schema": "execution-kernel-v1",
        "lane": lane,
        "keyword": kw,
        "next_task_id": pick_id or meta.get("pick_id"),
        "scheduled": scheduled,
        "state_transition": state_transition,
        "verify": verify_result,
        "meta": meta,
        "prompt_preview": (router.get("prompt") or "")[:400],
        "loop": router.get("loop"),
        "dry_run": dry_run,
        "invoke_loop": invoke_loop,
        "use_spine_router": use_spine_router,
        "invariant": "event→schedule→execute→verify→persist",
    }

    from agent_governance_events import log_governance_event  # noqa: WPS433

    log_governance_event(
        "execution_kernel_v1",
        workspace_id=lane,
        detail=f"tick pick={pick_id or '-'} kw={kw}",
        extra={"next_task_id": pick_id, "keyword": kw, "scheduler": bool(scheduled)},
    )
    return receipt


def main() -> None:
    parser = argparse.ArgumentParser(description="Execution kernel v1")
    parser.add_argument("--tick", action="store_true", help="Schedule + assemble prompt")
    parser.add_argument("--lane", default=os.environ.get("SINA_PROMPT_LANE", "sourcea"))
    parser.add_argument("--keyword", default="PLAN WITH NO ASF")
    parser.add_argument("--task-id", default="")
    parser.add_argument("--invoke-loop", action="store_true")
    parser.add_argument("--dry-run", action="store_true", default=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--use-spine-router", action="store_true")
    parser.add_argument("--skip-scheduler", action="store_true")
    parser.add_argument("--goal-tool-id", default="pos-run")
    args = parser.parse_args()

    dry = not args.execute
    if args.dry_run and not args.execute:
        dry = True

    if not args.tick:
        parser.error("use --tick")

    out = tick(
        lane=args.lane.strip().lower(),
        keyword=args.keyword,
        task_id=(args.task_id or "").strip(),
        invoke_loop=args.invoke_loop and args.execute,
        dry_run=dry,
        use_spine_router=args.use_spine_router,
        goal_tool_id=args.goal_tool_id,
        skip_scheduler=args.skip_scheduler,
    )
    print(json.dumps(out, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
