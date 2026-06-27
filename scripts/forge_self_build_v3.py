#!/usr/bin/env python3
"""Forge Self-Building v3 — distributed evolutionary swarm compiler."""
from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from forge_self_build_v2 import (  # noqa: WPS433
    SCHEMA as SCHEMA_V2,
    VERSION as VERSION_V2,
    build_spec,
    prove,
    register_evolution,
    save_rollback_snapshot,
    integrate_module,
    detect_missing_modules,
    introspect_system,
    _now,
)

SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-self-build-swarm-latest-v3.json"
SCHEMA = "forge-self-build-v3"
VERSION = "3.0.0"


def _genome(code: str, *, parent_ids: list[str] | None = None) -> dict[str, Any]:
    return {
        "id": f"gen-{uuid.uuid4().hex[:8]}",
        "code": code,
        "fitness": 0.0,
        "proofScore": 0.0,
        "performanceScore": 0.0,
        "stabilityScore": 0.0,
        "parentIds": parent_ids or [],
    }


def generate_swarm(*, gap: str, n: int = 5, dry_run: bool = True) -> list[dict[str, Any]]:
    from forge_self_build_v1 import generate_module_stub  # noqa: WPS433

    base = generate_module_stub(gap=gap, dry_run=dry_run)
    population: list[dict[str, Any]] = []
    for i in range(n):
        code = base["code"]
        if i % 2 == 1:
            code = code.replace("return {", "# optimized\n    return {")
        if i % 3 == 0:
            code = "# variant " + str(i) + "\n" + code
        population.append(_genome(code))
    return population


def mutate(genome: dict[str, Any]) -> dict[str, Any]:
    code = str(genome.get("code") or "")
    if "try:" not in code:
        code = code.replace("def ", "def _safe_", 1)
        code = code.replace("return {", "try:\n        pass\n    except Exception:\n        return {'ok': False}\n    return {", 1)
    return _genome(code, parent_ids=[str(genome.get("id"))])


def crossover(a: dict[str, Any], b: dict[str, Any]) -> dict[str, Any]:
    ca = str(a.get("code") or "")
    cb = str(b.get("code") or "")
    merged = ca.split("\n")[0] + "\n" + cb.split("\n")[-1] if cb else ca
    return _genome(merged, parent_ids=[str(a.get("id")), str(b.get("id"))])


def benchmark(code: str) -> float:
    return round(max(0.1, 1.0 - len(code) / 5000), 3)


def evaluate(genome: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    module = {"name": spec.get("name"), "code": genome.get("code"), "version": "0.1.0"}
    proof = prove(module, spec)
    perf = benchmark(str(genome.get("code") or ""))
    stability = 1.0 if proof.get("simulationPassed") else 0.3
    fitness = round(proof.get("confidence", 0) * 0.5 + perf * 0.3 + stability * 0.2, 4)
    genome["proofScore"] = proof.get("confidence", 0)
    genome["performanceScore"] = perf
    genome["stabilityScore"] = stability
    genome["fitness"] = fitness
    genome["proof"] = proof
    return genome


def select_best(population: list[dict[str, Any]]) -> dict[str, Any] | None:
    if not population:
        return None
    return sorted(population, key=lambda g: float(g.get("fitness") or 0), reverse=True)[0]


def swarm_evolve_tick(*, dry_run: bool = True, pool_size: int = 5, rounds: int = 2) -> dict[str, Any]:
    state = introspect_system()
    gaps = detect_missing_modules(state)
    winners: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []

    for gap in gaps[:2]:
        spec = build_spec(gap)
        population = generate_swarm(gap=gap, n=pool_size, dry_run=dry_run)
        for _ in range(rounds):
            population = [mutate(g) for g in population]
            if len(population) >= 2:
                population.append(crossover(population[0], population[1]))
        population = [evaluate(g, spec) for g in population]
        best = select_best(population)
        if not best or not (best.get("proof") or {}).get("valid"):
            failures.append({"gap": gap, "reason": "no_valid_genome"})
            continue
        module = {"name": spec.get("name"), "code": best.get("code"), "version": "0.1.0", "gap": gap}
        save_rollback_snapshot(module)
        integrate_module(module, dry_run=dry_run)
        register_evolution(module, best.get("proof") or {})
        winners.append({"gap": gap, "genome_id": best.get("id"), "fitness": best.get("fitness")})

    out = {
        "ok": True,
        "schema": SCHEMA,
        "version": VERSION,
        "parent_schema": SCHEMA_V2,
        "dry_run": dry_run,
        "winners": winners,
        "failures": failures,
        "gaps": gaps,
        "at": _now(),
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
