#!/usr/bin/env python3
"""Forge World State v1 — v6 geopolitical simulation stub (dry_run, Mac-safe).

Multi-nation world model for future cloud simulation — NOT production geopolitics.
Receipt: ~/.sina/forge-world-state-v1.json
"""
from __future__ import annotations

import json
import random
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
WORLD_PATH = SINA / "forge-world-state-v1.json"
TICK_RECEIPT = SINA / "forge-world-tick-latest-v1.json"

SEED_NATIONS: list[dict[str, Any]] = [
    {
        "id": "nation-sourcea",
        "name": "SourceA Mac Control Plane",
        "ideology": "governed_automation",
        "economy": {"gdp": 100.0, "currency": 1000.0, "inflation": 0.02},
        "population": 13,
        "resources": {"compute": 2.0, "data": 500.0, "energy": 10.0, "influence": 0.6},
        "stability": 0.85,
        "alliances": ["nation-cloudforge"],
    },
    {
        "id": "nation-cloudforge",
        "name": "Cloud Forge Railway",
        "ideology": "execution_body",
        "economy": {"gdp": 250.0, "currency": 5000.0, "inflation": 0.01},
        "population": 100,
        "resources": {"compute": 80.0, "data": 2000.0, "energy": 50.0, "influence": 0.7},
        "stability": 0.9,
        "alliances": ["nation-sourcea", "nation-labs"],
    },
    {
        "id": "nation-labs",
        "name": "Labs Sandbox",
        "ideology": "experimentation",
        "economy": {"gdp": 40.0, "currency": 500.0, "inflation": 0.03},
        "population": 5,
        "resources": {"compute": 10.0, "data": 300.0, "energy": 5.0, "influence": 0.3},
        "stability": 0.75,
        "alliances": ["nation-cloudforge"],
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_world() -> dict[str, Any]:
    try:
        doc = json.loads(WORLD_PATH.read_text(encoding="utf-8"))
        if doc.get("nations"):
            return doc
    except (OSError, json.JSONDecodeError):
        pass
    nations = {n["id"]: dict(n) for n in SEED_NATIONS}
    return {
        "schema": "forge-world-state-v1",
        "time": 0,
        "nations": nations,
        "events": [],
        "global_markets": {"compute_price": 1.0, "data_price": 0.5, "crash_risk": 0.1},
        "diplomacy_graph": {"edges": []},
        "at": _now(),
    }


def save_world(world: dict[str, Any]) -> None:
    world["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    WORLD_PATH.write_text(json.dumps(world, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def generate_events(world: dict[str, Any]) -> list[dict[str, Any]]:
    """Light event generator for simulation tick."""
    events: list[dict[str, Any]] = []
    t = int(world.get("time") or 0)
    if t % 5 == 0:
        events.append({"type": "tech_breakthrough", "nation": "nation-cloudforge", "impact": 0.05})
    if random.random() < 0.15:
        ids = list((world.get("nations") or {}).keys())
        if len(ids) >= 2:
            events.append({"type": "treaty", "nations": ids[:2], "impact": 0.02})
    if random.random() < 0.08:
        events.append({"type": "economic_shock", "impact": -0.03})
    return events


def world_governor(world: dict[str, Any]) -> dict[str, Any]:
    markets = world.get("global_markets") or {}
    if float(markets.get("crash_risk") or 0) > 0.7:
        markets["crash_risk"] = 0.4
        world.setdefault("events", []).append({"type": "stabilization", "source": "world_governor"})
    world["global_markets"] = markets
    return world


def simulate_nation_step(nation: dict[str, Any], world: dict[str, Any]) -> None:
    nation["resources"]["data"] = round(float(nation["resources"].get("data") or 0) * 1.001, 2)
    if nation.get("stability", 0) < 0.3:
        nation["stability"] = round(min(1.0, float(nation.get("stability") or 0) + 0.05), 3)


def world_tick(*, dry_run: bool = True) -> dict[str, Any]:
    """One world simulation step — Mac-safe stub."""
    world = load_world()
    world["time"] = int(world.get("time") or 0) + 1
    world = world_governor(world)
    events = generate_events(world)
    world.setdefault("events", []).extend(events)
    world["events"] = world["events"][-100:]

    for nid, nation in (world.get("nations") or {}).items():
        if dry_run:
            nation["_last_tick"] = "dry_run_stub"
        else:
            simulate_nation_step(nation, world)

    save_world(world)
    out = {
        "ok": True,
        "schema": "forge-world-tick-v1",
        "dry_run": dry_run,
        "time": world["time"],
        "events_this_tick": len(events),
        "nations": len(world.get("nations") or {}),
        "tick_id": f"world-{uuid.uuid4().hex[:8]}",
        "at": _now(),
    }
    TICK_RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
