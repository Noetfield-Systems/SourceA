#!/usr/bin/env python3
"""Forge Civilization Memory v1 — persistent event log for v4 foundation."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
MEMORY_PATH = SINA / "forge-civilization-memory-v1.json"
MAX_EVENTS = 200
MAX_TASK_HISTORY = 100

CONSTITUTION = {
    "max_cost_per_task": 10.0,
    "no_destructive_ops": True,
    "require_verification": True,
    "auditable_memory": True,
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load() -> dict[str, Any]:
    try:
        return json.loads(MEMORY_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {
            "schema": "forge-civilization-memory-v1",
            "event_log": [],
            "task_history": [],
            "failure_patterns": [],
            "graph_snapshot": {},
            "constitution": CONSTITUTION,
            "at": _now(),
        }


def _save(doc: dict[str, Any]) -> None:
    doc["at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    MEMORY_PATH.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def record_run(receipt: dict[str, Any]) -> dict[str, Any]:
    """Append swarm/advisor/L2/L3 run to civilization memory."""
    doc = _load()
    schema = str(receipt.get("schema") or "unknown")
    event = {
        "at": _now(),
        "schema": schema,
        "run_id": receipt.get("swarm_id") or receipt.get("run_id") or receipt.get("advisor_id"),
        "goal": (receipt.get("goal") or "")[:500],
        "ok": receipt.get("ok"),
        "state": receipt.get("state"),
        "dry_run": receipt.get("dry_run"),
    }
    doc["event_log"] = (doc.get("event_log") or [])[-MAX_EVENTS + 1 :] + [event]

    task_entry = {
        "goal": event["goal"],
        "verdict": receipt.get("state") or ("pass" if receipt.get("ok") else "fail"),
        "cost_estimate": receipt.get("cost_estimate") or 1.0,
        "at": event["at"],
    }
    doc["task_history"] = (doc.get("task_history") or [])[-MAX_TASK_HISTORY + 1 :] + [task_entry]

    if not receipt.get("ok"):
        issue = (receipt.get("critic_aggregate") or {}).get("issues") or []
        if issue:
            patterns = list(doc.get("failure_patterns") or [])
            patterns.append({"issues": issue[:5], "at": event["at"]})
            doc["failure_patterns"] = patterns[-50:]

    if receipt.get("repo_graph"):
        doc["graph_snapshot"] = receipt.get("repo_graph")

    _save(doc)
    return {"ok": True, "schema": "forge-civilization-memory-v1", "events": len(doc["event_log"]), "at": _now()}


def load_memory() -> dict[str, Any]:
    return _load()


def pending_failures() -> list[dict[str, Any]]:
    """Tasks from recent failures for civilization tick backlog."""
    doc = _load()
    out: list[dict[str, Any]] = []
    for ev in reversed(doc.get("event_log") or []):
        if ev.get("ok") is False and ev.get("goal"):
            out.append({"goal": ev["goal"], "source": "memory_failure", "run_id": ev.get("run_id")})
        if len(out) >= 5:
            break
    return out
