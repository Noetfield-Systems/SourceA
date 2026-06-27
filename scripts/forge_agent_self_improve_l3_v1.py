#!/usr/bin/env python3
"""Forge L3 self-improve — cloud dispatch when Mac L2 exhausts."""
from __future__ import annotations

import hashlib
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SINA = Path.home() / ".sina"
RECEIPT = SINA / "forge-agent-self-improve-l3-v1.json"
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


def run_self_improve_cloud(
    *,
    run_id: str,
    workspace_path: str,
    quality_gate: dict[str, Any],
    founder_text: str = "",
    l2_result: dict[str, Any] | None = None,
    dry_run: bool = True,
) -> dict[str, Any]:
    """Dispatch failed Forge run to Cloud Workers for L3 repair."""
    failed = [ly for ly in (quality_gate.get("layers") or []) if not ly.get("ok")]
    payload = {
        "kind": "forge_l3_self_improve",
        "source": "forge_terminal_v1",
        "run_id": run_id,
        "founder_text": founder_text[:2000],
        "quality_gate": quality_gate,
        "failed_layers": failed[:11],
        "workspace_hash": _workspace_hash(workspace_path),
        "l2_improved": bool((l2_result or {}).get("improved")),
        "dry_run": dry_run,
    }
    dispatch_id = f"l3-{uuid.uuid4().hex[:10]}"
    out: dict[str, Any] = {
        "ok": True,
        "schema": "forge-agent-self-improve-l3-v1",
        "level": "L3",
        "dispatch_id": dispatch_id,
        "run_id": run_id,
        "dry_run": dry_run,
        "payload": payload,
        "at": _now(),
    }

    if dry_run:
        out["cloud_status"] = "dry_run_stub"
        RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        return out

    import urllib.error
    import urllib.request

    url = f"http://127.0.0.1:{CLOUD_WORKERS_PORT}/api/cloud-worker/dispatch/v1"
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
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

    if run_id and out.get("ok"):
        from forge_terminal_v1 import quality_rerun  # noqa: WPS433

        qr = quality_rerun(run_id=run_id, founder_text=founder_text, workspace_path=workspace_path, full_llm=False)
        out["quality_gate"] = qr.get("quality_gate")
        out["decision_card"] = qr.get("decision_card")

    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return out
