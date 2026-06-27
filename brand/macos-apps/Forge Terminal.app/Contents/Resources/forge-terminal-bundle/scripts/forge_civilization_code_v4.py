#!/usr/bin/env python3
"""Forge Civilization Code Evolution v4 — code societies with law, economy, culture."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
CIV_STORE = SINA / "forge-civilization-code-v4.json"
RECEIPT = SINA / "forge-civilization-code-tick-latest-v4.json"
SCHEMA = "forge-civilization-code-v4"
VERSION = "4.0.0"

SEED_CIVS: list[dict[str, Any]] = [
    {
        "id": "civ-legal-heavy",
        "name": "Legal-Heavy Civ",
        "lawSystem": {"rules": ["strict correctness", "proof required"], "enforcementLevel": 0.9, "penalties": {"violation": "rollback"}},
        "economy": {"currency": 1000.0, "inflationRate": 0.01, "tradeBalance": 0.0},
        "culture": {"preferences": {"simplicity": 0.3, "performance": 0.2, "safety": 0.9, "creativity": 0.2}},
        "population": [],
        "stability": 0.88,
        "innovationRate": 0.4,
        "nation_id": "nation-sourcea",
    },
    {
        "id": "civ-economic",
        "name": "Economic Civ",
        "lawSystem": {"rules": ["cost optimize", "credit efficiency"], "enforcementLevel": 0.6, "penalties": {"violation": "isolation"}},
        "economy": {"currency": 2500.0, "inflationRate": 0.02, "tradeBalance": 0.1},
        "culture": {"preferences": {"simplicity": 0.4, "performance": 0.5, "safety": 0.4, "creativity": 0.3}},
        "population": [],
        "stability": 0.82,
        "innovationRate": 0.55,
        "nation_id": "nation-cloudforge",
    },
    {
        "id": "civ-fast-exec",
        "name": "Fast-Exec Civ",
        "lawSystem": {"rules": ["speed first", "minimal gates"], "enforcementLevel": 0.4, "penalties": {"violation": "mutation"}},
        "economy": {"currency": 500.0, "inflationRate": 0.03, "tradeBalance": -0.05},
        "culture": {"preferences": {"simplicity": 0.6, "performance": 0.8, "safety": 0.2, "creativity": 0.7}},
        "population": [],
        "stability": 0.7,
        "innovationRate": 0.75,
        "nation_id": "nation-labs",
    },
]


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_civilizations() -> dict[str, Any]:
    if CIV_STORE.is_file():
        try:
            doc = json.loads(CIV_STORE.read_text(encoding="utf-8"))
            if doc.get("civilizations"):
                return doc
        except (json.JSONDecodeError, OSError):
            pass
    return {"schema": SCHEMA, "civilizations": [dict(c) for c in SEED_CIVS], "treaties": [], "at": _now()}


def save_civilizations(doc: dict[str, Any]) -> None:
    doc["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    CIV_STORE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def trade_modules(civ_a: dict[str, Any], civ_b: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    pop_a = civ_a.setdefault("population", [])
    pop_b = civ_b.setdefault("population", [])
    if pop_a:
        pop_b.append({**pop_a[-1], "id": f"cit-{uuid.uuid4().hex[:6]}", "allegiance": civ_b.get("id")})
    if pop_b:
        pop_a.append({**pop_b[-1], "id": f"cit-{uuid.uuid4().hex[:6]}", "allegiance": civ_a.get("id")})
    civ_a["economy"]["tradeBalance"] = round(float(civ_a["economy"].get("tradeBalance", 0)) + 0.02, 3)
    civ_b["economy"]["tradeBalance"] = round(float(civ_b["economy"].get("tradeBalance", 0)) + 0.02, 3)
    return civ_a, civ_b


def resolve_conflict(civ_a: dict[str, Any], civ_b: dict[str, Any]) -> dict[str, Any]:
    score_a = float(civ_a.get("stability", 0)) + float(civ_a.get("innovationRate", 0))
    score_b = float(civ_b.get("stability", 0)) + float(civ_b.get("innovationRate", 0))
    winner, loser = (civ_a, civ_b) if score_a >= score_b else (civ_b, civ_a)
    winner["population"] = (winner.get("population") or []) + (loser.get("population") or [])[:2]
    loser["stability"] = round(max(0.1, float(loser.get("stability", 0)) - 0.1), 3)
    return {"winner": winner.get("id"), "loser": loser.get("id"), "score_a": score_a, "score_b": score_b}


def civilization_code_tick(*, dry_run: bool = True) -> dict[str, Any]:
    from forge_self_build_v3 import swarm_evolve_tick  # noqa: WPS433

    doc = load_civilizations()
    civs: list[dict[str, Any]] = doc.get("civilizations") or []
    swarm = swarm_evolve_tick(dry_run=dry_run, pool_size=3, rounds=1)

    for civ in civs:
        for w in swarm.get("winners") or []:
            citizen = {
                "id": f"cit-{uuid.uuid4().hex[:8]}",
                "code": w.get("genome_id", "stub"),
                "allegiance": civ.get("id"),
                "productivity": round(float(civ.get("innovationRate", 0.5)), 3),
                "compliance": round(float(civ.get("lawSystem", {}).get("enforcementLevel", 0.5)), 3),
            }
            civ.setdefault("population", []).append(citizen)
        civ["population"] = civ["population"][-50:]

    conflicts: list[dict[str, Any]] = []
    if len(civs) >= 2:
        civs[0], civs[1] = trade_modules(civs[0], civs[1])
        conflicts.append(resolve_conflict(civs[0], civs[2] if len(civs) > 2 else civs[1]))

    doc["civilizations"] = civs
    save_civilizations(doc)

    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "dry_run": dry_run,
        "civilizations": len(civs),
        "swarm": swarm,
        "conflicts": conflicts,
        "at": _now(),
    }
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
