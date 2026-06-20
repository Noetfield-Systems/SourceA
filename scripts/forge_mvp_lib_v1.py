"""Forge MVP shared helpers — trace paths, router rules, work order context."""
from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
ROUTER_RULES = ROOT / "data" / "forge-mvp-router-rules-v0.1.json"
TASK_GRAPH_SCHEMA = ROOT / "data/schemas/forge-task-graph-v0.1.json"
ACTIVE_WORK_ORDER = SINA / "forge-active-work-order-v1.json"
CLOUD_ENV_RECEIPT = SINA / "forge-cloud-env-receipt-v1.json"
DEFAULT_BAY = "forge-bay"


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def new_run_id(work_order_id: str = "") -> str:
    suffix = work_order_id.replace("/", "-")[:24] if work_order_id else uuid.uuid4().hex[:8]
    return f"forge-run-{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S')}-{suffix}"


def load_router_rules() -> dict[str, Any]:
    return json.loads(ROUTER_RULES.read_text(encoding="utf-8"))


def trace_dir(bay_slug: str = DEFAULT_BAY) -> Path:
    return ROOT / "receipts" / "bays" / bay_slug / "trace"


def trace_path(bay_slug: str, kind: str) -> Path:
    name = "cost.jsonl" if kind == "cost" else "eval.jsonl"
    return trace_dir(bay_slug) / name


def append_trace(bay_slug: str, kind: str, row: dict[str, Any]) -> None:
    p = trace_path(bay_slug, kind)
    p.parent.mkdir(parents=True, exist_ok=True)
    line = {"at": now_utc(), **row}
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(line, separators=(",", ":")) + "\n")


def task_graph_path(run_id: str, bay_slug: str = DEFAULT_BAY) -> Path:
    return trace_dir(bay_slug) / f"{run_id}-task-graph.json"


def persist_work_order(ctx: dict[str, Any]) -> Path:
    SINA.mkdir(parents=True, exist_ok=True)
    row = {"schema": "forge-active-work-order-v1", "saved_at": now_utc(), **ctx}
    ACTIVE_WORK_ORDER.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return ACTIVE_WORK_ORDER


def load_work_order() -> dict[str, Any]:
    if not ACTIVE_WORK_ORDER.is_file():
        return {}
    try:
        return json.loads(ACTIVE_WORK_ORDER.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def workstream_tasks(workstream: str, *, pick: dict[str, Any], run_id: str) -> list[dict[str, Any]]:
    rules = load_router_rules()
    ws_route = (rules.get("route_by_competitor_workstream") or {}).get(workstream, "gpt_control")
    kind_map = {
        "ws-ux": ("research", "ui_gen", "validate"),
        "ws-pricing": ("research", "code_gen", "validate"),
        "ws-run": ("code_gen", "validate", "deploy"),
        "ws-onboard": ("research", "code_gen", "validate"),
        "ws-integrate": ("code_gen", "patch", "validate"),
    }
    kinds = kind_map.get(workstream, ("research", "code_gen", "validate", "deploy", "evaluate"))
    route_by_kind = rules.get("route_by_task_kind") or {}
    tasks: list[dict[str, Any]] = []
    edges: list[dict[str, str]] = []
    prev: str | None = None
    for i, kind in enumerate(kinds, start=1):
        tid = f"T{i}"
        hint = route_by_kind.get(kind, ws_route)
        tasks.append(
            {
                "id": tid,
                "kind": kind,
                "title": f"{pick.get('competitor', '?')} · {workstream} · {kind}",
                "depends_on": [prev] if prev else [],
                "route_hint": hint,
                "artifact_out": f"{run_id}/{tid}",
            }
        )
        if prev:
            edges.append({"from": prev, "to": tid})
        prev = tid
    eval_id = f"T{len(tasks) + 1}"
    tasks.append(
        {
            "id": eval_id,
            "kind": "evaluate",
            "title": "Critic evaluate vs intent",
            "depends_on": [prev] if prev else [],
            "route_hint": "gpt_control",
        }
    )
    if prev:
        edges.append({"from": prev, "to": eval_id})
    return tasks, edges


def build_task_graph(*, pick: dict[str, Any], run_id: str | None = None) -> dict[str, Any]:
    rid = run_id or new_run_id(str(pick.get("id") or ""))
    ws = str(pick.get("workstream") or "ws-ux")
    tasks, edges = workstream_tasks(ws, pick=pick, run_id=rid)
    title = str(pick.get("title") or pick.get("competitor") or "")[:500]
    return {
        "schema": "forge-task-graph-v0.1",
        "version": "0.1.0",
        "run_id": rid,
        "saved_at": now_utc(),
        "prompt": {
            "raw": title,
            "intent": f"{pick.get('stack')} competitor parity · {pick.get('competitor')} · {ws}",
            "constraints": ["cloud_only", "receipt_required", "mac_build_forbidden"],
            "entities": [str(pick.get("competitor") or ""), ws],
            "risk_signals": [],
        },
        "tasks": tasks,
        "edges": edges,
        "meta_loop": {"max_replan": 2, "on_fail": "replan"},
        "work_order": {
            "plan_id": pick.get("id"),
            "stack": pick.get("stack"),
            "stack_key": pick.get("stack_key"),
            "tenant": (pick.get("forge") or {}).get("tenant"),
            "competitor": pick.get("competitor"),
            "workstream": ws,
            "prompt_abs": pick.get("prompt_abs"),
        },
    }
