#!/usr/bin/env python3
"""Knowledge library hub payload — fields, pipeline, ship-ready pointers."""
from __future__ import annotations

from pathlib import Path
from typing import Any

SOURCE_A = Path(__file__).resolve().parents[1]
LIB_ROOT = SOURCE_A / "knowledge-library"


def _doc_row(rel: str, *, role: str = "", title: str = "") -> dict[str, Any]:
    p = SOURCE_A / rel
    return {
        "path": rel,
        "title": title or rel.split("/")[-1],
        "role": role,
        "exists": p.is_file(),
    }


def knowledge_library_payload() -> dict[str, Any]:
    fields: list[dict[str, Any]] = []
    fields_dir = LIB_ROOT / "fields"
    if fields_dir.is_dir():
        for field_dir in sorted(fields_dir.iterdir()):
            if not field_dir.is_dir():
                continue
            fid = field_dir.name
            index = field_dir / "FIELD_INDEX.md"
            stages = {}
            for stage in ("01-extracts", "02-gathered", "03-merged", "04-unified", "05-books"):
                sd = field_dir / stage
                if sd.is_dir():
                    stages[stage] = sorted(
                        str(p.relative_to(SOURCE_A))
                        for p in sd.glob("*.md")
                        if p.is_file()
                    )
            fields.append(
                {
                    "id": fid,
                    "field_index": str(index.relative_to(SOURCE_A)) if index.is_file() else "",
                    "stages": stages,
                    "essay_count": len(stages.get("04-unified") or []),
                    "book_count": len(stages.get("05-books") or []),
                }
            )

    return {
        "ok": True,
        "index": _doc_row("knowledge-library/KNOWLEDGE_LIBRARY_INDEX.md", role="index", title="Master index"),
        "pipeline_law": _doc_row("knowledge-library/PIPELINE_LAW.md", role="law", title="Pipeline law"),
        "ship_ready": _doc_row(
            "SINA_POST_CLAUDE_ANALYSIS_SHIP_READY_COMPANION_v1.md",
            role="ship_ready",
            title="Post-Claude ship-ready companion",
        ),
        "ship_plan_d5": _doc_row(
            "knowledge-library/fields/pre-llm-world-model/04-unified/SHIP_PLAN_D5_AND_GATE_v1.md",
            role="ship_plan",
            title="Ship plan D5 + gate",
        ),
        "agent_start": [
            "Council Room → copy whole-system brief",
            "Essentials → governance entry router",
            "Knowledge Library → field essay + ship plan",
            "World Target Model → D5 + attachments",
            "Agent hub → your private page",
        ],
        "pipeline_stages": ["extract", "gather", "merge", "unify", "book"],
        "fields": fields,
        "primary_field": "pre-llm-world-model",
        "hub_tab": "knowledge-library",
    }
