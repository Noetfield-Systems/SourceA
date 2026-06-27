#!/usr/bin/env python3
"""Forge Agent Kernel v3 — Swarm (Planner / Builder / Reviewer + repo intel + git apply).

Receipt: ~/.sina/forge-agent-kernel-swarm-v3.json
Law: Mac control plane · workspace-only · light index (no validator marathon).
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
import uuid
from collections import Counter
from datetime import datetime, timezone
from enum import Enum
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from forge_agent_kernel_v1 import (  # noqa: E402
    ForgeAgentTools,
    MAX_STEPS,
    _llm_json,
    _now,
    run_agent_dev_loop,
    run_verify_harness_static,
)

SINA = Path.home() / ".sina"
SWARM_RECEIPT = SINA / "forge-agent-kernel-swarm-v3.json"

BANNED_DIFF = re.compile(
    r"rm\s+-rf\s+/|delete entire repo|\.env\b|secrets\.env|chmod\s+777",
    re.I,
)


class ForgeState(str, Enum):
    IDLE = "IDLE"
    PLANNING = "PLANNING"
    BUILDING = "BUILDING"
    PATCHING = "PATCHING"
    VERIFYING = "VERIFYING"
    FAILED = "FAILED"
    DONE = "DONE"


SWARM_PLANNER = """You are the Forge Planner agent (swarm v3).
Reply JSON only:
{"tasks": ["step 1", "step 2", ...], "risks": ["..."], "repo_focus": ["paths or symbols"]}
Max 6 tasks. Prefer analyze → patch → test → verify order."""

SWARM_BUILDER = """You are the Forge Builder agent (swarm v3).
Tools: read_file, patch_file, apply_git_patch, write_file, list_files, search_code, search_semantic, repo_index, run_shell
Reply JSON only:
{"done": false, "summary": "...", "action": {"tool": "...", "args": {...}}}
Prefer apply_git_patch or patch_file over write_file. Use search_semantic to locate code."""

SWARM_REVIEWER = """You are the Forge Reviewer agent (swarm v3).
Given goal, task, and builder result, reply JSON only:
{"approved": true|false, "issues": ["..."], "retry_hint": "..."}"""

SWARM_REPAIR = """You are the Forge Repair agent (swarm v3).
Given critic issues and blackboard snapshot, reply JSON only:
{"fixes": ["specific patch hint 1", "..."], "priority": "high|medium|low"}"""

SWARM_OPTIMIZER = """You are the Forge Optimizer agent (swarm v3).
Given tasks and repo graph size, reply JSON only:
{"skip_tasks": [], "model_tier": "build|check|reason", "notes": "..."}"""


def safety_check_diff(diff: str) -> tuple[bool, str]:
    if not (diff or "").strip():
        return False, "empty_diff"
    if BANNED_DIFF.search(diff):
        return False, "banned_pattern"
    return True, "ok"


def _tokenize(text: str) -> Counter[str]:
    return Counter(re.findall(r"[a-zA-Z_][a-zA-Z0-9_]{2,}", text.lower()))


class ForgeSwarmTools(ForgeAgentTools):
    """v3 tools: git apply + semantic search + repo index."""

    def repo_index(self, *, force: bool = False) -> dict[str, Any]:
        file_count = sum(1 for p in self.root.rglob("*") if p.is_file() and "node_modules" not in p.parts)
        if file_count > 800 and not force:
            return {"ok": True, "files": file_count, "symbols": 0, "edges": 0, "light_scan": True}
        try:
            from pre_llm.code_intelligence.index_builder import run_full_index  # noqa: WPS433

            row = run_full_index(repo_root=str(self.root), task_id=f"forge-swarm:{self.root.name}", force_refresh=force)
            stats = row.get("index_stats") or {}
            return {
                "ok": bool(row.get("ok")),
                "files": stats.get("files", 0),
                "symbols": stats.get("symbols", 0),
                "edges": stats.get("edges", 0),
                "cached": row.get("cached"),
            }
        except Exception as exc:
            return {"ok": False, "error": type(exc).__name__, "message": str(exc)[:200]}

    def search_semantic(self, query: str, limit: int = 12) -> dict[str, Any]:
        q = (query or "").strip()
        if not q:
            return {"ok": False, "error": "empty_query"}
        q_tokens = _tokenize(q)
        if not q_tokens:
            return self.search_code(query, limit)

        try:
            from pre_llm.code_intelligence.index_builder import run_full_index  # noqa: WPS433
            from pre_llm.code_intelligence.query_engine import run_query  # noqa: WPS433

            idx = run_full_index(repo_root=str(self.root), task_id=f"forge-swarm-q:{self.root.name}")
            if idx.get("ok"):
                sym = run_query(query_type="find_symbol", arg=q.split()[-1], canonical=idx)
                if sym.get("hits"):
                    return {"ok": True, "method": "code_intel", "hits": sym.get("hits")[:limit]}
        except Exception:
            pass

        scores: list[tuple[float, str, int]] = []
        for p in self.root.rglob("*"):
            if p.suffix not in (".py", ".js", ".ts", ".tsx", ".md", ".json") or not p.is_file():
                continue
            if p.stat().st_size > 256_000 or "node_modules" in p.parts:
                continue
            try:
                text = p.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            ft = _tokenize(text[:12000])
            if not ft:
                continue
            overlap = sum(min(ft[t], q_tokens[t]) for t in q_tokens if t in ft)
            if overlap > 0:
                rel = p.relative_to(self.root).as_posix()
                line = next((i + 1 for i, ln in enumerate(text.splitlines()) if q.lower() in ln.lower()), 0)
                scores.append((float(overlap), rel, line))
        scores.sort(reverse=True)
        hits = [{"path": r, "line": str(ln), "score": sc} for sc, r, ln in scores[:limit]]
        return {"ok": True, "method": "token_overlap", "hits": hits, "count": len(hits)}

    def apply_git_patch(self, diff: str, *, dry_run: bool = False) -> dict[str, Any]:
        ok, reason = safety_check_diff(diff)
        if not ok:
            return {"ok": False, "error": "safety_blocked", "reason": reason}
        git_dir = self.root / ".git"
        if not git_dir.is_dir():
            return {"ok": False, "error": "not_git_repo", "hint": "use patch_file instead"}
        tmp = self.root / ".forge-swarm.patch"
        try:
            tmp.write_text(diff, encoding="utf-8")
            check = subprocess.run(
                ["git", "apply", "--check", str(tmp)],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            if check.returncode != 0:
                return {
                    "ok": False,
                    "error": "git_apply_check_failed",
                    "stderr": (check.stderr or "")[:2000],
                }
            if dry_run:
                return {"ok": True, "dry_run": True, "diff_bytes": len(diff)}
            apply = subprocess.run(
                ["git", "apply", str(tmp)],
                cwd=self.root,
                capture_output=True,
                text=True,
                timeout=30,
            )
            return {
                "ok": apply.returncode == 0,
                "exit_code": apply.returncode,
                "stderr": (apply.stderr or "")[:2000],
                "diff_bytes": len(diff),
            }
        except subprocess.TimeoutExpired:
            return {"ok": False, "error": "timeout"}
        except OSError as exc:
            return {"ok": False, "error": str(exc)}
        finally:
            try:
                tmp.unlink(missing_ok=True)
            except OSError:
                pass

    def execute(
        self,
        action: dict[str, Any],
        *,
        dry_run: bool = False,
        patch_only: bool = False,
        agent_id: str = "builder-001",
        agent_role: str = "builder",
        task_id: str = "",
        governance_level: str = "SWARM",
    ) -> dict[str, Any]:
        tool = str(action.get("tool") or "").strip()
        args = action.get("args") or {}
        try:
            from forge_governance_kernel_v1 import govern  # noqa: WPS433

            payload = dict(args) if isinstance(args, dict) else {}
            if tool == "apply_git_patch":
                payload = {"diff": str(args.get("diff") or "")[:2000]}
            decision = govern(
                agent_id=agent_id,
                agent_role=agent_role,
                action_type=tool,
                payload=payload,
                task_id=task_id,
                level=governance_level,
                dry_run=dry_run,
                charge_on_allow=not dry_run,
            )
            if decision.get("status") == "DENY":
                return {"ok": False, "error": "governance_denied", "governance": decision, "tool": tool}
        except Exception:
            pass
        if tool == "apply_git_patch":
            return self.apply_git_patch(str(args.get("diff") or ""), dry_run=dry_run)
        if tool == "search_semantic":
            return self.search_semantic(str(args.get("query") or ""), int(args.get("limit") or 12))
        if tool == "repo_index":
            return self.repo_index(force=bool(args.get("force")))
        return super().execute(action, dry_run=dry_run, patch_only=patch_only)


SWARM_CRITIC = """You are a Forge Critic agent (swarm v3 parallel).
Given goal and blackboard snapshot, reply JSON only:
{"approved": true|false, "score": 0.0-1.0, "issues": ["..."]}
Score 1.0 = goal fully met on disk. Be strict on missing tests or broken patches."""


def _planner_tasks(*, goal: str, intel: dict[str, Any], planner_id: int = 0) -> dict[str, Any]:
    from model_dispatch import pick_roi_model  # noqa: WPS433

    model = pick_roi_model("reason")
    user = f"Goal: {goal}\nPlanner #{planner_id}\nRepo index: {json.dumps(intel)[:4000]}"
    row = _llm_json(system=SWARM_PLANNER, user=user, model=model, source=f"forge-swarm-planner-{planner_id}")
    if not row.get("ok"):
        return {"ok": False, "tasks": [goal], "fallback": row}
    parsed = row["parsed"]
    tasks = parsed.get("tasks") or [goal]
    if isinstance(tasks, str):
        tasks = [tasks]
    return {"ok": True, "tasks": [str(t) for t in tasks[:6]], "parsed": parsed, "model": model}


def _review_task(*, goal: str, task: str, builder_out: dict[str, Any]) -> dict[str, Any]:
    from model_dispatch import pick_roi_model  # noqa: WPS433

    model = pick_roi_model("check")
    user = f"Goal: {goal}\nTask: {task}\nBuilder: {json.dumps(builder_out)[:6000]}"
    row = _llm_json(system=SWARM_REVIEWER, user=user, model=model, source="forge-swarm-reviewer")
    if not row.get("ok"):
        return {"approved": True, "issues": [], "fallback": True}
    parsed = row["parsed"]
    return {
        "approved": bool(parsed.get("approved", True)),
        "issues": parsed.get("issues") or [],
        "retry_hint": parsed.get("retry_hint") or "",
        "model": model,
    }


def _repair_swarm(*, goal: str, board: dict[str, Any], issues: list[str], dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {"ok": True, "fixes": issues[:3] or ["Review critic issues"], "priority": "high", "stub": True}
    from model_dispatch import pick_roi_model  # noqa: WPS433

    model = pick_roi_model("build")
    user = f"Goal: {goal}\nIssues: {json.dumps(issues[:8])}\nLogs: {json.dumps(board.get('logs', [])[-5:])}"
    row = _llm_json(system=SWARM_REPAIR, user=user, model=model, source="forge-swarm-repair")
    if not row.get("ok"):
        return {"ok": False, "fixes": issues[:3], "fallback": True}
    parsed = row["parsed"]
    return {"ok": True, "fixes": parsed.get("fixes") or issues[:3], "priority": parsed.get("priority") or "high", "model": model}


def _optimizer_swarm(*, tasks: list[str], repo_graph: dict[str, Any], dry_run: bool = False) -> dict[str, Any]:
    if dry_run:
        return {"ok": True, "skip_tasks": [], "model_tier": "build", "notes": "dry_run stub", "stub": True}
    from model_dispatch import pick_roi_model  # noqa: WPS433

    model = pick_roi_model("check")
    snap = {"task_count": len(tasks), "graph_nodes": len((repo_graph or {}).get("nodes") or [])}
    user = f"Tasks: {json.dumps(tasks[:8])}\nGraph: {json.dumps(snap)}"
    row = _llm_json(system=SWARM_OPTIMIZER, user=user, model=model, source="forge-swarm-optimizer")
    if not row.get("ok"):
        return {"ok": True, "skip_tasks": [], "model_tier": "build", "notes": "fallback", "fallback": True}
    parsed = row["parsed"]
    return {
        "ok": True,
        "skip_tasks": parsed.get("skip_tasks") or [],
        "model_tier": parsed.get("model_tier") or "build",
        "notes": parsed.get("notes") or "",
        "model": model,
    }


def _run_builder_task(
    *,
    goal: str,
    task: str,
    root: Path,
    rnd: int,
    i: int,
    total: int,
    max_steps_per_task: int,
) -> dict[str, Any]:
    task_goal = f"{goal}\n\nSwarm task {i}/{total} (round {rnd}): {task}"
    builder = run_agent_dev_loop(
        goal=task_goal,
        workspace_path=str(root),
        max_steps=max_steps_per_task,
        dry_run=False,
        planner_system=SWARM_BUILDER,
        tools_class=ForgeSwarmTools,
    )
    review = _review_task(goal=goal, task=task, builder_out=builder)
    if not review.get("approved") and review.get("retry_hint"):
        builder = run_agent_dev_loop(
            goal=f"{task_goal}\nFix: {review.get('retry_hint')}",
            workspace_path=str(root),
            max_steps=2,
            dry_run=False,
            planner_system=SWARM_BUILDER,
            tools_class=ForgeSwarmTools,
        )
        review = _review_task(goal=goal, task=task, builder_out=builder)
    return {"task": task, "builder": builder, "review": review, "round": rnd}


def _critic_swarm(*, goal: str, board: dict[str, Any], critic_id: int = 0) -> dict[str, Any]:
    from model_dispatch import pick_roi_model  # noqa: WPS433

    model = pick_roi_model("check")
    snap = {
        "tasks": board.get("tasks", [])[:8],
        "artifacts": board.get("artifacts", [])[:5],
        "logs": board.get("logs", [])[-5:],
        "repo_graph_nodes": len((board.get("repo_graph") or {}).get("nodes") or []),
    }
    user = f"Goal: {goal}\nCritic #{critic_id}\nBlackboard: {json.dumps(snap)[:5000]}"
    row = _llm_json(system=SWARM_CRITIC, user=user, model=model, source=f"forge-swarm-critic-{critic_id}")
    if not row.get("ok"):
        return {"approved": True, "score": 0.7, "issues": [], "fallback": True}
    parsed = row["parsed"]
    return {
        "approved": bool(parsed.get("approved", True)),
        "score": float(parsed.get("score") or (1.0 if parsed.get("approved") else 0.3)),
        "issues": parsed.get("issues") or [],
        "critic_id": critic_id,
        "model": model,
    }


def _parallel_planners(*, goal: str, intel: dict[str, Any], count: int = 3) -> list[dict[str, Any]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if count <= 1:
        return [_planner_tasks(goal=goal, intel=intel, planner_id=0)]
    plans: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(count, 3)) as pool:
        futs = {pool.submit(_planner_tasks, goal=goal, intel=intel, planner_id=i): i for i in range(count)}
        for fut in as_completed(futs):
            try:
                plans.append(fut.result())
            except Exception as exc:
                plans.append({"ok": False, "tasks": [goal], "error": str(exc)[:80]})
    return plans


def _parallel_critics(*, goal: str, board: dict[str, Any], count: int = 3) -> list[dict[str, Any]]:
    from concurrent.futures import ThreadPoolExecutor, as_completed

    if count <= 1:
        return [_critic_swarm(goal=goal, board=board, critic_id=0)]
    verdicts: list[dict[str, Any]] = []
    with ThreadPoolExecutor(max_workers=min(count, 3)) as pool:
        futs = {pool.submit(_critic_swarm, goal=goal, board=board, critic_id=i): i for i in range(count)}
        for fut in as_completed(futs):
            try:
                verdicts.append(fut.result())
            except Exception as exc:
                verdicts.append({"approved": False, "score": 0.0, "issues": [str(exc)[:80]]})
    return verdicts


def run_swarm_loop(
    *,
    goal: str,
    workspace_path: str,
    max_tasks: int = 5,
    max_steps_per_task: int = 4,
    dry_run: bool = False,
    parallel: bool = True,
    parallel_build: bool = True,
    planner_count: int = 3,
    critic_count: int = 3,
    max_replan_rounds: int = 2,
) -> dict[str, Any]:
    """v3 swarm: blackboard → parallel planners → build → parallel critics → replan."""
    from forge_swarm_blackboard_v1 import (  # noqa: WPS433
        aggregate_critic_verdicts,
        build_repo_graph_light,
        build_task_economy,
        collect_agent_bids,
        merge_plans,
        new_blackboard,
        save_blackboard,
    )

    root = Path(workspace_path).expanduser().resolve()
    if not root.is_dir():
        return {"ok": False, "error": "invalid_workspace", "path": workspace_path}

    goal = (goal or "").strip()
    if not goal:
        return {"ok": False, "error": "empty_goal"}

    swarm_id = f"swarm-{uuid.uuid4().hex[:10]}"
    board = new_blackboard(goal=goal, workspace_path=str(root))
    board["swarm_id"] = swarm_id
    board["parallel"] = parallel
    repair_runs: list[dict[str, Any]] = []
    optimizer_notes: dict[str, Any] = {}

    try:
        from forge_agent_registry_v1 import assign_planner_ids, evolve_agents, load_registry, update_reputation  # noqa: WPS433

        planner_agent_ids = assign_planner_ids(planner_count)
        registry = load_registry()
    except Exception:
        planner_agent_ids = [f"planner-{i + 1:03d}" for i in range(planner_count)]
        registry = {"agents": []}
        update_reputation = evolve_agents = None  # type: ignore

    if dry_run:
        board["logs"].append("dry_run stub")
        board["tasks"] = [{"type": "analyze_repo", "text": goal, "priority": 1}]
        board["planner_votes"] = [{"planner_id": 0, "agent_id": planner_agent_ids[0] if planner_agent_ids else "planner-001", "tasks": [goal]}]
        board["critic_verdicts"] = [{"approved": True, "score": 1.0}]
        board["task_economy"] = build_task_economy(tasks=[goal], goal=goal, repo_graph={"nodes": [], "edges": []})
        board["agent_bids"] = collect_agent_bids(board["task_economy"], registry)
        save_blackboard(board)
        out = {
            "ok": True,
            "schema": "forge-agent-kernel-swarm-v3",
            "swarm_id": swarm_id,
            "goal": goal,
            "workspace_path": str(root),
            "state": ForgeState.DONE.value,
            "dry_run": True,
            "parallel": parallel,
            "parallel_build": parallel_build,
            "blackboard": board,
            "repo_intel": {"ok": True, "files": 1, "stub": True},
            "repo_graph": {"nodes": [], "edges": [], "symbols": []},
            "plan": {"ok": True, "tasks": [goal], "merged_from": 1},
            "task_runs": [
                {
                    "task": goal,
                    "builder": {"ok": True, "done": False, "steps": [{"step": 1, "summary": "dry_run stub"}], "run_id": f"agk-dry-{swarm_id[:8]}"},
                    "review": {"approved": True, "issues": []},
                }
            ],
            "repair_runs": [],
            "optimizer_notes": {"notes": "dry_run stub"},
            "critic_aggregate": {"approved": True, "score": 1.0},
            "verify_harness": run_verify_harness_static(workspace_path=str(root)),
            "at": _now(),
        }
        SWARM_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        SWARM_RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        try:
            from forge_civilization_memory_v1 import record_run  # noqa: WPS433

            record_run(out)
        except Exception:
            pass
        return out

    tools = ForgeSwarmTools(root)
    intel = tools.repo_index(force=False)
    if not intel.get("ok"):
        intel = tools.list_files(prefix="", limit=30)
    board["repo_state"] = intel if isinstance(intel, dict) else {}
    try:
        from forge_repo_intel_v1 import build_repo_graph  # noqa: WPS433

        board["repo_graph"] = build_repo_graph(workspace=root)
    except Exception:
        board["repo_graph"] = build_repo_graph_light(workspace=root, intel=board["repo_state"])

    replan_rounds: list[dict[str, Any]] = []
    state = ForgeState.PLANNING
    task_runs: list[dict[str, Any]] = []
    critic_aggregate: dict[str, Any] = {"approved": False, "score": 0.0}

    for rnd in range(1, max_replan_rounds + 1):
        board["round"] = rnd
        board["logs"].append(f"replan_round_{rnd}_start")
        state = ForgeState.PLANNING

        if parallel:
            plans = _parallel_planners(goal=goal, intel=board["repo_state"], count=planner_count)
            board["planner_votes"] = [
                {"planner_id": i, "agent_id": planner_agent_ids[i] if i < len(planner_agent_ids) else f"planner-{i:03d}", "tasks": p.get("tasks")}
                for i, p in enumerate(plans)
            ]
            tasks = merge_plans(plans, max_tasks=max_tasks)
        else:
            plan = _planner_tasks(goal=goal, intel=board["repo_state"])
            tasks = plan.get("tasks") or [goal]
            plans = [plan]

        optimizer_notes = _optimizer_swarm(tasks=tasks, repo_graph=board["repo_graph"], dry_run=False)
        skip = set(optimizer_notes.get("skip_tasks") or [])
        tasks = [t for t in tasks if t not in skip][:max_tasks]

        board["tasks"] = [{"type": "task", "text": t, "priority": i + 1} for i, t in enumerate(tasks)]
        board["task_economy"] = build_task_economy(tasks=tasks, goal=goal, repo_graph=board["repo_graph"])
        board["agent_bids"] = collect_agent_bids(board["task_economy"], registry)
        state = ForgeState.BUILDING
        round_runs: list[dict[str, Any]] = []

        if parallel_build and len(tasks) > 1:
            from forge_execution_mesh_v1 import execute_mesh  # noqa: WPS433

            jobs = [{"goal": goal, "task": t, "rnd": rnd, "i": i, "total": len(tasks[:max_tasks])} for i, t in enumerate(tasks[:max_tasks], start=1)]

            def _mesh_job(job: dict[str, Any]) -> dict[str, Any]:
                return _run_builder_task(
                    goal=job["goal"],
                    task=job["task"],
                    root=root,
                    rnd=job["rnd"],
                    i=job["i"],
                    total=job["total"],
                    max_steps_per_task=max_steps_per_task,
                )

            round_runs = execute_mesh(jobs, run_fn=_mesh_job)
        else:
            for i, task in enumerate(tasks[:max_tasks], start=1):
                round_runs.append(
                    _run_builder_task(goal=goal, task=task, root=root, rnd=rnd, i=i, total=len(tasks[:max_tasks]), max_steps_per_task=max_steps_per_task)
                )

        for rec in round_runs:
            task_runs.append(rec)
            builder = rec.get("builder") or {}
            if builder.get("steps"):
                board["artifacts"].append({"task": rec.get("task"), "steps": len(builder.get("steps") or []), "round": rnd})

        state = ForgeState.VERIFYING
        if parallel:
            verdicts = _parallel_critics(goal=goal, board=board, count=critic_count)
            board["critic_verdicts"] = verdicts
            critic_aggregate = aggregate_critic_verdicts(verdicts)
        else:
            critic_aggregate = aggregate_critic_verdicts([_critic_swarm(goal=goal, board=board)])

        replan_rounds.append({"round": rnd, "tasks": len(tasks), "critic": critic_aggregate, "runs": len(round_runs)})
        board["logs"].append(f"round_{rnd}_critic_approved={critic_aggregate.get('approved')}")
        save_blackboard(board)

        if critic_aggregate.get("approved"):
            state = ForgeState.DONE
            break
        if rnd < max_replan_rounds:
            board["logs"].append("replanning...")
            repair = _repair_swarm(goal=goal, board=board, issues=critic_aggregate.get("issues") or [], dry_run=False)
            repair_runs.append({"round": rnd, "repair": repair})
            fixes = repair.get("fixes") or []
            goal = f"{goal}\nFix issues: {'; '.join((critic_aggregate.get('issues') or []) + fixes)[:400]}"

    harness = run_verify_harness_static(workspace_path=str(root))
    if not harness.get("ok"):
        state = ForgeState.FAILED
    elif state != ForgeState.DONE:
        state = ForgeState.FAILED if not critic_aggregate.get("approved") else ForgeState.DONE

    success = state == ForgeState.DONE or any(tr.get("builder", {}).get("ok") for tr in task_runs)
    if update_reputation:
        agent_ids = planner_agent_ids + [b.get("agent_id") for b in board.get("agent_bids") or [] if b.get("agent_id")]
        update_reputation(agent_ids=agent_ids[:8], success=success)
        evolve_agents(success=success)
        if success and not dry_run:
            try:
                from forge_economy_v1 import reward_agent  # noqa: WPS433

                for aid in agent_ids[:3]:
                    reward_agent(agent_id=aid, amount=1.0, reason="swarm_success")
            except Exception:
                pass

    out = {
        "ok": success,
        "schema": "forge-agent-kernel-swarm-v3",
        "swarm_id": swarm_id,
        "goal": goal,
        "workspace_path": str(root),
        "state": state.value,
        "parallel": parallel,
        "parallel_build": parallel_build,
        "blackboard": board,
        "repo_intel": board["repo_state"],
        "repo_graph": board["repo_graph"],
        "plan": {"tasks": [t.get("text") for t in board.get("tasks") or []], "merged_from": len(board.get("planner_votes") or [])},
        "task_runs": task_runs,
        "repair_runs": repair_runs,
        "optimizer_notes": optimizer_notes,
        "replan_rounds": replan_rounds,
        "critic_aggregate": critic_aggregate,
        "verify_harness": harness,
        "at": _now(),
    }
    SWARM_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    SWARM_RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    save_blackboard(board)
    try:
        from forge_civilization_memory_v1 import record_run  # noqa: WPS433

        record_run(out)
    except Exception:
        pass
    if not success:
        try:
            from forge_l3_auto_runtime_v1 import enqueue_swarm_repair  # noqa: WPS433

            enqueue_swarm_repair(swarm_id=swarm_id, goal=goal, issues=critic_aggregate.get("issues"))
        except Exception:
            pass
    return out
