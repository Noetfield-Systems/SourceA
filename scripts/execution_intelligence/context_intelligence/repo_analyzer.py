"""Repository and program awareness (read-only metadata)."""
from __future__ import annotations

import json
from pathlib import Path

SOURCE_A = Path(__file__).resolve().parents[3]
PROGRESS = SOURCE_A / "PROGRAM_PROGRESS.json"
BOWL_STATE = SOURCE_A / "sina-bowl/state.json"
DRIFT = SOURCE_A / "sina-bowl/DRIFT.json"
THREADS_REGISTRY = SOURCE_A / "ASF_PROGRAM_THREADS_REGISTRY_LOCKED_v1.md"
DOC_REGISTRY = SOURCE_A / "SOURCE_A_DOCUMENT_SEQUENCE_REGISTRY_LOCKED_v1.md"

ACTIVE_STATUSES = frozenset({"active", "active_parallel", "mostly_green"})
BLOCKED_STATUSES = frozenset({"blocked", "stalled", "paused", "red"})


def _read_json(path: Path) -> dict | list | None:
    if not path.is_file():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _plan_row(plan: dict) -> dict:
    return {
        "id": plan.get("id"),
        "title": plan.get("title"),
        "thread": plan.get("thread"),
        "status": plan.get("status"),
        "priority": plan.get("priority"),
        "progress_pct": plan.get("progress_pct"),
        "next_action": plan.get("next_action"),
    }


def analyze_repo_state() -> dict:
    prog = _read_json(PROGRESS) or {}
    plans = prog.get("parallel_plans") or []
    bowl = _read_json(BOWL_STATE) or {}
    drift_raw = _read_json(DRIFT)
    drift_items = drift_raw if isinstance(drift_raw, list) else (drift_raw or {}).get("items", []) if isinstance(drift_raw, dict) else []

    active_projects = [_plan_row(p) for p in plans if p.get("status") in ACTIVE_STATUSES]
    blocked_projects = [_plan_row(p) for p in plans if p.get("status") in BLOCKED_STATUSES]

    p0 = plans[0] if plans else {}
    critical_paths: list[str] = []
    if p0.get("next_action"):
        critical_paths.append(f"P0 {p0.get('id')}: {p0['next_action']}")
    for plan in sorted(active_projects, key=lambda p: p.get("priority") or 99)[:3]:
        if plan.get("next_action") and plan.get("id") != p0.get("id"):
            critical_paths.append(f"{plan['id']}: {plan['next_action']}")

    roadmap_docs: list[dict] = []
    try:
        from roadmaps_goals import _roadmap_docs  # noqa: WPS433

        roadmap_docs = _roadmap_docs()
    except Exception:  # noqa: BLE001
        pass

    registry_present = {
        "threads_registry": THREADS_REGISTRY.is_file(),
        "document_registry": DOC_REGISTRY.is_file(),
        "program_progress": PROGRESS.is_file(),
    }

    return {
        "active_projects": active_projects,
        "blocked_projects": blocked_projects,
        "progress_summary": {
            "updated_at": prog.get("updated_at"),
            "p0_id": p0.get("id"),
            "p0_title": p0.get("title"),
            "p0_progress_pct": p0.get("progress_pct"),
            "active_plan_count": len(active_projects),
            "total_plans": len(plans),
            "drift_count": len(drift_items) if isinstance(drift_items, list) else 0,
            "locks": prog.get("locks") or {},
            "must_do_today": (bowl.get("must_do_today") or [])[:5],
        },
        "critical_paths": critical_paths[:6],
        "roadmap_docs": roadmap_docs,
        "registry_present": registry_present,
    }
