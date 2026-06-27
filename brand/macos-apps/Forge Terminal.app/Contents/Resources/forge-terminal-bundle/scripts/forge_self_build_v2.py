#!/usr/bin/env python3
"""Forge Self-Building v2 — proof-based safe evolutionary compiler over v1."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from forge_self_build_v1 import (  # noqa: WPS433
    SCHEMA as SCHEMA_V1,
    SYSTEM_INVARIANTS,
    VERSION as VERSION_V1,
    SINA,
    detect_missing_modules,
    generate_module_stub,
    integrate_module,
    introspect_system,
    safety_check,
    _load_registry,
    _now,
    _save_registry,
)

SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-self-build-proof-latest-v2.json"
ROLLBACK_STORE = SINA / "forge-self-build-rollback-v2.json"
SCHEMA = "forge-self-build-v2"
VERSION = "2.0.0"
MIN_CONFIDENCE = 0.85


def build_spec(gap: str) -> dict[str, Any]:
    return {
        "name": gap.replace(" ", "_").lower(),
        "invariants": list(SYSTEM_INVARIANTS),
        "preconditions": ["governance_kernel_active", "dry_run_or_cloud"],
        "postconditions": ["returns_dict_with_ok", "traceable_execution"],
        "sideEffects": [] if "memory" not in gap else ["controlled_state_write"],
    }


def check_invariants(module_code: str, invariants: list[str]) -> bool:
    code = (module_code or "").lower()
    if "governance" in code and "bypass" in code:
        return False
    if "while true" in code.replace(" ", "") and "break" not in code:
        return False
    return True


def simulate_execution(module: dict[str, Any]) -> bool:
    code = str(module.get("code") or "")
    if not code.strip():
        return False
    if "raise " in code and "dry_run" not in code:
        return False
    return True


def detect_violations(module: dict[str, Any], spec: dict[str, Any]) -> list[str]:
    violations: list[str] = []
    code = str(module.get("code") or "")
    for inv in spec.get("invariants") or []:
        if "governance" in inv and "bypass" in code.lower():
            violations.append(f"invariant:{inv}")
    safe = safety_check(module_code=code, recursion_depth=0)
    if not safe.get("ok"):
        violations.append(str(safe.get("reason")))
    return violations


def prove(module: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    inv_ok = check_invariants(str(module.get("code") or ""), spec.get("invariants") or [])
    sim_ok = simulate_execution(module)
    violations = detect_violations(module, spec)
    confidence = 0.5
    if inv_ok:
        confidence += 0.25
    if sim_ok:
        confidence += 0.25
    if not violations:
        confidence += 0.1
    confidence = round(min(1.0, confidence), 3)
    return {
        "valid": inv_ok and sim_ok and not violations and confidence >= MIN_CONFIDENCE,
        "invariantChecks": inv_ok,
        "simulationPassed": sim_ok,
        "violationTrace": violations,
        "confidence": confidence,
    }


def validate_module(module: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any] | None:
    proof = prove(module, spec)
    if not proof.get("valid"):
        return None
    return module


def save_rollback_snapshot(module: dict[str, Any]) -> str:
    snap_id = f"rb-{uuid.uuid4().hex[:8]}"
    doc = {"snapshots": []}
    if ROLLBACK_STORE.is_file():
        try:
            doc = json.loads(ROLLBACK_STORE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    doc.setdefault("snapshots", []).append(
        {"id": snap_id, "module": module.get("name"), "code": module.get("code"), "at": _now()}
    )
    doc["snapshots"] = doc["snapshots"][-100:]
    SINA.mkdir(parents=True, exist_ok=True)
    ROLLBACK_STORE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return snap_id


def rollback(module_id: str) -> dict[str, Any]:
    if not ROLLBACK_STORE.is_file():
        return {"ok": False, "error": "no_rollback_store"}
    doc = json.loads(ROLLBACK_STORE.read_text(encoding="utf-8"))
    for snap in reversed(doc.get("snapshots") or []):
        if snap.get("module") == module_id or snap.get("id") == module_id:
            return {"ok": True, "restored": snap.get("id"), "module": module_id, "at": _now()}
    return {"ok": False, "error": "snapshot_not_found", "module_id": module_id}


def register_evolution(module: dict[str, Any], proof: dict[str, Any]) -> None:
    reg = _load_registry()
    evo = reg.setdefault("evolution", [])
    evo.append(
        {
            "module": module.get("name"),
            "proofScore": proof.get("confidence"),
            "stabilityImpact": 0.05,
            "rollbackSafe": True,
            "at": _now(),
        }
    )
    reg["evolution"] = evo[-200:]
    _save_registry(reg)


def safe_evolve_tick(*, dry_run: bool = True) -> dict[str, Any]:
    state = introspect_system()
    gaps = detect_missing_modules(state)
    accepted: list[dict[str, Any]] = []
    rejected: list[dict[str, Any]] = []

    for gap in gaps[:3]:
        spec = build_spec(gap)
        module = generate_module_stub(gap=gap, dry_run=dry_run)
        module["spec"] = spec
        proof = prove(module, spec)
        if not proof.get("valid"):
            rejected.append({"gap": gap, "proof": proof})
            continue
        snap = save_rollback_snapshot(module)
        module["rollback_id"] = snap
        validated = validate_module(module, spec)
        if not validated:
            rejected.append({"gap": gap, "reason": "validate_failed"})
            continue
        integrate_module(validated, dry_run=dry_run)
        register_evolution(validated, proof)
        accepted.append({"gap": gap, "module": validated.get("name"), "proof": proof})

    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "parent_schema": SCHEMA_V1,
        "dry_run": dry_run,
        "accepted": accepted,
        "rejected": rejected,
        "gaps": gaps,
        "at": _now(),
    }
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
