#!/usr/bin/env python3
"""Forge Prompt OS Compiler v2 — adaptive learning layer over v1.

Learns from successful executions, tunes stack routing, evolves constraints.
Receipt: ~/.sina/forge-prompt-os-compiler-latest-v2.json
Learning store: ~/.sina/forge-prompt-os-learning-v2.json
Law: brain-os/law/enforcement/SOURCEA_FORGE_PROMPT_OS_COMPILER_V2_LOCKED_v1.md
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from forge_prompt_os_compiler_v1 import (  # noqa: WPS433
    SCHEMA as SCHEMA_V1,
    StackLevel,
    build_cursor_mission,
    build_prompt,
    calculate_priority,
    complexity_score,
    estimate_cost,
    execution_mode_for_stack,
    generate_constraints,
    parse_intent,
    resolve_context,
    select_stack,
    to_forge_task,
    _load_system_state,
    _now,
)

SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-prompt-os-compiler-latest-v2.json"
LEARNING_STORE = SINA / "forge-prompt-os-learning-v2.json"
SCHEMA = "forge-prompt-os-compiler-v2"
COMPILER_VERSION = "2.0.0"
MAX_RUN_HISTORY = 200
MIN_SAMPLES_FOR_ADAPTIVE = 3

STACK_LEVELS: tuple[str, ...] = ("L1", "L2", "L3", "L4", "L5", "L6", "L7")


def _empty_learning() -> dict[str, Any]:
    return {
        "schema": "forge-prompt-os-learning-v2",
        "version": COMPILER_VERSION,
        "intent_stack_stats": {},
        "constraint_hits": {},
        "pattern_scores": {},
        "stack_bias": {lvl: 0.0 for lvl in STACK_LEVELS},
        "runs": [],
        "updated_at": _now(),
    }


def load_learning() -> dict[str, Any]:
    if LEARNING_STORE.is_file():
        try:
            data = json.loads(LEARNING_STORE.read_text(encoding="utf-8"))
            if isinstance(data, dict) and data.get("schema") == "forge-prompt-os-learning-v2":
                return data
        except (json.JSONDecodeError, OSError):
            pass
    return _empty_learning()


def save_learning(data: dict[str, Any]) -> dict[str, Any]:
    data["updated_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    LEARNING_STORE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return data


def _success_rate(stats: dict[str, int]) -> float:
    ok = int(stats.get("success") or 0)
    fail = int(stats.get("fail") or 0)
    total = ok + fail
    if total == 0:
        return 0.5
    return ok / total


def _intent_stats(learning: dict[str, Any], intent: str) -> dict[str, dict[str, int]]:
    all_stats = learning.setdefault("intent_stack_stats", {})
    return all_stats.setdefault(intent, {lvl: {"success": 0, "fail": 0} for lvl in STACK_LEVELS})


def best_learned_stack(intent: str, learning: dict[str, Any] | None = None) -> str | None:
    """Pick stack with highest success rate for intent when enough samples exist."""
    store = learning or load_learning()
    intent_rows = (store.get("intent_stack_stats") or {}).get(intent) or {}
    best_lvl: str | None = None
    best_rate = -1.0
    for lvl in STACK_LEVELS:
        stats = intent_rows.get(lvl) or {}
        total = int(stats.get("success") or 0) + int(stats.get("fail") or 0)
        if total < MIN_SAMPLES_FOR_ADAPTIVE:
            continue
        rate = _success_rate(stats)
        if rate > best_rate:
            best_rate = rate
            best_lvl = lvl
    return best_lvl


def select_stack_adaptive(intent: str, complexity: float, learning: dict[str, Any] | None = None) -> tuple[StackLevel, dict[str, Any]]:
    """v1 baseline + learned override + complexity nudge."""
    store = learning or load_learning()
    baseline = select_stack(intent, complexity)
    learned = best_learned_stack(intent, store)
    meta: dict[str, Any] = {
        "baseline_stack": baseline,
        "learned_stack": learned,
        "adaptive_applied": False,
        "complexity": complexity,
    }

    chosen: StackLevel = baseline  # type: ignore[assignment]
    if learned and learned != baseline:
        learned_stats = (_intent_stats(store, intent).get(learned) or {})
        base_stats = (_intent_stats(store, intent).get(baseline) or {})
        learned_total = int(learned_stats.get("success") or 0) + int(learned_stats.get("fail") or 0)
        base_total = int(base_stats.get("success") or 0) + int(base_stats.get("fail") or 0)
        if learned_total >= MIN_SAMPLES_FOR_ADAPTIVE and (
            base_total < MIN_SAMPLES_FOR_ADAPTIVE or _success_rate(learned_stats) > _success_rate(base_stats) + 0.1
        ):
            chosen = learned  # type: ignore[assignment]
            meta["adaptive_applied"] = True

    # Complexity nudge: high complexity bumps one level if adaptive data supports it
    if complexity > 0.75 and chosen in ("L1", "L2", "L3", "L4", "L5"):
        idx = STACK_LEVELS.index(chosen)
        if idx < len(STACK_LEVELS) - 1:
            nudged = STACK_LEVELS[idx + 1]
            nudged_stats = (_intent_stats(store, intent).get(nudged) or {})
            if int(nudged_stats.get("success") or 0) >= MIN_SAMPLES_FOR_ADAPTIVE:
                meta["complexity_nudge"] = nudged
                chosen = nudged  # type: ignore[assignment]

    bias = store.get("stack_bias") or {}
    if isinstance(bias, dict):
        meta["stack_bias"] = {k: bias.get(k, 0.0) for k in STACK_LEVELS}

    meta["chosen_stack"] = chosen
    return chosen, meta


def generate_constraints_adaptive(intent: str, learning: dict[str, Any] | None = None) -> tuple[list[str], list[str]]:
    """Base constraints + dynamically evolved constraints from successful runs."""
    base = generate_constraints(intent)
    store = learning or load_learning()
    hits = store.get("constraint_hits") or {}
    ranked: list[tuple[float, str]] = []
    for constraint, stats in hits.items():
        if not isinstance(stats, dict):
            continue
        total = int(stats.get("success") or 0) + int(stats.get("fail") or 0)
        if total < MIN_SAMPLES_FOR_ADAPTIVE:
            continue
        rate = _success_rate(stats)
        if rate >= 0.7 and constraint not in base:
            ranked.append((rate, constraint))
    ranked.sort(reverse=True)
    evolved = [c for _, c in ranked[:3]]
    return base + evolved, evolved


def record_execution_outcome(
    *,
    compiled: dict[str, Any],
    execution_ok: bool,
    execution_state: str = "",
    quality_verdict: str = "",
    run_id: str = "",
) -> dict[str, Any]:
    """Learn from a completed Forge execution tied to a compiler spec."""
    if not compiled or not compiled.get("ok"):
        return {"ok": False, "error": "no_compiled_spec"}

    intent = str(compiled.get("intent") or "general_build")
    stack = str(compiled.get("stackLevel") or "L3")
    success = bool(execution_ok)
    if quality_verdict.upper() in ("REJECT", "FAIL"):
        success = False
    if execution_state.upper() in ("FAILED", "ERROR", "BLOCKED"):
        success = False

    store = load_learning()
    intent_rows = _intent_stats(store, intent)
    lvl_stats = intent_rows.setdefault(stack, {"success": 0, "fail": 0})
    if success:
        lvl_stats["success"] = int(lvl_stats.get("success") or 0) + 1
    else:
        lvl_stats["fail"] = int(lvl_stats.get("fail") or 0) + 1

    for c in compiled.get("cursor_prompt", {}).get("constraints") or []:
        ch = store.setdefault("constraint_hits", {}).setdefault(c, {"success": 0, "fail": 0})
        if success:
            ch["success"] = int(ch.get("success") or 0) + 1
        else:
            ch["fail"] = int(ch.get("fail") or 0) + 1

    pattern_key = f"{intent}|{stack}|{compiled.get('complexity', 0):.2f}"
    ps = store.setdefault("pattern_scores", {}).setdefault(pattern_key, {"success": 0, "fail": 0})
    if success:
        ps["success"] = int(ps.get("success") or 0) + 1
    else:
        ps["fail"] = int(ps.get("fail") or 0) + 1

    # Stack bias: reward successful stacks, penalize failed
    bias = store.setdefault("stack_bias", {lvl: 0.0 for lvl in STACK_LEVELS})
    delta = 0.05 if success else -0.03
    bias[stack] = round(float(bias.get(stack, 0.0)) + delta, 4)
    for lvl in STACK_LEVELS:
        bias[lvl] = round(max(-0.5, min(0.5, float(bias.get(lvl, 0.0)))), 4)

    run_row = {
        "id": run_id or f"plrun-{uuid.uuid4().hex[:10]}",
        "intent": intent,
        "stack": stack,
        "success": success,
        "state": execution_state,
        "verdict": quality_verdict,
        "at": _now(),
    }
    runs = store.setdefault("runs", [])
    runs.append(run_row)
    store["runs"] = runs[-MAX_RUN_HISTORY:]
    save_learning(store)

    return {"ok": True, "schema": SCHEMA, "recorded": run_row, "learning_samples": len(runs)}


def compile_prompt(
    *,
    raw: str,
    system_state: dict[str, Any] | None = None,
    workspace_path: str = "",
    adaptive: bool = True,
) -> dict[str, Any]:
    """Full v2 pipeline with optional adaptive routing (default on)."""
    raw = (raw or "").strip()
    if not raw:
        return {"ok": False, "error": "empty_input", "schema": SCHEMA}

    learning = load_learning()
    intent = parse_intent(raw)
    complexity = complexity_score(raw)

    if adaptive:
        stack, routing_meta = select_stack_adaptive(intent, complexity, learning)
        constraints, evolved = generate_constraints_adaptive(intent, learning)
    else:
        stack = select_stack(intent, complexity)
        routing_meta = {"baseline_stack": stack, "adaptive_applied": False}
        constraints = generate_constraints(intent)
        evolved = []

    state = system_state or _load_system_state()
    if workspace_path:
        state["workspace_path"] = workspace_path
    context = resolve_context(state)
    if workspace_path:
        context.append(f"Workspace: {workspace_path}")
    if adaptive and evolved:
        context.append(f"Adaptive constraints ({len(evolved)} learned)")

    prompt = build_prompt(raw=raw, context=context, constraints=constraints, stack=stack, intent=intent)
    task = to_forge_task(prompt)
    mission = build_cursor_mission(prompt)

    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": COMPILER_VERSION,
        "parent_schema": SCHEMA_V1,
        "adaptive": adaptive,
        "intent": intent,
        "complexity": complexity,
        "stackLevel": stack,
        "routing": routing_meta,
        "evolved_constraints": evolved,
        "cursor_prompt": prompt,
        "forge_task": task,
        "cursor_mission": mission,
        "executionMode": task.get("executionMode"),
        "estimatedCost": task.get("estimatedCost"),
        "learning_samples": len(learning.get("runs") or []),
        "system_state": state,
        "at": _now(),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def compile_and_dispatch_hint(*, raw: str, workspace_path: str = "", adaptive: bool = True) -> dict[str, Any]:
    compiled = compile_prompt(raw=raw, workspace_path=workspace_path, adaptive=adaptive)
    if not compiled.get("ok"):
        return compiled
    task = compiled.get("forge_task") or {}
    hint = task.get("api_hint") or {}
    return {
        **compiled,
        "dispatch_hint": {
            "action": hint.get("action", "advisor_run"),
            "goal": raw,
            "workspace_path": workspace_path,
            "swarm": hint.get("swarm", False),
            "dry_run": hint.get("dry_run", True),
            "stackLevel": compiled.get("stackLevel"),
            "adaptive": adaptive,
        },
    }


def seed_learning_demo() -> dict[str, Any]:
    """Seed minimal learning data for cold-start adaptive routing (idempotent)."""
    store = load_learning()
    if store.get("runs"):
        return {"ok": True, "seeded": False, "reason": "already_has_runs"}
    demo = {
        "feature_addition": {"L2": {"success": 8, "fail": 1}, "L1": {"success": 2, "fail": 3}},
        "optimization": {"L4": {"success": 5, "fail": 0}, "L3": {"success": 1, "fail": 2}},
        "swarm": {"L6": {"success": 4, "fail": 0}, "L5": {"success": 1, "fail": 1}},
    }
    for intent, stacks in demo.items():
        rows = _intent_stats(store, intent)
        for lvl, stats in stacks.items():
            rows[lvl] = stats
    store["constraint_hits"] = {
        "must support distributed parallel execution via swarm blackboard": {"success": 6, "fail": 0},
        "patch-only preferred — L2 self-heal policy": {"success": 5, "fail": 0},
    }
    save_learning(store)
    return {"ok": True, "seeded": True, "intents": list(demo.keys())}
