#!/usr/bin/env python3
"""Bind live_pick to run-inbox queue_sa — dual-pick alignment SSOT."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
REGISTRY = ROOT / "os" / "plan-library" / "sourcea-1000" / "REGISTRY.yaml"


def queue_sa_from_disk() -> str:
    """Queue sa from run-inbox truth, then factory-now."""
    for path in (SINA / "run-inbox-disk-truth-v1.json", SINA / "factory-now-v1.json"):
        if not path.is_file():
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        sa = (data.get("queue") or {}).get("sa_id") or data.get("queue_sa") or ""
        if sa:
            return str(sa) if str(sa).startswith("sa-") else f"sa-{sa}"
    return ""


def plan_for_sa(plans: list[dict], sa_id: str) -> dict | None:
    sid = str(sa_id or "").strip()
    if not sid:
        return None
    for pl in plans:
        if pl.get("id") == sid:
            return pl
    return None


def _healthy_queue_row(qsa: str) -> dict | None:
    """Build live_pick from healthy-queue when sa is outside sourcea-1000 REGISTRY."""
    hq_path = SINA / "healthy-queue-30-active.json"
    if not hq_path.is_file():
        return None
    try:
        hq = json.loads(hq_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    era = str(hq.get("era") or "")
    phase = str(hq.get("phase") or "")
    if not (
        hq.get("plans_unified")
        or hq.get("upgrade_plan_schema")
        or phase in ("phase-unified-plans-v1", "phase-s6-outbound-factory-upgrade")
        or era == "forge_factory_cycle2"
    ):
        return None
    for item in hq.get("queue") or []:
        if str(item.get("sa_id") or "") != qsa:
            continue
        return {
            "id": qsa,
            "phase": str(item.get("phase") or phase or era or ""),
            "tier": str(item.get("sa_tier") or "P1"),
            "status": "assigned",
            "title": str(item.get("sa_title") or item.get("title") or "")[:80],
            "path": str(item.get("sa_path") or ""),
        }
    return None


def _phase_market_pick() -> dict | None:
    obs_path = SINA / "phase-observed-v1.json"
    if not obs_path.is_file():
        return None
    try:
        obs = json.loads(obs_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if str(obs.get("era") or "") != "phase_market":
        return None
    head = str(obs.get("cloud_forge_run_head") or "CLOUD-SEC-001")
    return {
        "id": head,
        "phase": "phase-market",
        "tier": "T0",
        "status": "cloud_forge_run",
        "title": f"Secondary Cloud Forge Run · {head}",
        "path": "data/secondary-cloud-forge-run-next-100-v1.json",
    }


def live_pick_aligned(plans: list[dict], *, fallback_pick: dict | None = None) -> dict | None:
    """Prefer queue_sa plan; else healthy-queue row; else phase_market; else phase-first fallback."""
    market = _phase_market_pick()
    if market:
        return market
    qsa = queue_sa_from_disk()
    if qsa:
        row = plan_for_sa(plans, qsa)
        if row:
            return row
        row = _healthy_queue_row(qsa)
        if row:
            return row
    return fallback_pick
