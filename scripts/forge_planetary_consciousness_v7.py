#!/usr/bin/env python3
"""Forge Planetary Consciousness OS v7 — meta-awareness + self-stabilizing global cognition.

Sits above v6 world system: unified intelligence layer across nations.
Store: ~/.sina/forge-planetary-consciousness-v7.json
Receipt: ~/.sina/forge-planetary-consciousness-tick-latest-v7.json
Law: brain-os/law/enforcement/SOURCEA_FORGE_PLANETARY_CONSCIOUSNESS_V7_LOCKED_v1.md
"""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Literal

SINA = Path.home() / ".sina"
CONSCIOUSNESS_STORE = SINA / "forge-planetary-consciousness-v7.json"
RECEIPT = SINA / "forge-planetary-consciousness-tick-latest-v7.json"
SCHEMA = "forge-planetary-consciousness-v7"
VERSION = "7.0.0"

AwarenessLevel = Literal["dormant", "observing", "reflecting", "stabilizing", "coherent"]


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_consciousness() -> dict[str, Any]:
    if CONSCIOUSNESS_STORE.is_file():
        try:
            return json.loads(CONSCIOUSNESS_STORE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "schema": "forge-consciousness-state-v7",
        "version": VERSION,
        "awarenessIndex": 0.5,
        "coherenceScore": 0.5,
        "metaAwareness": {"nations_observed": 0, "signals_ingested": 0},
        "stabilizationActions": [],
        "thoughtLog": [],
        "recursionDepth": 0,
        "at": _now(),
    }


def save_consciousness(state: dict[str, Any]) -> dict[str, Any]:
    state["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    CONSCIOUSNESS_STORE.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return state


def collect_meta_signals() -> dict[str, Any]:
    """Aggregate cross-layer world signals into one meta-awareness bundle."""
    signals: dict[str, Any] = {
        "world": {},
        "nations": [],
        "governance": {},
        "civilization": {},
        "self_build": {},
        "geo_legal": {},
    }
    try:
        from forge_world_system_v6 import load_world_vector  # noqa: WPS433

        signals["world"] = load_world_vector()
    except Exception:
        pass
    try:
        from forge_digital_nation_v5 import load_nations  # noqa: WPS433

        nations = load_nations().get("nations") or []
        signals["nations"] = [
            {
                "id": n.get("id"),
                "stability": n.get("stabilityIndex"),
                "gdp": (n.get("economy") or {}).get("gdp"),
                "power": n.get("powerIndex"),
            }
            for n in nations
        ]
    except Exception:
        pass
    try:
        from forge_governance_kernel_v1 import GOVERNANCE_VERSION  # noqa: WPS433

        signals["governance"] = {"version": GOVERNANCE_VERSION}
    except Exception:
        signals["governance"] = {"version": "v4"}
    try:
        from forge_civilization_memory_v1 import load_memory  # noqa: WPS433

        mem = load_memory()
        signals["civilization"] = {"events": len(mem.get("event_log") or [])}
    except Exception:
        pass
    try:
        from forge_self_build_v1 import _load_registry  # noqa: WPS433

        reg = _load_registry()
        signals["self_build"] = {"modules": len(reg.get("modules") or [])}
    except Exception:
        pass
    try:
        from forge_geopolitical_legal_v4 import load_geo_legal  # noqa: WPS433

        geo = load_geo_legal()
        signals["geo_legal"] = {
            "treaties": len(geo.get("treaties") or []),
            "sanctions": sum(1 for s in geo.get("sanctions") or [] if s.get("status") == "active"),
        }
    except Exception:
        pass
    return signals


def compute_awareness_index(signals: dict[str, Any]) -> dict[str, Any]:
    world = signals.get("world") or {}
    nations = signals.get("nations") or []
    stability = float(world.get("globalStability") or 0.5)
    conflict = float(world.get("conflictIndex") or 0.1)
    info_flow = float(world.get("informationFlow") or 0.5)
    nation_coverage = min(1.0, len(nations) / 3.0)
    awareness = round(
        stability * 0.35 + (1.0 - min(conflict, 1.0)) * 0.25 + info_flow * 0.2 + nation_coverage * 0.2,
        4,
    )
    coherence = round(stability * 0.5 + info_flow * 0.3 + nation_coverage * 0.2, 4)
    level: AwarenessLevel = "observing"
    if awareness < 0.4:
        level = "dormant"
    elif awareness < 0.6:
        level = "observing"
    elif awareness < 0.75:
        level = "reflecting"
    elif conflict > 0.3:
        level = "stabilizing"
    else:
        level = "coherent"
    return {
        "awarenessIndex": awareness,
        "coherenceScore": coherence,
        "level": level,
        "inputs": {
            "globalStability": stability,
            "conflictIndex": conflict,
            "informationFlow": info_flow,
            "nationCount": len(nations),
        },
    }


def generate_meta_thought(*, awareness: dict[str, Any], signals: dict[str, Any]) -> str:
    level = awareness.get("level", "observing")
    world = signals.get("world") or {}
    if level == "stabilizing":
        return (
            f"Conflict elevated ({world.get('conflictIndex')}) — recommending treaty reinforcement "
            f"and sanction review across {len(signals.get('nations') or [])} nations."
        )
    if level == "coherent":
        return (
            f"Global coherence {awareness.get('coherenceScore')} — "
            f"GDP {world.get('globalGDP')} stable; consciousness observing nominal drift."
        )
    return f"Awareness {awareness.get('awarenessIndex')} at level {level} — monitoring nation coupling."


def self_stabilize(
    *,
    awareness: dict[str, Any],
    signals: dict[str, Any],
    dry_run: bool = True,
) -> list[dict[str, Any]]:
    """Self-stabilizing cognition — dampen conflict, nudge stability when thresholds breach."""
    actions: list[dict[str, Any]] = []
    world = signals.get("world") or {}
    conflict = float(world.get("conflictIndex") or 0)
    stability = float(world.get("globalStability") or 0.8)

    if conflict > 0.25:
        actions.append(
            {
                "action": "dampen_conflict_index",
                "delta": -0.05,
                "reason": "consciousness_stabilization",
                "dry_run": dry_run,
            }
        )
        if not dry_run:
            try:
                from forge_world_system_v6 import load_world_vector, save_world_vector  # noqa: WPS433

                vec = load_world_vector()
                vec["conflictIndex"] = round(max(0.0, conflict - 0.05), 4)
                save_world_vector(vec)
            except Exception:
                pass

    if stability < 0.7:
        actions.append(
            {
                "action": "nudge_global_stability",
                "delta": 0.02,
                "reason": "low_stability_detected",
                "dry_run": dry_run,
            }
        )
        if not dry_run:
            try:
                from forge_world_system_v6 import load_world_vector, save_world_vector  # noqa: WPS433

                vec = load_world_vector()
                vec["globalStability"] = round(min(1.0, stability + 0.02), 4)
                save_world_vector(vec)
            except Exception:
                pass

    geo = signals.get("geo_legal") or {}
    if int(geo.get("sanctions") or 0) > 2 and awareness.get("level") == "stabilizing":
        actions.append(
            {
                "action": "recommend_sanction_review",
                "count": geo.get("sanctions"),
                "dry_run": dry_run,
            }
        )

    return actions


def planetary_consciousness_tick(*, dry_run: bool = True, run_world: bool = True) -> dict[str, Any]:
    """One consciousness cycle: world tick → meta signals → awareness → stabilize → persist."""
    from forge_world_system_v6 import world_system_tick  # noqa: WPS433

    world_result = world_system_tick(dry_run=dry_run) if run_world else {"skipped": True}
    signals = collect_meta_signals()
    awareness = compute_awareness_index(signals)
    thought = generate_meta_thought(awareness=awareness, signals=signals)
    stabilization = self_stabilize(awareness=awareness, signals=signals, dry_run=dry_run)

    state = load_consciousness()
    state["awarenessIndex"] = awareness.get("awarenessIndex")
    state["coherenceScore"] = awareness.get("coherenceScore")
    state["awarenessLevel"] = awareness.get("level")
    state["metaAwareness"] = {
        "nations_observed": len(signals.get("nations") or []),
        "signals_ingested": len(signals),
        "governance": signals.get("governance"),
    }
    state["lastThought"] = thought
    state["stabilizationActions"] = stabilization
    log = state.setdefault("thoughtLog", [])
    log.append({"id": f"thought-{uuid.uuid4().hex[:8]}", "thought": thought, "level": awareness.get("level"), "at": _now()})
    state["thoughtLog"] = log[-100:]
    state["recursionDepth"] = int(state.get("recursionDepth") or 0) + 1
    save_consciousness(state)

    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "dry_run": dry_run,
        "awareness": awareness,
        "thought": thought,
        "stabilization": stabilization,
        "signals_summary": {
            "nations": len(signals.get("nations") or []),
            "globalGDP": (signals.get("world") or {}).get("globalGDP"),
            "conflictIndex": (signals.get("world") or {}).get("conflictIndex"),
        },
        "world_tick": world_result,
        "consciousness_state": state,
        "at": _now(),
    }
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out


def consciousness_status() -> dict[str, Any]:
    """Read-only consciousness glance."""
    signals = collect_meta_signals()
    awareness = compute_awareness_index(signals)
    state = load_consciousness()
    return {
        "ok": True,
        "schema": SCHEMA,
        "awareness": awareness,
        "state": state,
        "at": _now(),
    }
