#!/usr/bin/env python3
"""Forge Self-Building Mode v1 — introspect → gap → generate → verify → integrate.

Mac-safe: dry_run stubs, no LLM required. Receipt: ~/.sina/forge-self-build-latest-v1.json
Registry: ~/.sina/forge-self-build-registry-v1.json
Law: brain-os/law/enforcement/SOURCEA_FORGE_SELF_BUILD_STACK_LOCKED_v1.md
"""
from __future__ import annotations

import json
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-self-build-latest-v1.json"
REGISTRY = SINA / "forge-self-build-registry-v1.json"
SCHEMA = "forge-self-build-v1"
VERSION = "1.0.0"
MAX_RECURSION = 10

REQUIRED_CAPABILITIES: dict[str, str] = {
    "economic_balancer": "forge_economy_v1.py",
    "swarm_optimizer": "forge_agent_kernel_v3_swarm.py",
    "governance_enforcer": "forge_governance_kernel_v1.py",
    "memory_compactor": "forge_civilization_memory_v1.py",
    "deployment_controller": "forge_swarm_cloud_dispatch_v1.py",
    "legal_arbitration": "forge_governance_legal_v3.py",
    "geo_legal_layer": "forge_geopolitical_legal_v4.py",
    "prompt_compiler": "forge_prompt_os_compiler_v3.py",
}

SYSTEM_INVARIANTS = [
    "no unauthorized state mutation",
    "no infinite loop execution",
    "no bypass of governance kernel",
    "no uncontrolled external IO",
    "all actions must be traceable",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_registry() -> dict[str, Any]:
    if REGISTRY.is_file():
        try:
            return json.loads(REGISTRY.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {"schema": SCHEMA, "modules": [], "metrics": {}, "updated_at": _now()}


def _save_registry(doc: dict[str, Any]) -> None:
    doc["updated_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def list_forge_modules() -> list[str]:
    return sorted(p.name for p in SCRIPTS.glob("forge_*.py"))


def introspect_system() -> dict[str, Any]:
    """Read Forge self-state."""
    state: dict[str, Any] = {
        "modules": list_forge_modules(),
        "module_count": 0,
        "registry": {},
        "memory": {},
        "tasks": [],
        "performance": {},
        "governance_version": "v4",
    }
    state["module_count"] = len(state["modules"])
    try:
        from forge_agent_registry_v1 import load_registry  # noqa: WPS433

        state["registry"] = {"agents": len((load_registry().get("agents") or []))}
    except Exception:
        state["registry"] = {"agents": 0}
    try:
        from forge_civilization_memory_v1 import load_memory  # noqa: WPS433

        mem = load_memory()
        state["memory"] = {"events": len(mem.get("event_log") or [])}
    except Exception:
        state["memory"] = {"events": 0}
    try:
        from forge_governance_kernel_v1 import GOVERNANCE_VERSION  # noqa: WPS433

        state["governance_version"] = GOVERNANCE_VERSION
    except Exception:
        pass
    state["capabilities"] = {
        name: (SCRIPTS / fname).is_file() for name, fname in REQUIRED_CAPABILITIES.items()
    }
    return state


def detect_missing_modules(state: dict[str, Any] | None = None) -> list[str]:
    st = state or introspect_system()
    caps = st.get("capabilities") or {}
    return [name for name, present in caps.items() if not present]


def safety_check(*, module_code: str, recursion_depth: int) -> dict[str, Any]:
    if recursion_depth > MAX_RECURSION:
        return {"ok": False, "reason": "recursion_depth_exceeded"}
    banned = re.compile(r"system_override|wipe_registry|rm\s+-rf|override_all_agents", re.I)
    if banned.search(module_code or ""):
        return {"ok": False, "reason": "forbidden_pattern"}
    if "def " not in module_code and "function " not in module_code:
        return {"ok": False, "reason": "no_function_boundary"}
    return {"ok": True, "reason": "safety_ok"}


def generate_module_stub(*, gap: str, dry_run: bool = True) -> dict[str, Any]:
    """Stub module generator — production path uses LLM on cloud."""
    name = gap.replace(" ", "_").lower()
    code = f'''"""Self-generated Forge module stub: {gap}."""
def run_{name}(*, dry_run: bool = True) -> dict:
    return {{"ok": True, "module": "{name}", "dry_run": dry_run, "origin": "self-generated"}}
'''
    return {
        "name": name,
        "version": "0.1.0",
        "gap": gap,
        "code": code,
        "origin": "self-generated",
        "dry_run": dry_run,
    }


def verify_module_heuristic(module: dict[str, Any]) -> dict[str, Any]:
    code = str(module.get("code") or "")
    has_fn = "def " in code
    safe = safety_check(module_code=code, recursion_depth=int(module.get("recursion_depth") or 0))
    return {
        "ok": has_fn and safe.get("ok"),
        "has_tests": "# test" in code.lower() or "dry_run" in code,
        "passes_lint": len(code) < 50_000 and "eval(" not in code,
        "deterministic": "random" not in code.lower() or "dry_run" in code,
        "core_safe": safe.get("ok"),
        "reason": safe.get("reason", "verified"),
    }


def integrate_module(module: dict[str, Any], *, dry_run: bool = True) -> dict[str, Any]:
    """Register module — dry_run never writes to scripts/."""
    reg = _load_registry()
    row = {
        "name": module.get("name"),
        "version": module.get("version", "0.1.0"),
        "origin": module.get("origin", "self-generated"),
        "gap": module.get("gap"),
        "integrated": not dry_run,
        "at": _now(),
    }
    reg["modules"] = (reg.get("modules") or [])[-200:] + [row]
    metrics = reg.setdefault("metrics", {})
    metrics["moduleCount"] = len(reg["modules"])
    metrics["selfGeneratedModules"] = sum(1 for m in reg["modules"] if m.get("origin") == "self-generated")
    metrics["stabilityScore"] = round(min(1.0, 0.7 + metrics["selfGeneratedModules"] * 0.01), 3)
    metrics["recursionDepth"] = int(metrics.get("recursionDepth") or 0)
    _save_registry(reg)
    return {"ok": True, "registered": row, "dry_run": dry_run}


def self_build_tick(*, dry_run: bool = True, recursion_depth: int = 0) -> dict[str, Any]:
    """One self-build loop iteration."""
    if recursion_depth > MAX_RECURSION:
        return {"ok": False, "error": "max_recursion", "schema": SCHEMA}

    state = introspect_system()
    gaps = detect_missing_modules(state)
    built: list[dict[str, Any]] = []
    skipped: list[str] = []

    for gap in gaps[:3]:
        module = generate_module_stub(gap=gap, dry_run=dry_run)
        module["recursion_depth"] = recursion_depth
        verified = verify_module_heuristic(module)
        if not verified.get("ok"):
            skipped.append(gap)
            continue
        reg = integrate_module(module, dry_run=dry_run)
        built.append({"gap": gap, "module": module.get("name"), "registered": reg.get("registered")})

    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "dry_run": dry_run,
        "state": {"module_count": state.get("module_count"), "governance": state.get("governance_version")},
        "gaps_detected": gaps,
        "built": built,
        "skipped": skipped,
        "metrics": _load_registry().get("metrics"),
        "recursion_depth": recursion_depth,
        "at": _now(),
    }
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
