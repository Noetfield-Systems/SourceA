#!/usr/bin/env python3
"""Roadmaps & goals payload — reads PROGRAM_PROGRESS.json logged."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

def _source_a_root() -> Path:
    import os

    env = os.environ.get("SINA_SOURCE_A", "").strip()
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[1]


SOURCE_A = _source_a_root()
PROGRESS = SOURCE_A / "PROGRAM_PROGRESS.json"
MASTER_ORDERS = SOURCE_A / "sina-bowl" / "MASTER_ORDERS.json"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _roadmap_docs() -> list[dict]:
    # Product / portfolio roadmaps only — NOT World Target Model (see WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md)
    docs = [
        ("factory", "Product factory roadmap", "PRODUCT_FACTORY_ROADMAP_LOCKED_v1.md", "THREAD-FACTORY"),
        ("investor", "Investor roadmap", "investor/ROADMAP.md", "THREAD-PORTFOLIO"),
        ("commercial-partners", "AI infra partnerships (LOCKED v3)", "AI_INFRA_PARTNERSHIP_PROPOSALS_LOCKED_v1.md", "THREAD-PORTFOLIO"),
        ("hub-proof-ux", "Hub proof UX P0 (LOCKED v1)", "HUB_PROOF_UX_P0_LOCKED_v1.md", "THREAD-FACTORY"),
        ("wire", "Wire lane progress", "WIRE_LANE_PROGRESS.md", "THREAD-WIRE"),
        ("mergepack", "MergePack START_HERE", "~/Desktop/mergepack/START_HERE.md", "THREAD-MERGEPACK"),
    ]
    out = []
    for rid, title, rel, thread in docs:
        path = SOURCE_A / rel if not rel.startswith("~") else Path(rel.replace("~", str(Path.home())))
        out.append(
            {
                "id": rid,
                "title": title,
                "path": str(path),
                "exists": path.is_file(),
                "thread": thread,
                "open_kind": "abs" if str(path).startswith("/") else "path",
            }
        )
    return out


def _strategic_goals() -> list[dict]:
    mo = _read_json(MASTER_ORDERS)
    goals: list[dict] = []
    for sec in mo.get("sections") or []:
        sid = sec.get("id", "")
        title = sec.get("title", "Goals")
        for item in sec.get("items") or []:
            goals.append(
                {
                    "id": f"{sid}-{item.get('id', '')}",
                    "section": title,
                    "text": item.get("text", ""),
                    "status": item.get("status", "active"),
                    "source": "master_orders",
                }
            )
    return goals[:24]


def _synthesis_goals() -> list[dict]:
    try:
        from strategic_synthesis_hub import strategic_goals  # noqa: WPS433

        return strategic_goals()
    except Exception:
        return []


def roadmaps_goals_payload() -> dict:
    prog = _read_json(PROGRESS)
    plans = []
    for p in prog.get("parallel_plans") or []:
        pct = p.get("progress_pct")
        plans.append(
            {
                **p,
                "progress_label": f"{pct}%" if pct is not None else "—",
                "open_detail": "program",
                "detail_id": p.get("id"),
            }
        )
    locks = prog.get("locks") or {}
    return {
        "ok": True,
        "updated_at": prog.get("updated_at") or _now(),
        "summary": {
            "active_plans": len([x for x in plans if x.get("status") in ("active", "active_parallel", "mostly_green")]),
            "total_plans": len(plans),
            "p0_id": (plans[0].get("id") if plans else None),
        },
        "parallel_plans": plans,
        "roadmap_docs": _roadmap_docs(),
        "strategic_goals": _strategic_goals() + _synthesis_goals(),
        "strategic_synthesis_doc": "STRATEGIC_NEXT_STEPS_SYNTHESIS_LOCKED_v2.md",
        "strategic_synthesis_api": "/api/strategic-synthesis-v1",
        "locks": locks,
        "health_mini_app": "http://127.0.0.1:13025/",
        "wtm_pointer": {
            "title": "World Target Model (major upgrade)",
            "note": "System upgrade roadmap — NOT this tab",
            "hub_tab": "system-roadmap",
            "hub_url": "http://127.0.0.1:13020/?tab=system-roadmap",
            "law_doc": "WORLD_TARGET_MODEL_ROADMAP_LAW_LOCKED_v2.md",
            "map_doc": "brain-os/wtm/WORLD_TARGET_MODEL_MAP_LOCKED_v5.md",
        },
    }
