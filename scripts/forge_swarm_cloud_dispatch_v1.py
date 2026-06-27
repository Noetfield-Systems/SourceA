#!/usr/bin/env python3
"""Forge Swarm Cloud Dispatch v1 — route live swarm to Cloud Workers / FBE."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-swarm-cloud-dispatch-latest-v1.json"
CLOUD_WORKERS_PORT = 13027


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _workspace_hash(workspace_path: str) -> str:
    root = Path(workspace_path).expanduser()
    if not root.is_dir():
        return ""
    h = hashlib.sha256()
    for p in sorted(root.rglob("*"))[:200]:
        if p.is_file() and p.stat().st_size < 64_000:
            try:
                h.update(p.relative_to(root).as_posix().encode())
                h.update(p.read_bytes()[:512])
            except OSError:
                continue
    return h.hexdigest()[:16]


def dispatch_swarm_cloud(
    *,
    goal: str,
    workspace_path: str,
    parallel: bool = True,
    planner_count: int = 3,
    critic_count: int = 3,
    blackboard_snapshot: dict[str, Any] | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Dispatch swarm run to cloud execution body (Mac-safe dry_run stub)."""
    goal = (goal or "").strip()
    if not goal:
        return {"ok": False, "error": "empty_goal"}

    dispatch_id = f"swarm-{uuid.uuid4().hex[:10]}"
    payload = {
        "kind": "forge_swarm_run",
        "source": "forge_terminal_v1",
        "dispatch_id": dispatch_id,
        "goal": goal[:4000],
        "workspace_hash": _workspace_hash(workspace_path),
        "parallel": parallel,
        "planner_count": planner_count,
        "critic_count": critic_count,
        "blackboard_snapshot": dict(list((blackboard_snapshot or {}).items())[:20]) if isinstance(blackboard_snapshot, dict) else {},
        "dry_run": dry_run,
    }
    out: dict[str, Any] = {
        "ok": True,
        "schema": "forge-swarm-cloud-dispatch-v1",
        "dispatch_id": dispatch_id,
        "goal": goal,
        "dry_run": dry_run,
        "payload": payload,
        "at": _now(),
    }

    if dry_run:
        out["cloud_status"] = "dry_run_stub"
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return out

    import urllib.error
    import urllib.request

    url = f"http://127.0.0.1:{CLOUD_WORKERS_PORT}/api/cloud-worker/dispatch/v1"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            body = json.loads(resp.read().decode())
        out["cloud_status"] = "dispatched"
        out["cloud_response"] = body
        out["ok"] = bool(body.get("ok", True))
    except urllib.error.HTTPError as exc:
        out["ok"] = False
        out["cloud_status"] = "http_error"
        out["error"] = str(exc.code)
    except Exception as exc:
        out["ok"] = False
        out["cloud_status"] = "offline"
        out["error"] = type(exc).__name__

    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
