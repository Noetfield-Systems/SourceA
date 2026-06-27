#!/usr/bin/env python3
"""Forge L3 repair queue — cloud forge run auto-trigger hook."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
QUEUE = SINA / "forge-l3-repair-queue-v1.json"
RECEIPT = SINA / "forge-l3-auto-runtime-latest-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"items": []}


def enqueue_forge_l3_repair(
    *,
    run_id: str,
    quality_gate: dict[str, Any],
    l3_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Queue failed Forge run for cloud auto-runtime pickup."""
    doc = _read(QUEUE)
    items = list(doc.get("items") or [])
    entry = {
        "run_id": run_id,
        "verdict": quality_gate.get("verdict"),
        "passed_layers": quality_gate.get("passed_layers"),
        "at": _now(),
        "l3_dispatch_id": (l3_result or {}).get("dispatch_id"),
        "dry_run": (l3_result or {}).get("dry_run", True),
    }
    items = [i for i in items if i.get("run_id") != run_id]
    items.append(entry)
    doc = {"schema": "forge-l3-repair-queue-v1", "items": items[-50:], "updated_at": _now()}
    SINA.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    receipt = {"ok": True, "schema": "forge-l3-auto-runtime-v1", "queued": entry, "queue_size": len(items), "at": _now()}
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return receipt


def list_pending() -> list[dict[str, Any]]:
    return list(_read(QUEUE).get("items") or [])


def enqueue_swarm_repair(*, swarm_id: str, goal: str, issues: list[str] | None = None) -> dict[str, Any]:
    """Queue failed swarm replan for cloud civilization tick."""
    doc = _read(QUEUE)
    items = list(doc.get("items") or [])
    entry = {
        "run_id": swarm_id,
        "kind": "swarm_replan",
        "goal": (goal or "")[:500],
        "issues": (issues or [])[:8],
        "at": _now(),
    }
    items = [i for i in items if i.get("run_id") != swarm_id]
    items.append(entry)
    doc = {"schema": "forge-l3-repair-queue-v1", "items": items[-50:], "updated_at": _now()}
    SINA.mkdir(parents=True, exist_ok=True)
    QUEUE.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return {"ok": True, "queued": entry, "queue_size": len(items)}


def tick_forge_l3_repairs(*, dry_run: bool = True) -> dict[str, Any]:
    """Cloud auto-runtime helper — process pending Forge L3 repairs."""
    pending = list_pending()
    processed: list[dict[str, Any]] = []
    for item in pending[:5]:
        rid = str(item.get("run_id") or "")
        if not rid:
            continue
        if item.get("kind") == "swarm_replan":
            from forge_swarm_cloud_dispatch_v1 import dispatch_swarm_cloud  # noqa: WPS433

            row = dispatch_swarm_cloud(
                goal=str(item.get("goal") or ""),
                workspace_path=str(Path.home() / "Desktop" / "SourceA"),
                dry_run=dry_run,
            )
            processed.append({"run_id": rid, "ok": row.get("ok"), "status": row.get("cloud_status"), "kind": "swarm_replan"})
            continue
        from forge_agent_self_improve_l3_v1 import run_self_improve_cloud  # noqa: WPS433

        row = run_self_improve_cloud(
            run_id=rid,
            workspace_path=str(Path.home() / "Desktop" / "SourceA"),
            quality_gate={"verdict": item.get("verdict"), "passed_layers": item.get("passed_layers")},
            dry_run=dry_run,
        )
        processed.append({"run_id": rid, "ok": row.get("ok"), "status": row.get("cloud_status")})
    out = {"ok": True, "schema": "forge-l3-auto-runtime-tick-v1", "processed": processed, "pending": len(pending), "at": _now()}
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
