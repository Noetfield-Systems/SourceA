#!/usr/bin/env python3
"""Locked-definitions collision check for Signal Factory v1 Base Brain registration."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

LOCKED = ROOT / "reports/locked-definitions-v1.json"
SSOT = ROOT / "data/signal-factory-v1.json"
SKILL = ROOT / ".cursor/skills/signal-factory/SKILL.md"

TRUSTFIELD_CHILD_PHRASES = (
    "trustfield is a sourcea",
    "sourcea owns trustfield",
    "trustfield subsidiary of sourcea",
    "child of sourcea",
)


def run() -> dict:
    locked = json.loads(LOCKED.read_text(encoding="utf-8"))
    ssot = json.loads(SSOT.read_text(encoding="utf-8"))
    skill_text = SKILL.read_text(encoding="utf-8")
    skill_lower = skill_text.lower()

    term_ids = {t["id"] for t in locked.get("terms", []) if isinstance(t, dict)}
    claim_ids = {c["id"] for c in locked.get("claims", []) if isinstance(c, dict)}
    forbidden = {f["id"] for f in locked.get("forbidden", []) if isinstance(f, dict)}

    sf_terms = set(ssot.get("classifications", []) + ssot.get("decisions", []) + ssot.get("score_fields", []))
    sf_entities = set((ssot.get("entity_hygiene") or {}).get("entities", []))

    collisions: list[str] = []
    for t in ["signal-factory", "signal_factory", *sf_terms]:
        if t in term_ids or t in claim_ids or t in forbidden:
            collisions.append(f"id_collision:{t}")

    for phrase in TRUSTFIELD_CHILD_PHRASES:
        if phrase in skill_lower:
            collisions.append(f"trustfield_child:{phrase}")

    if "TrustField" not in sf_entities:
        collisions.append("trustfield_missing_from_entity_hygiene")
    if (ssot.get("adapter_hooks") or {}).get("trustfield") is not None:
        collisions.append("trustfield_adapter_not_null")

    from brain_core_v1.locked_definitions import validate_locked_definitions_checksum  # noqa: WPS433

    chk = validate_locked_definitions_checksum()

    return {
        "schema": "signal-factory-locked-definitions-collision-v1",
        "ok": len(collisions) == 0 and bool(chk.get("match")),
        "collisions": collisions,
        "locked_definitions_checksum": chk,
        "signal_factory_terms_checked": sorted(sf_terms),
        "locked_term_ids": sorted(term_ids),
        "entity_hygiene": sorted(sf_entities),
        "trustfield_separate_watched_surface": True,
        "notes": [
            "Signal Factory classifications/decisions are orthogonal to locked-definitions term/claim ids",
            "locked-definitions requires_status_signal is runtime status keys, not Signal Factory product",
            "TrustField listed as peer entity in entity_hygiene; adapter_hooks.trustfield is null",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run()
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
