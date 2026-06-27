#!/usr/bin/env python3
"""Forge World System v6 — planetary simulation layer (coupled geo-nations)."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
WORLD_VECTOR = SINA / "forge-world-vector-v6.json"
RECEIPT = SINA / "forge-world-system-tick-latest-v6.json"
SCHEMA = "forge-world-system-v6"
VERSION = "6.0.0"


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_world_vector() -> dict[str, Any]:
    if WORLD_VECTOR.is_file():
        try:
            return json.loads(WORLD_VECTOR.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "schema": "forge-world-state-vector-v6",
        "time": 0,
        "globalGDP": 390.0,
        "globalStability": 0.83,
        "resourceMap": {"compute": 92.0, "data": 2800.0, "energy": 65.0},
        "conflictIndex": 0.1,
        "informationFlow": 0.6,
        "climatePressure": 0.15,
    }


def save_world_vector(vec: dict[str, Any]) -> None:
    vec["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    WORLD_VECTOR.write_text(json.dumps(vec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def propagate_conflict(nation_a: dict[str, Any], nation_b: dict[str, Any], world: dict[str, Any]) -> None:
    power_a = float(nation_a.get("powerIndex", 0)) + float(nation_a.get("economy", {}).get("gdp", 0))
    power_b = float(nation_b.get("powerIndex", 0)) + float(nation_b.get("economy", {}).get("gdp", 0))
    world["conflictIndex"] = round(float(world.get("conflictIndex", 0)) + abs(power_a - power_b) / 1000, 4)
    for n in world.get("nations_list") or []:
        allies = (n.get("foreignPolicy") or {}).get("alliances") or []
        if nation_a.get("id") in allies or nation_b.get("id") in allies:
            n["stabilityIndex"] = round(max(0.0, float(n.get("stabilityIndex", 0.8)) - 0.02), 3)


def spread_narrative(source: str, target: dict[str, Any], strength: float) -> None:
    info = target.setdefault("information", {"influenceScores": {}, "narratives": {}})
    info["influenceScores"][source] = round(float(info["influenceScores"].get(source, 0)) + strength, 3)
    if strength > 0.5:
        target["stabilityIndex"] = round(max(0.0, float(target.get("stabilityIndex", 0.8)) - 0.03), 3)


def world_system_tick(*, dry_run: bool = True) -> dict[str, Any]:
    from forge_digital_nation_v5 import digital_nation_tick, load_nations  # noqa: WPS433
    from forge_civilization_code_v4 import civilization_code_tick  # noqa: WPS433

    vec = load_world_vector()
    vec["time"] = int(vec.get("time") or 0) + 1

    nation_tick = digital_nation_tick(dry_run=dry_run)
    civ_tick = civilization_code_tick(dry_run=dry_run)
    nations_doc = load_nations()
    nations = nations_doc.get("nations") or []
    vec["nations_list"] = nations

    if len(nations) >= 2:
        propagate_conflict(nations[0], nations[1], vec)
        spread_narrative(str(nations[0].get("id")), nations[1], 0.3)

    vec["globalGDP"] = round(sum(float(n.get("economy", {}).get("gdp", 0)) for n in nations), 2)
    vec["globalStability"] = round(
        sum(float(n.get("stabilityIndex", 0.8)) for n in nations) / max(len(nations), 1),
        3,
    )
    vec["informationFlow"] = round(min(1.0, float(vec.get("informationFlow", 0.6)) + 0.01), 3)

    save_world_vector(vec)
    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "dry_run": dry_run,
        "world_vector": vec,
        "nation_tick": nation_tick,
        "civilization_code": civ_tick,
        "at": _now(),
    }
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
