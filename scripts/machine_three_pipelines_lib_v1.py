#!/usr/bin/env python3
"""SSOT — Machine refinement pipelines: Calibrate · Tune · machine prove (founder trigger: forge)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"

LAW = "brain-os/law/MACHINE_THREE_PIPELINES_CALIBRATE_TUNE_FORGE_LOCKED_v1.md"
UNIFIED_LAW = "brain-os/law/REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md"
TEST_LADDER_LAW = "SOURCEA_MACHINE_TEST_AND_UPGRADE_LADDER_LOCKED_v1.md"

TIERS: dict[str, dict[str, Any]] = {
    "calibrate": {
        "tier": 1,
        "label": "Blueprint",
        "trigger": "calibrate",
        "duration_class": "short",
        "duration_hint": "10–20 min · map machines + validators + receipts · no upgrade",
        "purpose": "Understand machine ecosystem · test ladder · upgrade law · catalog",
    },
    "tune": {
        "tier": 2,
        "label": "Tune-up",
        "trigger": "tune",
        "duration_class": "medium",
        "duration_hint": "5–20 min · daily/3day ladder · shorter than Forge",
        "purpose": "Routine machine health · receipt sync · heal hubs · discharge to factory",
    },
    "forge": {
        "tier": 3,
        "label": "Forge",
        "trigger": "forge",
        "duration_class": "long_worst",
        "duration_hint": "30–120 min · full upgrade gauntlet · before/after baseline",
        "quarantine": True,
        "purpose": "Sick or pre-ship machine · weekly/monthly proof · W1/W2/W3 delta · passport",
    },
}

CALIBRATE_READS: tuple[tuple[str, str, str], ...] = (
    ("C1", "test_ladder_law", TEST_LADDER_LAW),
    ("C2", "machine_pipelines_law", LAW),
    ("C3", "unified_refinement", UNIFIED_LAW),
    ("C4", "agentic_stack", "SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md"),
    ("C5", "two_hub", "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md"),
    ("C6", "architecture", "docs/ARCHITECTURE.md"),
    ("C7", "runbook", "docs/RUNBOOK.md"),
)

UPGRADE_BOARD: tuple[dict[str, str], ...] = (
    {"id": "UP-01", "goal": "RAGAS CI vs Eval-1b", "win": "W2", "cadence": "Quarterly", "form_pick": "No"},
    {"id": "UP-02", "goal": "Demo film W1", "win": "W1", "cadence": "Weekly", "form_pick": "Yes if hub button"},
    {"id": "UP-03", "goal": "Kernel single write path", "win": "W2", "cadence": "Daily", "form_pick": "No"},
    {"id": "UP-04", "goal": "Machine test ladder", "win": "H1", "cadence": "Daily", "form_pick": "No"},
    {"id": "UP-05", "goal": "Machine refine pipelines", "win": "H1", "cadence": "Daily smoke", "form_pick": "No"},
    {"id": "UP-06", "goal": "Agentic layer v3", "win": "W2", "cadence": "Weekly", "form_pick": "Yes if phase change"},
)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def file_station(sid: str, name: str, rel: str) -> dict[str, Any]:
    path = ROOT / rel
    ok = path.is_file()
    return {"id": sid, "name": name, "path": rel, "ok": ok, "bytes": path.stat().st_size if ok else 0}


def critical_count() -> int:
    p = SINA / "find-bugs" / "last-run.json"
    if not p.is_file():
        return 0
    try:
        return int(load_json(p).get("critical_count") or 0)
    except (TypeError, ValueError):
        return 0
