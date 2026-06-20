#!/usr/bin/env python3
"""One-shot migration: align step IDs with hub phase letters (founder law v4)."""
from __future__ import annotations

import re
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[1]
TARGET = SOURCE_A / "scripts" / "system_roadmap.py"

OLD_TO_NEW: dict[str, str] = {
    # Phase A — spine (was D*)
    "D1": "A1",
    "D2": "A2",
    "D3": "A3",
    "D4": "A4",
    # Phase B — intelligence (was C*)
    "C1": "B1",
    "C2": "B2",
    "C3": "B3",
    "C4": "B4",
    "C5": "B5",
    "C6": "B6",
    # Phase C — runtime (was B*)
    "B1": "C1",
    "B2": "C2",
    "B3": "C3",
    "B4": "C4",
    "B5": "C5",
    "B6": "C6",
    "B7": "C7",
    # Phase D — pre-LLM (was A*)
    "A1.1": "D1",
    "A1.1.1": "D2",
    "A1.2": "D3",
    "A1.3": "D4",
    "A2.1": "D5",
    "A2.1.1": "D6",
    "A2.1b": "D7",
    "A2.2": "D8",
    "A3.1": "D9",
    "A3.2": "D10",
    "A4.1": "D11",
    "A4.2": "D12",
    "A5.1": "D13",
    "A5.2": "D14",
    "A5.3": "D15",
    "A5.3.1": "D16",
}

SUBPHASE_BLOCK = '''            "subphases": [
                {"id": "core", "title": "Core foundation", "steps": ["D1", "D2", "D3", "D4"]},
                {"id": "semantic", "title": "Semantic understanding", "steps": ["D5", "D6", "D7", "D8"]},
                {"id": "decision", "title": "Pre-LLM decision system", "steps": ["D9", "D10"]},
                {"id": "prep", "title": "Execution preparation", "steps": ["D11", "D12"]},
                {"id": "packet", "title": "Final context system", "steps": ["D13", "D14", "D15", "D16"]},
            ],'''

PHASE_STEPS_BLOCK = '''            "steps": ["A1", "A2", "A3", "A4"],
        },
        {
            "id": "B",
            "title": "Execution Intelligence OS",
            "status": "frozen",
            "purpose": "Post-execution learning — frozen after major upgrade intelligence wave.",
            "doc": "SINA_EXECUTION_INTELLIGENCE_STACK_LOCKED_v1.md",
            "build_order": 2,
            "track": "major_upgrade",
            "steps": ["B1", "B2", "B3", "B4", "B5", "B6"],
        },
        {
            "id": "C",
            "title": "Runtime Stack",
            "status": "partial",
            "purpose": "Verified plan → dispatch instruction → confirm → spine.",
            "doc": "SINA_RUNTIME_STACK_LOCKED_v1.md",
            "build_order": 3,
            "track": "major_upgrade",
            "steps": ["C1", "C2", "C3", "C4", "C5", "C6", "C7"],
        },
        {
            "id": "D",
            "title": "Pre-LLM World Model",
            "status": "not_built",
            "purpose": "Repo understanding before execution → LLM context packet (target world model).",
            "doc": "SINA_PRE_LLM_WORLD_MODEL_ROADMAP_LOCKED_v2.md",
            "build_order": 4,
            "track": "major_upgrade",
'''


def migrate_text(text: str) -> str:
    for old in sorted(OLD_TO_NEW, key=len, reverse=True):
        text = text.replace(f'"{old}"', f'"__MIG_{old}__"')
    for old, new in OLD_TO_NEW.items():
        text = text.replace(f'"__MIG_{old}__"', f'"{new}"')

    text = text.replace('CURRENT_RUNTIME_STEP = "C4"', 'CURRENT_RUNTIME_STEP = "C4"')
    text = re.sub(r'CURRENT_RUNTIME_STEP = "[^"]+"', 'CURRENT_RUNTIME_STEP = "C4"', text, count=1)
    text = re.sub(r'CURRENT_STRATEGIC_STEP = "[^"]+"', 'CURRENT_STRATEGIC_STEP = "D1"', text, count=1)
    text = text.replace('PAYLOAD_VERSION = "3.0"', 'PAYLOAD_VERSION = "4.0"')
    text = text.replace('MAP_DOC = "WORLD_TARGET_MODEL_MAP_LOCKED_v3.md"', 'MAP_DOC = "WORLD_TARGET_MODEL_MAP_LOCKED_v4.md"')

    text = text.replace(
        '"steps": ["D1", "D2", "D3", "D4"],\n        },\n        {\n            "id": "B",',
        '"steps": ["A1", "A2", "A3", "A4"],\n        },\n        {\n            "id": "B",',
    )
    text = text.replace(
        '"steps": ["C1", "C2", "C3", "C4", "C5", "C6"],\n        },\n        {\n            "id": "C",',
        '"steps": ["B1", "B2", "B3", "B4", "B5", "B6"],\n        },\n        {\n            "id": "C",',
    )
    text = text.replace(
        '"steps": ["B1", "B2", "B3", "B4", "B5", "B6", "B7"],\n        },\n        {\n            "id": "D",',
        '"steps": ["C1", "C2", "C3", "C4", "C5", "C6", "C7"],\n        },\n        {\n            "id": "D",',
    )

    text = re.sub(
        r'"subphases": \[[\s\S]*?\],\n        \},\n    \]',
        SUBPHASE_BLOCK + "\n        },\n    ]",
        text,
        count=1,
    )

    done_old = '"D1", "D2", "D3", "D4", "C1", "C2", "C3", "C4", "C5", "C6", "B1", "B2", "B3"'
    done_new = '"A1", "A2", "A3", "A4", "B1", "B2", "B3", "B4", "B5", "B6", "C1", "C2", "C3"'
    text = text.replace(done_old, done_new)

    # Strategic build phases — roadmap_id remap via migration tokens already applied if quoted

    # WORLD_TARGET_MAP blocks
    text = text.replace('"after": "D1",\n        "step": "D2",', '"after": "D1",\n        "step": "D2",')
    text = text.replace(
        '"then_queue": ["D2", "D3", "D4", "D5", "D6", "D7", "D8"]',
        '"then_queue": ["D2", "D3", "D4", "D5", "D6", "D7", "D8"]',
    )

    text = text.replace('{"id": "B1-B3",', '{"id": "C1-C3",')
    text = text.replace('{"id": "B4", "title": "Autonomous Repair Loop", "status": "next"},\n    {"id": "D1",',
                        '{"id": "C4", "title": "Autonomous Repair Loop", "status": "next"},\n    {"id": "D1",')

    # Fix prose that wrongly migrated
    text = text.replace("Phase C intelligence (patterns", "Phase B intelligence (patterns")
    text = text.replace("Phase C is FROZEN at C6", "Phase B is FROZEN at B6")
    text = text.replace("Phase C frozen", "Phase B frozen")
    text = text.replace("Next learning is Phase A (pre-LLM)", "Next learning is Phase D (pre-LLM)")
    text = text.replace("Code graph is Phase A1.2", "Code graph is Phase D3")
    text = text.replace("unlocks Phase A1.2", "unlocks Phase D3")
    text = text.replace("Feeds A1.2 impact", "Feeds D3 impact")
    text = text.replace("unlocks B4 repair", "unlocks C4 repair")
    text = text.replace("Beyond B2", "Beyond C2")
    text = text.replace("B2 validates", "C2 validates")
    text = text.replace("graph verification layer (B2)", "graph verification layer (C2)")
    text = text.replace('("B4", "A1.1")', '("C4", "D1")')
    text = text.replace("Step IDs (D1, B4, A1.1)", "Step IDs match phases (A1, B4, C4, D1)")
    text = text.replace('{"id": "C1", "title": "Pattern', '{"id": "B1", "title": "Pattern')
    text = text.replace('{"order": 4, "id": "B5",', '{"order": 4, "id": "B5",')  # chronology ids migrated by quotes

    # ui_contract naming — replace legend with alignment law
    text = re.sub(
        r'"naming_legend": \{[\s\S]*?\},\n        "do_now":',
        '"step_id_law": "Step ID prefix MUST equal hub phase letter — INCIDENT-004 migration v4.",\n        "step_id_migration_doc": "WORLD_TARGET_MODEL_STEP_ID_MIGRATION_LOCKED_v1.md",\n        "do_now":',
        text,
        count=1,
    )
    text = text.replace(
        '"label": f"DO THIS STEP NOW: {CURRENT_RUNTIME_STEP} (Phase C)",',
        '"label": f"DO THIS STEP NOW: {CURRENT_RUNTIME_STEP}",',
    )
    text = text.replace(
        '"naming_note": (\n                "B4 = Hub Phase C runtime. A1.1 = Hub Phase D pre-LLM (step ID A*, not Phase A). "\n                "Phase A spine (D1–D4) is already shipped."\n            ),',
        '"naming_note": "Step ID matches phase letter — C4 is Phase C, D1 is Phase D.",',
    )

    return text


def main() -> int:
    text = TARGET.read_text(encoding="utf-8")
    out = migrate_text(text)
    TARGET.write_text(out, encoding="utf-8")
    print(f"OK: migrated {TARGET.name} · {len(OLD_TO_NEW)} step ID mappings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
