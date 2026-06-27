#!/usr/bin/env python3
"""AG Routing Panel — agent-light + full modes for Cursor agents (cost · route · ROI)."""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

VERSION = "1.1.0"
PORT = int(os.environ.get("AG_ROUTING_PANEL_PORT", "8782"))
ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _golden_tips(*, routing: dict, cost: dict, active: dict) -> list[str]:
    tips: list[str] = []
    tips.append(
        "Brain = Auto route only · Worker = one sa bounded path · heavy motor = cloud not Mac validators."
    )
    tier = (cost.get("task_tiers") or {}).get("T0", {})
    if tier:
        tips.append(f"T0 daily: {tier.get('where')} · model {tier.get('model')} — receipts not chat mega-paste.")
    primary = active.get("primary") or active.get("route_to")
    if primary and primary != "—":
        tips.append(f"Active loop route → {primary} — align next WORK order to that lane.")
    if active.get("loop_verdict") not in (None, "PASS", "ok"):
        tips.append("Loop verdict not clean — run API Station routing_panel (light) before new sa builds.")
    tips.append("Full architect WebGL lives on :8780 — this app is fast agent truth on :8782.")
    tips.append("Founder form P0 only when motor blocked — agents fix wiring in the repository first.")
    return tips[:6]


def _mermaid_agent_flow() -> str:
    return """flowchart TB
  subgraph cursor["Cursor Mac — control plane"]
    B[Brain · Auto · route]
    W[Worker · Composer · one sa]
  end
  subgraph cloud["Cloud body"]
    CW[Cloud Workers · CLOUD-SEC]
    N8[n8n cron · backup]
    RF[Railway FORGE]
  end
  F[Founder] --> B
  B --> W
  W --> CW
  CW --> RF
  N8 -.-> CW
  B -.->|never implement sa| X[refuse]
"""


def _mermaid_brand_routes(routes: list[dict]) -> str:
    lines = ["flowchart LR"]
    for i, r in enumerate(routes[:6]):
        say = str(r.get("if_they_say") or r.get("label") or f"r{i}")[:28].replace('"', "'")
        dest = str(r.get("route_to") or "?")
        lines.append(f'  S{i}["{say}"] --> D{i}["{dest}"]')
    return "\n".join(lines)


def _as_list(val: Any, limit: int = 8) -> list[Any]:
    if isinstance(val, list):
        return val[:limit]
    if isinstance(val, dict):
        return list(val.values())[:limit]
    return []


def _build_agent_glance(
    *,
    live: dict[str, Any],
    phase: dict[str, Any],
    active: dict[str, Any],
    cost: dict[str, Any],
    routing: dict[str, Any],
) -> dict[str, Any]:
    """First-screen agent routing — where to go next."""
    queue = phase.get("cloud_forge_run_head") or phase.get("queue_head") or "—"
    factory = (
        live.get("factory_now_line")
        or routing.get("founder_routing_panel_line")
        or "Read disk · route · one bounded WORK order"
    )
    priority = live.get("task_plan_priority_line") or ""
    cost_line = cost.get("one_law") or cost.get("line") or "Auto/Composer daily · API ship-window only"

    apps = {
        "hub": {"id": "hub", "label": "Worker Hub", "href": "http://127.0.0.1:13020/"},
        "cloud": {"id": "cloud", "label": "Cloud Workers", "href": "http://127.0.0.1:13027/"},
        "n8n": {"id": "n8n", "label": "N8N Integration", "href": "http://127.0.0.1:13026/"},
        "chat": {"id": "chat", "label": "Chat Unify", "href": "http://127.0.0.1:13023/"},
        "mail": {"id": "mail", "label": "Portfolio Mail", "href": "http://127.0.0.1:13020/mail-hub/"},
        "mac-law": {"id": "mac-law", "label": "Mac Law", "href": "http://127.0.0.1:8781/"},
    }

    primary_key = "hub"
    primary_reason = "Daily task queue · cloud proceed · form picks — start WORK here."
    q_upper = str(queue).upper()
    if q_upper and q_upper != "—" and ("CLOUD" in q_upper or "SA-MKT" in q_upper or "B0" in q_upper):
        primary_key = "cloud"
        primary_reason = f"Queue head {queue} — run cloud motor / proceed next drain row."
    elif active.get("loop_verdict") not in (None, "PASS", "ok", "—"):
        primary_key = "ag-routing"
        primary_reason = "Loop verdict not clean — refresh routing panel before new builds."
    founder_action = str(active.get("founder_action") or "").strip()
    if founder_action and founder_action not in ("—", "none", "None"):
        primary_key = "hub"
        primary_reason = f"Founder action: {founder_action[:80]} — Worker Hub form lane."

    primary = dict(apps.get(primary_key, apps["hub"]))
    primary["reason"] = primary_reason
    if primary_key == "ag-routing":
        primary = {
            "id": "ag-routing",
            "label": "Refresh routing panel",
            "href": "http://127.0.0.1:8782/",
            "reason": primary_reason,
            "action": "refresh_panel",
        }

    quick = [primary]
    for key in ("cloud", "hub", "n8n", "chat"):
        if key != primary_key and key in apps:
            row = dict(apps[key])
            row["reason"] = {
                "cloud": "CLOUD-SEC queue · Railway dispatch",
                "hub": "Backlog · proceed · API Station",
                "n8n": "Automation spine · validators · 24/7 cron",
                "chat": "Merge Cursor chats · webhook wire",
            }.get(key, "")
            quick.append(row)

    return {
        "factory_line": factory,
        "queue_head": queue,
        "priority_line": priority,
        "cost_one_liner": cost_line,
        "primary_action": primary,
        "quick_apps": quick[:5],
        "role_hint": "Brain = Auto route only · Worker = one sa · cloud = motor body",
    }


def build_report_light() -> dict[str, Any]:
    """Sub-second disk slice — default agent daily view."""
    sys_path = str(ROOT / "scripts")
    if sys_path not in __import__("sys").path:
        __import__("sys").path.insert(0, sys_path)

    routing_receipt = _read(SINA / "founder-routing-panel-v1.json")
    if not routing_receipt.get("founder_routing_panel_line"):
        try:
            from founder_routing_panel_v1 import hub_slice  # noqa: WPS433

            routing_receipt = hub_slice()
        except Exception:
            pass

    cost = _read(ROOT / "data/cursor-cost-intelligence-routing-v1.json")
    orient = _read(ROOT / "data/sourcea_orient_routing_v1.json")
    live = _read(SINA / "agent-live-surfaces-v1.json")
    phase = _read(SINA / "phase-observed-v1.json")

    active = routing_receipt.get("active_route") or {}
    brands = routing_receipt.get("brand_routes") or []
    loop = routing_receipt.get("loop_chain") or {}

    return {
        "ok": True,
        "schema": "ag-routing-panel-v1",
        "mode": "light",
        "version": VERSION,
        "port": PORT,
        "at": _now(),
        "headline": routing_receipt.get("founder_routing_panel_line")
        or live.get("factory_now_line")
        or "AG Routing — agent light",
        "cursor_cost": {
            "one_law": cost.get("one_law"),
            "pools": cost.get("cursor_pools"),
            "model_routing": cost.get("cursor_model_routing"),
            "task_tiers": cost.get("task_tiers"),
            "order_template": cost.get("founder_order_template"),
            "line": cost.get("cursor_cost_intelligence_line")
            or "Auto/Composer daily · API ship-window only",
        },
        "active_route": active,
        "brand_routes": brands,
        "loop_chain": {
            "observatory": loop.get("observatory_line"),
            "investigator": loop.get("investigator_line"),
            "judge": loop.get("judge_loop_line"),
            "specialist": loop.get("loop_specialist_line"),
            "compile_order": routing_receipt.get("compile_order")
            or (routing_receipt.get("stack_map") or {}).get("compile_order"),
        },
        "queue_head": phase.get("cloud_forge_run_head") or phase.get("queue_head"),
        "orient_roles": _as_list(orient.get("role_routing") or orient.get("roles"), 8),
        "golden_tips": _golden_tips(routing=routing_receipt, cost=cost, active=active),
        "agent_glance": _build_agent_glance(
            live=live,
            phase=phase,
            active=active,
            cost=cost,
            routing=routing_receipt,
        ),
        "mermaid": {
            "agent_flow": _mermaid_agent_flow(),
            "brand_routes": _mermaid_brand_routes(brands),
        },
        "links": {
            "legacy_architect": "http://127.0.0.1:8780/",
            "mac_law": "http://127.0.0.1:8781/",
            "worker_hub": "http://127.0.0.1:13020/",
            "cloud_workers": "http://127.0.0.1:13027/",
        },
        "for_agent": {
            "plain_english": (
                "Use light mode for daily Cursor routing: cost pools, active brand route, "
                "loop one-liners, queue head. Switch Full for investigator routes + stack map."
            ),
        },
    }


def build_report_full() -> dict[str, Any]:
    """Full agent routing — still disk-first, no WebGL."""
    light = build_report_light()
    light["mode"] = "full"
    sys_path = str(ROOT / "scripts")
    if sys_path not in __import__("sys").path:
        __import__("sys").path.insert(0, sys_path)

    try:
        from founder_routing_panel_v1 import run_panel  # noqa: WPS433

        panel = run_panel(write=False)
    except Exception as exc:
        panel = {"ok": False, "error": str(exc)[:200]}

    try:
        from cursor_cost_intelligence_routing_v1 import main as cost_main  # noqa: WPS433
        import io
        import contextlib

        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            cost_main()
    except Exception:
        pass

    inv_routes = _read(ROOT / "data/investigator-specialist-routing-v1.json")
    stack = _read(ROOT / "data/commercial/stack-map-routing-v1.json")
    orient_report = _read(SINA / "orient-routing-report-v1.json")

    light["full_panel"] = panel
    light["investigator_routes"] = inv_routes.get("routes") or []
    light["stack_map"] = stack
    light["orient_report"] = {
        "ok": orient_report.get("ok"),
        "summary": orient_report.get("summary_line") or orient_report.get("for_founder"),
        "at": orient_report.get("at"),
    }
    light["loop_chain_full"] = panel.get("loop_chain") or {}
    light["weekly_ssot"] = panel.get("weekly_ssot")
    light["founder_pivot"] = panel.get("founder_pivot")
    light["mermaid"]["loop_chain"] = """flowchart TD
  O[Observatory] --> A[Advisory]
  A --> I[Investigator]
  I --> J[Judge]
  J --> S[Loop specialist]
  S --> R[Routing panel]
  R --> P[Plans unified]"""
    return light


def handle_action(body: dict | None = None) -> dict[str, Any]:
    body = body or {}
    action = str(body.get("action") or "report").strip().lower()
    if action in ("report_full", "full"):
        return build_report_full()
    if action == "refresh_panel":
        try:
            from founder_routing_panel_v1 import run_panel  # noqa: WPS433

            return {"ok": True, "panel": run_panel(write=True), **build_report_light()}
        except Exception as exc:
            return {"ok": False, "error": str(exc)[:200]}
    if action == "orient_refresh":
        try:
            from orient_routing_v1 import build_orient_report  # noqa: WPS433

            return {"ok": True, "orient": build_orient_report(), **build_report_light()}
        except Exception as exc:
            return {"ok": False, "error": str(exc)[:200]}
    return build_report_light()
