#!/usr/bin/env python3
"""Forge router executor — dispatch task graph to model lanes (cloud MVP)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from forge_mvp_lib_v1 import DEFAULT_BAY, append_trace, load_router_rules, now_utc  # noqa: E402


def _estimate_cost(route: str) -> float:
    caps = load_router_rules().get("cost_caps_usd") or {}
    defaults = {"openrouter_bulk": 0.02, "claude_code": 0.08, "gpt_control": 0.04, "gemini_context": 0.03, "sandbox": 0.0, "critic": 0.04}
    return float(defaults.get(route, caps.get("per_task_default", 0.05)))


def _call_openrouter(prompt: str, model: str) -> dict[str, Any]:
    key = os.environ.get("OPENROUTER_API_KEY", "").strip()
    if not key:
        return {"ok": True, "stub": True, "route": "openrouter_bulk", "note": "no OPENROUTER_API_KEY — stub"}
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": prompt[:4000]}]}).encode()
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=body,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            row = json.loads(resp.read().decode())
            return {"ok": True, "route": "openrouter_bulk", "model": model, "usage": row.get("usage")}
    except Exception as exc:
        return {"ok": False, "route": "openrouter_bulk", "error": str(exc)}


def execute_task(task: dict[str, Any], *, graph: dict[str, Any], bay: str) -> dict[str, Any]:
    rules = load_router_rules()
    kind = str(task.get("kind") or "")
    route = str(task.get("route_hint") or rules.get("route_by_task_kind", {}).get(kind, "gpt_control"))
    if route == "sandbox":
        result = {"ok": True, "route": "sandbox", "note": "delegated_to_fbe_w5_wrappers"}
    elif route == "openrouter_bulk":
        models = (rules.get("models") or {}).get("openrouter_bulk", {}).get("models") or ["deepseek/deepseek-chat"]
        result = _call_openrouter(f"{task.get('title')}\nIntent:{graph.get('prompt',{}).get('intent','')}", str(models[0]))
    else:
        result = {"ok": True, "stub": True, "route": route, "note": f"MVP stub — cloud key lane {route}"}
    cost = _estimate_cost(route)
    append_trace(
        bay,
        "cost",
        {
            "run_id": graph.get("run_id"),
            "task_id": task.get("id"),
            "kind": kind,
            "route": route,
            "cost_usd": cost,
            "ok": result.get("ok"),
            "stub": result.get("stub"),
        },
    )
    return {"task_id": task.get("id"), "route": route, "cost_usd": cost, **result}


def execute_graph(*, graph: dict[str, Any], bay: str = DEFAULT_BAY) -> dict[str, Any]:
    tasks = graph.get("tasks") or []
    results = [execute_task(t, graph=graph, bay=bay) for t in tasks if t.get("kind") != "evaluate"]
    total = sum(float(r.get("cost_usd") or 0) for r in results)
    cap = float((load_router_rules().get("cost_caps_usd") or {}).get("per_run_default", 2.0))
    ok = all(r.get("ok") for r in results) and total <= cap
    return {
        "schema": "forge-router-execute-v0.1",
        "ok": ok,
        "at": now_utc(),
        "run_id": graph.get("run_id"),
        "tasks_run": len(results),
        "cost_usd_total": round(total, 4),
        "cost_cap_usd": cap,
        "results": results,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--graph", required=True, help="Path to task graph JSON")
    ap.add_argument("--bay", default=DEFAULT_BAY)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    graph = json.loads(Path(args.graph).read_text(encoding="utf-8"))
    row = execute_graph(graph=graph, bay=args.bay)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
