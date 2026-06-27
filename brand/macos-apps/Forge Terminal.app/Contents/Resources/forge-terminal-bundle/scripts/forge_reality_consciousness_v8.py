#!/usr/bin/env python3
"""Forge Reality-Coupled Consciousness v8 — bind v7 to live receipts + cloud + founder session.

Couples planetary consciousness to disk truth: Mac control plane, autorun, cloud ticks.
Store: ~/.sina/forge-reality-consciousness-v8.json
Receipt: ~/.sina/forge-reality-consciousness-tick-latest-v8.json
Law: brain-os/law/enforcement/SOURCEA_FORGE_REALITY_CONSCIOUSNESS_V8_LOCKED_v1.md
"""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
REALITY_STORE = SINA / "forge-reality-consciousness-v8.json"
RECEIPT = SINA / "forge-reality-consciousness-tick-latest-v8.json"
SCHEMA = "forge-reality-consciousness-v8"
VERSION = "8.0.0"

REALITY_RECEIPTS: dict[str, Path] = {
    "mac_control_plane": SINA / "mac-control-plane-v1.flag",
    "cli_disabled": SINA / "cli-disabled-v1.flag",
    "brain_session": SINA / "brain_session_receipt_v1.json",
    "agent_session_gate": SINA / "agent_session_gate_receipt_v1.json",
    "cloud_auto_runtime_tick": SINA / "cloud-auto-runtime-tick-receipt-v1.json",
    "hub_cloud_proceed": SINA / "hub-cloud-forge-run-proceed-receipt-v1.json",
    "civilization_tick": SINA / "forge-civilization-tick-latest-v1.json",
    "planetary_consciousness": SINA / "forge-planetary-consciousness-tick-latest-v7.json",
    "forge_runtime": SINA / "forge-prompt-os-runtime-latest-v3.json",
    "governance_latest": SINA / "forge-governance-latest-v1.json",
    "cloud_forge_auto_flag": SINA / "cloud-forge-run-auto-proceed-v1.flag",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _flag_present(path: Path) -> bool:
    return path.is_file()


def _receipt_age_hours(path: Path) -> float | None:
    if not path.is_file():
        return None
    try:
        mtime = path.stat().st_mtime
        return round((datetime.now(timezone.utc).timestamp() - mtime) / 3600.0, 2)
    except OSError:
        return None


def load_reality_state() -> dict[str, Any]:
    if REALITY_STORE.is_file():
        try:
            return json.loads(REALITY_STORE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "schema": "forge-reality-consciousness-state-v8",
        "version": VERSION,
        "realityHealth": 0.5,
        "coupledAwareness": 0.5,
        "realityLog": [],
        "at": _now(),
    }


def save_reality_state(state: dict[str, Any]) -> dict[str, Any]:
    state["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    REALITY_STORE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return state


def collect_reality_signals() -> dict[str, Any]:
    """Read live disk receipts — Mac founder session + cloud autorun + Forge motor."""
    signals: dict[str, Any] = {
        "mac": {},
        "founder_session": {},
        "cloud": {},
        "forge_motor": {},
        "cycle_receipts": {},
    }

    signals["mac"] = {
        "control_plane": _flag_present(REALITY_RECEIPTS["mac_control_plane"]),
        "cli_disabled": _flag_present(REALITY_RECEIPTS["cli_disabled"]),
        "api_enabled": not _flag_present(SINA / "api-disabled-v1.flag"),
    }

    brain = _read_json(REALITY_RECEIPTS["brain_session"])
    gate = _read_json(REALITY_RECEIPTS["agent_session_gate"])
    signals["founder_session"] = {
        "brain_present": bool(brain),
        "brain_schema": brain.get("schema"),
        "gate_present": bool(gate),
        "gate_ok": gate.get("ok"),
        "gate_schema": gate.get("schema"),
        "role": gate.get("role") or brain.get("role"),
    }

    cloud_tick = _read_json(REALITY_RECEIPTS["cloud_auto_runtime_tick"])
    hub_proceed = _read_json(REALITY_RECEIPTS["hub_cloud_proceed"])
    signals["cloud"] = {
        "auto_runtime_tick_present": bool(cloud_tick),
        "auto_runtime_schema": cloud_tick.get("schema"),
        "auto_runtime_ok": cloud_tick.get("ok"),
        "tick_age_hours": _receipt_age_hours(REALITY_RECEIPTS["cloud_auto_runtime_tick"]),
        "hub_proceed_present": bool(hub_proceed),
        "hub_proceed_ok": hub_proceed.get("ok"),
        "auto_proceed_armed": _flag_present(REALITY_RECEIPTS["cloud_forge_auto_flag"]),
        "processed": (cloud_tick.get("pack") or {}).get("processed") if isinstance(cloud_tick.get("pack"), dict) else cloud_tick.get("processed"),
    }

    civ = _read_json(REALITY_RECEIPTS["civilization_tick"])
    runtime = _read_json(REALITY_RECEIPTS["forge_runtime"])
    gov = _read_json(REALITY_RECEIPTS["governance_latest"])
    signals["forge_motor"] = {
        "civilization_tick_ok": civ.get("ok"),
        "runtime_present": bool(runtime),
        "runtime_ok": runtime.get("ok"),
        "governance_status": gov.get("status"),
        "governance_version": gov.get("version"),
    }

    cycle_dir = SINA / "autonomous-forge-run-cycle-receipts"
    cycle_count = 0
    if cycle_dir.is_dir():
        cycle_count = sum(1 for p in cycle_dir.glob("*.json") if p.is_file())
    signals["cycle_receipts"] = {"count": cycle_count, "dir": str(cycle_dir)}

    return signals


def compute_reality_health(signals: dict[str, Any]) -> dict[str, Any]:
    """0–1 health from live receipt presence + freshness."""
    score = 0.0
    weights: list[tuple[float, bool]] = []

    mac = signals.get("mac") or {}
    weights.append((0.15, bool(mac.get("control_plane"))))
    weights.append((0.05, bool(mac.get("cli_disabled"))))

    founder = signals.get("founder_session") or {}
    weights.append((0.1, bool(founder.get("gate_present") or founder.get("brain_present"))))

    cloud = signals.get("cloud") or {}
    weights.append((0.25, bool(cloud.get("auto_runtime_tick_present"))))
    if cloud.get("auto_runtime_ok") is True:
        score += 0.1
    tick_age = cloud.get("tick_age_hours")
    if tick_age is not None and tick_age < 24:
        score += 0.05

    motor = signals.get("forge_motor") or {}
    weights.append((0.15, motor.get("governance_status") == "ALLOW" or bool(motor.get("runtime_present"))))

    cycles = signals.get("cycle_receipts") or {}
    if int(cycles.get("count") or 0) > 0:
        score += 0.05

    for w, ok in weights:
        if ok:
            score += w

    health = round(min(1.0, score), 4)
    stale_cloud = tick_age is not None and tick_age > 48
    status = "healthy"
    if health < 0.4:
        status = "degraded"
    elif stale_cloud:
        status = "stale_cloud"
    elif not mac.get("control_plane"):
        status = "mac_unarmed"

    return {
        "realityHealth": health,
        "status": status,
        "stale_cloud_tick": stale_cloud,
        "tick_age_hours": tick_age,
    }


def couple_awareness(*, v7_awareness: dict[str, Any], reality_health: dict[str, Any]) -> dict[str, Any]:
    """Blend simulated v7 awareness with live reality health."""
    sim = float(v7_awareness.get("awarenessIndex") or 0.5)
    real = float(reality_health.get("realityHealth") or 0.5)
    coupled = round(sim * 0.45 + real * 0.55, 4)
    coherence = round(
        float(v7_awareness.get("coherenceScore") or 0.5) * 0.5 + real * 0.5,
        4,
    )
    level = v7_awareness.get("level", "observing")
    if reality_health.get("status") == "degraded":
        level = "stabilizing"
    elif coupled >= 0.75 and reality_health.get("status") == "healthy":
        level = "coherent"
    return {
        "coupledAwareness": coupled,
        "coherenceScore": coherence,
        "level": level,
        "simulatedAwareness": sim,
        "realityHealth": real,
        "realityStatus": reality_health.get("status"),
    }


def generate_reality_thought(
    *,
    coupled: dict[str, Any],
    reality: dict[str, Any],
    signals: dict[str, Any],
) -> str:
    cloud = signals.get("cloud") or {}
    mac = signals.get("mac") or {}
    if reality.get("status") == "stale_cloud":
        return (
            f"Reality stale — cloud tick age {cloud.get('tick_age_hours')}h; "
            f"recommend Cloud Forge Run proceed or CF worker tick."
        )
    if not mac.get("control_plane"):
        return "Mac control plane flag absent — founder session may be unarmed."
    if coupled.get("level") == "coherent":
        proc = cloud.get("processed")
        return (
            f"Reality-coupled coherence {coupled.get('coupledAwareness')} — "
            f"Mac armed · cloud motor {'live' if cloud.get('auto_runtime_ok') else 'idle'}"
            + (f" · processed={proc}" if proc is not None else "")
            + "."
        )
    return (
        f"Coupled awareness {coupled.get('coupledAwareness')} · "
        f"reality {reality.get('status')} · monitoring autorun receipts."
    )


def reality_stabilize_actions(
    *,
    reality: dict[str, Any],
    signals: dict[str, Any],
    dry_run: bool = True,
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    cloud = signals.get("cloud") or {}

    if reality.get("stale_cloud_tick"):
        actions.append(
            {
                "action": "dispatch_cloud_auto_runtime_tick",
                "reason": "stale_cloud_receipt",
                "dry_run": dry_run,
                "hint": "POST hub /api/cloud-worker/dispatch or CF worker cron",
            }
        )

    if not cloud.get("auto_proceed_armed") and reality.get("realityHealth", 0) < 0.6:
        actions.append(
            {
                "action": "recommend_arm_auto_proceed",
                "flag": str(REALITY_RECEIPTS["cloud_forge_auto_flag"]),
                "dry_run": dry_run,
            }
        )

    mac = signals.get("mac") or {}
    if not mac.get("control_plane"):
        actions.append(
            {
                "action": "recommend_mac_control_plane",
                "script": "scripts/enter-mac-control-plane-v1.sh",
                "dry_run": dry_run,
            }
        )

    return actions


def reality_consciousness_tick(*, dry_run: bool = True, run_v7: bool = True) -> dict[str, Any]:
    """Full v8 cycle: v7 consciousness + reality signals + coupling."""
    from forge_planetary_consciousness_v7 import (  # noqa: WPS433
        collect_meta_signals,
        compute_awareness_index,
        planetary_consciousness_tick,
        self_stabilize,
    )

    v7_result = planetary_consciousness_tick(dry_run=dry_run, run_world=run_v7) if run_v7 else {}
    reality_signals = collect_reality_signals()
    reality_health = compute_reality_health(reality_signals)

    sim_signals = collect_meta_signals()
    v7_awareness = compute_awareness_index(sim_signals)
    if v7_result.get("awareness"):
        v7_awareness = v7_result["awareness"]

    coupled = couple_awareness(v7_awareness=v7_awareness, reality_health=reality_health)
    thought = generate_reality_thought(coupled=coupled, reality=reality_health, signals=reality_signals)
    reality_actions = reality_stabilize_actions(reality=reality_health, signals=reality_signals, dry_run=dry_run)

    sim_stabilization = v7_result.get("stabilization") or self_stabilize(
        awareness=v7_awareness, signals=sim_signals, dry_run=dry_run
    )

    state = load_reality_state()
    state["realityHealth"] = reality_health.get("realityHealth")
    state["coupledAwareness"] = coupled.get("coupledAwareness")
    state["realityStatus"] = reality_health.get("status")
    state["lastThought"] = thought
    state["realityActions"] = reality_actions
    log = state.setdefault("realityLog", [])
    log.append(
        {
            "id": f"rl-{uuid.uuid4().hex[:8]}",
            "thought": thought,
            "coupled": coupled.get("coupledAwareness"),
            "reality": reality_health.get("realityHealth"),
            "at": _now(),
        }
    )
    state["realityLog"] = log[-100:]
    save_reality_state(state)

    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "dry_run": dry_run,
        "coupled": coupled,
        "reality_health": reality_health,
        "reality_signals": reality_signals,
        "thought": thought,
        "reality_actions": reality_actions,
        "simulation_stabilization": sim_stabilization,
        "v7_tick": v7_result if run_v7 else {"skipped": True},
        "reality_state": state,
        "at": _now(),
    }
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def reality_consciousness_status() -> dict[str, Any]:
    reality_signals = collect_reality_signals()
    reality_health = compute_reality_health(reality_signals)
    state = load_reality_state()
    return {
        "ok": True,
        "schema": SCHEMA,
        "reality_health": reality_health,
        "reality_signals": reality_signals,
        "state": state,
        "at": _now(),
    }
