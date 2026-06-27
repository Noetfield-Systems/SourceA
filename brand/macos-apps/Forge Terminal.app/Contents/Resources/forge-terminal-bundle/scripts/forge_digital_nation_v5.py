#!/usr/bin/env python3
"""Forge Digital Nation OS v5 — sovereign nations with constitution, GDP, diplomacy."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
NATION_STORE = SINA / "forge-digital-nation-v5.json"
RECEIPT = SINA / "forge-digital-nation-tick-latest-v5.json"
SCHEMA = "forge-digital-nation-v5"
VERSION = "5.0.0"


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _nation_from_world(nid: str, world_nation: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": nid,
        "constitution": {
            "laws": ["no unauthorized system override", "all actions traceable", "economic balance preserved"],
            "amendmentPolicy": {"threshold": 0.67, "votingSystem": "MERITOCRACY"},
            "immutableRules": ["governance_kernel_v4_active"],
        },
        "government": {
            "type": "technocracy" if nid == "nation-cloudforge" else "hybrid",
            "executiveAgents": ["builder-001"],
            "legislativeAgents": ["planner-001"],
            "judiciaryAgents": ["critic-001"],
            "decisionEngine": "forge_governance_legal_v3",
        },
        "economy": {
            "gdp": float(world_nation.get("economy", {}).get("gdp", 100)),
            "inflation": float(world_nation.get("economy", {}).get("inflation", 0.02)),
            "treasury": float(world_nation.get("economy", {}).get("currency", 1000)),
            "taxRate": 0.05,
            "tradeBalance": 0.0,
        },
        "currency": {
            "name": f"FORGE-{nid.split('-')[-1].upper()}",
            "supply": float(world_nation.get("economy", {}).get("currency", 1000)),
            "exchangeRates": {},
        },
        "foreignPolicy": {
            "alliances": list(world_nation.get("alliances") or []),
            "enemies": [],
            "neutral": [],
            "sanctions": {},
            "tradeAgreements": [],
        },
        "stabilityIndex": float(world_nation.get("stability", 0.8)),
        "powerIndex": float(world_nation.get("resources", {}).get("influence", 0.5)),
        "population_agents": int(world_nation.get("population", 10)),
    }


def load_nations() -> dict[str, Any]:
    if NATION_STORE.is_file():
        try:
            return json.loads(NATION_STORE.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass
    from forge_world_state_v1 import load_world  # noqa: WPS433

    world = load_world()
    nations = [_nation_from_world(nid, n) for nid, n in (world.get("nations") or {}).items()]
    return {"schema": SCHEMA, "nations": nations, "at": _now()}


def save_nations(doc: dict[str, Any]) -> None:
    doc["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    NATION_STORE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def global_geopolitics(nations: list[dict[str, Any]]) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for n in nations:
        n["economy"]["gdp"] = round(float(n["economy"].get("gdp", 0)) * 1.001, 2)
        n["stabilityIndex"] = round(min(1.0, float(n.get("stabilityIndex", 0.8)) + 0.001), 3)
    if len(nations) >= 2:
        a, b = nations[0], nations[1]
        score_a = float(a.get("powerIndex", 0)) + float(a["economy"].get("gdp", 0))
        score_b = float(b.get("powerIndex", 0)) + float(b["economy"].get("gdp", 0))
        if abs(score_a - score_b) < 50:
            events.append({"type": "trade_agreement", "nations": [a.get("id"), b.get("id")]})
    return events


def digital_nation_tick(*, dry_run: bool = True) -> dict[str, Any]:
    from forge_geopolitical_legal_v4 import geo_legal_tick  # noqa: WPS433

    doc = load_nations()
    nations: list[dict[str, Any]] = doc.get("nations") or []
    events = global_geopolitics(nations) if not dry_run else [{"type": "dry_run_stub"}]
    geo = geo_legal_tick(dry_run=dry_run)
    doc["nations"] = nations
    save_nations(doc)
    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "dry_run": dry_run,
        "nations": len(nations),
        "events": events,
        "geo_legal": geo,
        "at": _now(),
    }
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
