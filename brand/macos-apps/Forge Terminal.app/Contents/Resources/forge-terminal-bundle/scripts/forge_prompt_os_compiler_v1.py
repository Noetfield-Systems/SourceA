#!/usr/bin/env python3
"""Forge Prompt OS Compiler v1 — raw intent → structured Forge execution spec.

Bridge: Cursor Ask Mode ↔ Forge Kernel ↔ Swarm Execution
Receipt: ~/.sina/forge-prompt-os-compiler-latest-v1.json
Law: brain-os/law/enforcement/SOURCEA_FORGE_PROMPT_OS_COMPILER_LOCKED_v1.md
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-prompt-os-compiler-latest-v1.json"
SCHEMA = "forge-prompt-os-compiler-v1"
COMPILER_VERSION = "1.0.0"

StackLevel = Literal["L1", "L2", "L3", "L4", "L5", "L6", "L7"]
ExecutionMode = Literal["single", "swarm"]

STACK_COST: dict[str, float] = {
    "L1": 5.0,
    "L2": 8.0,
    "L3": 12.0,
    "L4": 15.0,
    "L5": 20.0,
    "L6": 35.0,
    "L7": 50.0,
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_system_state() -> dict[str, Any]:
    """Inject live Forge state for context resolver."""
    state: dict[str, Any] = {
        "forgeVersion": "4.0.0-alpha",
        "activeModules": [],
        "economy": None,
        "swarm": None,
        "governance": None,
    }
    try:
        from forge_terminal_connect_server_v1 import UI_VERSION  # noqa: WPS433

        state["forgeVersion"] = UI_VERSION
    except Exception:
        pass
    modules = [
        "forge_agent_kernel_v1",
        "forge_agent_kernel_v3_swarm",
        "forge_governance_kernel_v1",
        "forge_governance_legal_v3",
        "forge_geopolitical_legal_v4",
        "forge_economy_v1",
        "forge_civilization_memory_v1",
        "forge_prompt_os_compiler_v1",
        "forge_prompt_os_compiler_v2",
        "forge_prompt_os_compiler_v3",
    ]
    root = Path(__file__).resolve().parents[1] / "scripts"
    state["activeModules"] = [m for m in modules if (root / f"{m}.py").is_file()]
    try:
        from forge_economy_v1 import load_economy  # noqa: WPS433

        eco = load_economy()
        state["economy"] = {"enabled": True, "currency": eco.get("currency"), "accounts": len(eco.get("accounts") or {})}
    except Exception:
        state["economy"] = {"enabled": False}
    try:
        from forge_swarm_blackboard_v1 import load_blackboard  # noqa: WPS433

        bb = load_blackboard()
        state["swarm"] = {"active": bool(bb.get("goal")), "round": bb.get("round", 0)}
    except Exception:
        state["swarm"] = {"active": False}
    try:
        from forge_governance_kernel_v1 import GOVERNANCE_VERSION  # noqa: WPS433

        state["governance"] = GOVERNANCE_VERSION
    except Exception:
        state["governance"] = "v4"
    return state


def parse_intent(raw: str) -> str:
    text = (raw or "").lower()
    if any(k in text for k in ("architecture", "system design", "design module")):
        return "system_design"
    if any(k in text for k in ("convert", "migrate", "transform", "refactor")):
        return "transformation"
    if any(k in text for k in ("optimize", "performance", "faster", "cost")):
        return "optimization"
    if any(k in text for k in ("swarm", "parallel", "multi-agent", "distributed")):
        return "swarm"
    if any(k in text for k in ("add", "implement", "build", "create", "ship")):
        return "feature_addition"
    if any(k in text for k in ("fix", "repair", "heal", "debug")):
        return "repair"
    if any(k in text for k in ("deploy", "railway", "production")):
        return "deployment"
    return "general_build"


def complexity_score(raw: str) -> float:
    text = (raw or "").strip()
    score = min(len(text) / 400.0, 0.4)
    if re.search(r"\b(and|also|plus|then)\b", text, re.I):
        score += 0.15
    if re.search(r"\b(all|every|entire|full)\b", text, re.I):
        score += 0.1
    if text.count("\n") > 3:
        score += 0.1
    if any(k in text.lower() for k in ("microservice", "distributed", "swarm", "nation", "economy")):
        score += 0.25
    return round(min(score, 1.0), 3)


def select_stack(intent: str, complexity: float) -> StackLevel:
    if intent == "deployment" or complexity > 0.85:
        return "L7"
    if intent == "swarm" or complexity > 0.7:
        return "L6"
    if intent == "system_design" and complexity > 0.5:
        return "L5"
    if intent == "optimization":
        return "L4"
    if intent in ("transformation", "repair"):
        return "L3"
    if intent == "feature_addition":
        return "L2"
    if intent == "general_build":
        return "L1"
    return "L3"


def resolve_context(state: dict[str, Any] | None = None) -> list[str]:
    st = state or _load_system_state()
    lines = [
        f"Forge version: {st.get('forgeVersion', '?')}",
        f"Active modules: {', '.join(st.get('activeModules') or [])}",
        f"Governance: {st.get('governance', '?')}",
    ]
    eco = st.get("economy") or {}
    lines.append(f"Economy: {'enabled' if eco.get('enabled') else 'disabled'}")
    swarm = st.get("swarm") or {}
    lines.append(f"Swarm: {'active' if swarm.get('active') else 'idle'}")
    if swarm.get("round"):
        lines.append(f"Swarm round: {swarm.get('round')}")
    return lines


def generate_constraints(intent: str) -> list[str]:
    base = [
        "no breaking changes without explicit founder approval",
        "production-ready only — integrate with existing Forge kernel",
        "Mac founder session: dry_run default unless cloud armed",
        "pass governance kernel before tool execution",
        "verify output before marking done",
    ]
    if intent == "system_design":
        base.append("must support horizontal scaling and cloud dispatch")
    if intent == "swarm":
        base.append("must support distributed parallel execution via swarm blackboard")
    if intent == "deployment":
        base.append("deploy only via cloud — never Mac body")
    if intent == "repair":
        base.append("patch-only preferred — L2 self-heal policy")
    return base


def detect_transformation(raw: str) -> str:
    text = (raw or "").lower()
    if "convert" in text or "migrate" in text:
        return "migration"
    if "refactor" in text:
        return "refactor"
    if "add" in text or "implement" in text:
        return "feature_add"
    if "fix" in text:
        return "repair"
    return "build"


def infer_output_format(raw: str) -> str:
    text = (raw or "").lower()
    if "api" in text or "endpoint" in text:
        return "api_module"
    if "ui" in text or "frontend" in text or "terminal" in text:
        return "ui_component"
    if "doc" in text or "readme" in text:
        return "documentation"
    if "test" in text or "e2e" in text:
        return "test_suite"
    return "code_patch"


def build_prompt(
    *,
    raw: str,
    context: list[str],
    constraints: list[str],
    stack: StackLevel,
    intent: str,
) -> dict[str, Any]:
    return {
        "goal": (raw or "").strip(),
        "context": context,
        "constraints": constraints,
        "transformationType": detect_transformation(raw),
        "outputFormat": infer_output_format(raw),
        "acceptanceCriteria": [
            "runs without modification in open workspace",
            "integrates with Forge kernel and governance v2",
            "passes verify harness or living E2E where applicable",
            f"appropriate stack level {stack} execution path",
        ],
        "stackLevel": stack,
        "intent": intent,
    }


def calculate_priority(prompt: dict[str, Any]) -> int:
    stack = prompt.get("stackLevel") or "L3"
    base = {"L1": 3, "L2": 4, "L3": 5, "L4": 6, "L5": 7, "L6": 8, "L7": 9}.get(stack, 5)
    if prompt.get("intent") == "repair":
        base += 2
    return min(base, 10)


def estimate_cost(prompt: dict[str, Any]) -> float:
    stack = str(prompt.get("stackLevel") or "L3")
    return float(STACK_COST.get(stack, 12.0))


def execution_mode_for_stack(stack: StackLevel) -> ExecutionMode:
    if stack in ("L5", "L6", "L7"):
        return "swarm"
    return "single"


def to_forge_task(prompt: dict[str, Any]) -> dict[str, Any]:
    stack = prompt.get("stackLevel") or "L3"
    mode = execution_mode_for_stack(stack)  # type: ignore[arg-type]
    return {
        "id": f"ftask-{uuid.uuid4().hex[:10]}",
        "prompt": prompt,
        "executionMode": mode,
        "priority": calculate_priority(prompt),
        "estimatedCost": estimate_cost(prompt),
        "api_hint": {
            "action": "advisor_run" if mode == "swarm" else "agent_dev_loop",
            "swarm": mode == "swarm",
            "dry_run": True,
        },
    }


def build_cursor_mission(prompt: dict[str, Any]) -> str:
    """Human/Cursor-ready mission block."""
    lines = [
        f"GOAL: {prompt.get('goal', '')}",
        "",
        "CONTEXT:",
    ]
    for c in prompt.get("context") or []:
        lines.append(f"- {c}")
    lines.extend(["", "CONSTRAINTS:"])
    for c in prompt.get("constraints") or []:
        lines.append(f"- {c}")
    lines.extend(
        [
            "",
            f"STACK: {prompt.get('stackLevel')} · {prompt.get('transformationType')} → {prompt.get('outputFormat')}",
            "",
            "ACCEPTANCE:",
        ]
    )
    for a in prompt.get("acceptanceCriteria") or []:
        lines.append(f"- {a}")
    return "\n".join(lines)


def compile_prompt(
    *,
    raw: str,
    system_state: dict[str, Any] | None = None,
    workspace_path: str = "",
) -> dict[str, Any]:
    """Full pipeline: intent → stack → context → constraints → prompt → forge task."""
    raw = (raw or "").strip()
    if not raw:
        return {"ok": False, "error": "empty_input", "schema": SCHEMA}

    intent = parse_intent(raw)
    complexity = complexity_score(raw)
    stack = select_stack(intent, complexity)
    state = system_state or _load_system_state()
    if workspace_path:
        state["workspace_path"] = workspace_path
    context = resolve_context(state)
    if workspace_path:
        context.append(f"Workspace: {workspace_path}")
    constraints = generate_constraints(intent)
    prompt = build_prompt(raw=raw, context=context, constraints=constraints, stack=stack, intent=intent)
    task = to_forge_task(prompt)
    mission = build_cursor_mission(prompt)

    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": COMPILER_VERSION,
        "intent": intent,
        "complexity": complexity,
        "stackLevel": stack,
        "cursor_prompt": prompt,
        "forge_task": task,
        "cursor_mission": mission,
        "executionMode": task.get("executionMode"),
        "estimatedCost": task.get("estimatedCost"),
        "system_state": state,
        "at": _now(),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def compile_and_dispatch_hint(*, raw: str, workspace_path: str = "") -> dict[str, Any]:
    """Compile + return API body hint for forge_terminal handle_post."""
    compiled = compile_prompt(raw=raw, workspace_path=workspace_path)
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
        },
    }
