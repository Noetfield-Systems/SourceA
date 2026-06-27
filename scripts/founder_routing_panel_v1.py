#!/usr/bin/env python3
"""Founder Routing Panel — weekly brand routes + live Auto Runtime specialist routing.

Law: docs/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md §3
      docs/SOURCEA_INVESTIGATOR_JUDGE_LOOP_ROOM_LOCKED_v1.md §4
Receipt: ~/.sina/founder-routing-panel-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
RECEIPT = SINA / "founder-routing-panel-v1.json"
STACK_MAP = ROOT / "data" / "commercial" / "stack-map-routing-v1.json"
INVEST_ROUTING = ROOT / "data" / "investigator-specialist-routing-v1.json"

FOUNDER_BRAND_ROUTES = [
    {
        "if_they_say": "Prove our Copilot actions",
        "route_to": "Noetfield",
        "sku": "NF-RD",
        "asset": "Noetfield hero · founding one-pager",
    },
    {
        "if_they_say": "Tokenization / MSB / EMD evidence",
        "route_to": "TrustField",
        "sku": "TF-001 / T-P6",
        "asset": "TrustField beats",
    },
    {
        "if_they_say": "Build our agent loop",
        "route_to": "SourceA",
        "sku": "Agency $3–10K",
        "asset": "SourceA-Commercial-Short.mp4",
    },
    {
        "if_they_say": "Install exchange/KYB factory",
        "route_to": "Catalog",
        "sku": "FBE SKU",
        "asset": "Demo + certainty report",
    },
    {
        "if_they_say": "Publish with accountability",
        "route_to": "WitnessBC",
        "sku": "W-P1",
        "asset": "WitnessBC STYLE-B1",
    },
    {
        "if_they_say": "Nonprofit navigation",
        "route_to": "777",
        "sku": "Gate 0",
        "asset": "No commercial cross-pollution",
    },
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _active_loop_route(*, investigation: dict, judge: dict, specialist: dict) -> dict:
    routes = investigation.get("specialist_routes") or []
    top = routes[0] if routes else {}
    return {
        "investigation_verdict": investigation.get("investigation_verdict"),
        "loop_verdict": judge.get("loop_verdict"),
        "tick_decision": specialist.get("tick_decision"),
        "primary": top.get("primary_label") or top.get("primary") or "—",
        "secondary": top.get("secondary_label") or top.get("secondary"),
        "founder_action": investigation.get("commercial_founder_action"),
        "escalations": judge.get("escalations") or [],
    }


def _panel_line(*, active: dict, brand_count: int) -> str:
    return (
        f"routing · loop={active.get('loop_verdict') or '?'} · "
        f"→{active.get('primary') or '?'} · "
        f"tick={active.get('tick_decision') or '?'} · "
        f"brands={brand_count}"
    )


def run_panel(*, write: bool = True) -> dict:
    stack = _read_json(STACK_MAP)
    inv_routing = _read_json(INVEST_ROUTING)
    investigation = _read_json(SINA / "loop-health-investigation-receipt-v1.json")
    judge = _read_json(SINA / "judge-loop" / "latest-verdict-v1.json")
    specialist = _read_json(SINA / "loop-specialist-tick-receipt-v1.json")
    advisory = _read_json(SINA / "future-loop-prompt-advisory-v1.json")
    observatory = _read_json(SINA / "loop-observatory-report-v1.json")

    if not investigation or investigation.get("schema") != "loop-health-investigation-receipt-v1":
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            from investigator_circle_run_v1 import run_investigation  # noqa: WPS433

            investigation = run_investigation(write=True)
        except Exception:
            pass
    if not judge or judge.get("schema") != "judge-loop-verdict-v1":
        sys.path.insert(0, str(ROOT / "scripts"))
        try:
            from judge_loop_room_v1 import run_judge_loop  # noqa: WPS433

            judge = run_judge_loop(write=True)
        except Exception:
            pass

    active = _active_loop_route(investigation=investigation, judge=judge, specialist=specialist)
    pivot_suffix = ""
    sys.path.insert(0, str(ROOT / "scripts"))
    try:
        from founder_pivot_router_v1 import apply_routing_override, panel_line_suffix  # noqa: WPS433

        active = apply_routing_override(active)
        pivot_suffix = panel_line_suffix()
    except Exception:
        pass
    compile_order = (
        (observatory.get("commercial") or {}).get("compile_order")
        or "SourceA Sina read → Noetfield compile → TrustField send"
    )

    row = {
        "schema": "founder-routing-panel-v1",
        "ok": True,
        "at": _now(),
        "law": "docs/SOURCEA_ECOSYSTEM_FAST_BUSINESS_MODEL_LOCKED_v2.md §3",
        "weekly_ssot": "One brand per email · separate SOWs · CAD ≥ $2K signal",
        "brand_routes": FOUNDER_BRAND_ROUTES,
        "stack_map": {
            "phase": stack.get("phase"),
            "weekly_lever": (stack.get("better_loop") or {}).get("weekly_lever"),
            "compile_order": compile_order,
            "path": str(STACK_MAP),
        },
        "loop_chain": {
            "observatory_line": observatory.get("founder_one_line"),
            "investigator_line": investigation.get("investigator_line"),
            "judge_loop_line": judge.get("judge_loop_line"),
            "loop_specialist_line": specialist.get("loop_specialist_line"),
            "advisory_top": ((advisory.get("ranked_prompts") or [{}])[0]).get("upgrade_id"),
            "machine_routes": inv_routing.get("routes") or [],
        },
        "active_route": active,
        "founder_pivot": {
            "receipt": str(SINA / "founder-pivot-routing-receipt-v1.json"),
            "pivot_id": active.get("pivot_id"),
            "inject_line": active.get("inject_line"),
            "work_template": active.get("work_template"),
        }
        if active.get("pivot_primary")
        else None,
        "founder_routing_panel_line": "",
        "command": "python3 scripts/founder_routing_panel_v1.py --json",
    }
    row["founder_routing_panel_line"] = _panel_line(
        active=active, brand_count=len(FOUNDER_BRAND_ROUTES)
    ) + pivot_suffix
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def hub_slice() -> dict:
    row = _read_json(RECEIPT)
    if not row or row.get("schema") != "founder-routing-panel-v1":
        row = run_panel(write=True)
    active = row.get("active_route") or {}
    w3 = _read_json(SINA / "w3-founder-review-v1.json")
    pending_sina = [
        str(a.get("account_id"))
        for a in (w3.get("artifacts") or [])
        if (a.get("scores") or {}).get("sina_read_pending")
    ]
    loop_chain = row.get("loop_chain") or {}
    return {
        "schema": "worker-hub-routing-panel-v1",
        "ok": row.get("ok"),
        "at": row.get("at"),
        "founder_routing_panel_line": row.get("founder_routing_panel_line"),
        "weekly_ssot": row.get("weekly_ssot"),
        "brand_routes": row.get("brand_routes") or [],
        "active_route": active,
        "loop_chain": loop_chain,
        "compile_order": (row.get("stack_map") or {}).get("compile_order"),
        "panel_settings": {
            "theme": "light",
            "accent": "indigo-gold",
            "layout": "hero-active-route · brand-grid · loop-chain",
        },
        "sina_read": {
            "hub_anchor": "#sina-read-card",
            "hub_url": "http://127.0.0.1:13020/worker-hub/#sina-read-card",
            "pending_count": len(pending_sina),
            "pending_accounts": pending_sina,
            "ship_authority": "sina_read_score_pct only (Sina human)",
            "command_show": "python3 scripts/w3_founder_review_v1.py --show",
            "bundle_path": str(SINA / "outbound" / "founder-review-bundle-v1.md"),
        },
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="Founder routing panel")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--hub-slice", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    if args.hub_slice:
        row = hub_slice()
    else:
        row = run_panel(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_routing_panel_line") or "routing panel ok")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
