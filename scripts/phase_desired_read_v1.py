#!/usr/bin/env python3
"""READ-ONLY desired (spec) loader — founder/ASF authors assignment.active.

Law: data/execution-state-desired-observed-v1.json
FORBIDDEN: any write path in this module. Observed reconciler imports read_* only.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ASSIGNMENT_REPO = ROOT / "data" / "sourcea-worker-professional-assignment-v1.json"
ASSIGNMENT_HOME = Path.home() / ".sina" / "sourcea-worker-professional-assignment-v1.json"
LAW = ROOT / "data" / "execution-state-desired-observed-v1.json"


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def assignment_path() -> Path:
    """Prefer repo SSOT; mirror in ~/.sina is read-only copy for agents."""
    if ASSIGNMENT_REPO.is_file():
        return ASSIGNMENT_REPO
    return ASSIGNMENT_HOME


def read_assignment() -> dict[str, Any]:
    return _read(assignment_path())


def read_desired_active() -> dict[str, Any]:
    """Founder-authored desired slice — spec only."""
    row = read_assignment()
    active = dict(row.get("active") or {})
    return {
        "schema": "phase-desired-active-v1",
        "source": str(assignment_path()),
        "phase_id": str(active.get("phase_id") or ""),
        "start_plan": str(active.get("start_plan") or ""),
        "next_ssot": str(active.get("next_ssot") or ""),
        "execution_plane": str(active.get("execution_plane") or ""),
        "mac_executes": bool(active.get("mac_executes")),
        "prior_phase_complete": str(active.get("prior_phase_complete") or ""),
        "label": str(active.get("label") or ""),
    }


def read_phase_record(phase_id: str) -> dict[str, Any]:
    row = read_assignment()
    for ph in row.get("phases") or []:
        if str(ph.get("id") or "") == phase_id:
            return dict(ph)
    return {}


def desired_targets_phase_market() -> bool:
    return read_desired_active().get("phase_id") == "phase-market"


def desired_cloud_drain_head() -> str:
    return str(read_desired_active().get("start_plan") or "CLOUD-SEC-001")


def validate_desired_readable() -> tuple[bool, list[str]]:
    issues: list[str] = []
    active = read_desired_active()
    if not active.get("phase_id"):
        issues.append("desired_active_phase_id_missing")
    if not active.get("source") or not Path(str(active["source"])).is_file():
        issues.append("assignment_ssot_missing")
    return len(issues) == 0, issues
