#!/usr/bin/env python3
"""ZCP ingest v1 — Forge Terminal bridge → Cursor inbox · Forge orchestrator spine."""
from __future__ import annotations

import hashlib
import json
import os
import urllib.error
import urllib.request
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal

from zcp.zcp_lib_v1 import (
    ZCPRunResult,
    critic_validate,
    run_executor,
    task_id_from_envelope,
)

SINA = Path.home() / ".sina"
RECEIPT_LOG = SINA / "zcp-bridge-receipts-v1.jsonl"
ORCHESTRATOR_URL = os.environ.get("FORGE_ORCHESTRATOR_URL", "http://127.0.0.1:3101").rstrip("/")

Plane = Literal["parse_only", "cursor", "cloud", "auto"]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _sha256(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _append_receipt(row: dict[str, Any]) -> None:
    SINA.mkdir(parents=True, exist_ok=True)
    with RECEIPT_LOG.open("a", encoding="utf-8") as f:
        f.write(json.dumps(row, separators=(",", ":")) + "\n")


def _probe_orchestrator() -> bool:
    try:
        req = urllib.request.Request(f"{ORCHESTRATOR_URL}/health", method="GET")
        with urllib.request.urlopen(req, timeout=2) as resp:
            return resp.status == 200
    except (urllib.error.URLError, OSError, TimeoutError):
        return False


def _post_orchestrator(payload: dict[str, Any]) -> dict[str, Any]:
    body = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        f"{ORCHESTRATOR_URL}/zcp/ingest",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return {"ok": False, "error": f"http_{exc.code}", "detail": raw[:400]}
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return {"ok": False, "error": "orchestrator_unreachable", "detail": str(exc)[:200]}


def _send_cursor(prompt: str, *, task_id: str, meta: dict[str, Any] | None = None) -> dict[str, Any]:
    import sys
    from pathlib import Path

    scripts = Path(__file__).resolve().parents[1]
    if str(scripts) not in sys.path:
        sys.path.insert(0, str(scripts))
    from worker_inject_lib import deliver_to_worker_inbox  # noqa: WPS433

    inj = deliver_to_worker_inbox(
        prompt,
        source="zcp_bridge_v1",
        meta={
            "sa_id": f"zcp-{task_id}",
            "queue_role": "act",
            "origin": "zcp_ingest_v1",
            "zcp_task_id": task_id,
            **(meta or {}),
        },
        fast=True,
    )
    return inj


def _resolve_plane(run: ZCPRunResult, plane: Plane, orchestrator_up: bool) -> Plane:
    if plane != "auto":
        return plane
    if run.mode == "CRITIC":
        return "parse_only"
    if orchestrator_up:
        return "cloud"
    return "cursor"


def ingest(
    *,
    input_text: str,
    complexity: str = "medium",
    project_id: str = "zcp",
    dispatch: bool = False,
    plane: Plane = "auto",
    dry_run: bool = False,
) -> dict[str, Any]:
    if not input_text.strip():
        return {"ok": False, "schema": "zcp-bridge-ingest-v1", "error": "input required"}

    run = run_executor(input_text, complexity=complexity)  # type: ignore[arg-type]
    task_id = task_id_from_envelope(run.envelope)
    orch_up = _probe_orchestrator()
    resolved_plane = _resolve_plane(run, plane, orch_up)

    receipt = {
        "schema": "zcp-execution-receipt-v1",
        "task_id": task_id,
        "timestamp": int(datetime.now(timezone.utc).timestamp() * 1000),
        "zcp_type": run.mode,
        "station": run.route,
        "input_hash": _sha256(input_text),
        "status": "rejected" if run.status != "ok" else ("scored" if run.mode == "CRITIC" else "applied"),
        "plane": resolved_plane,
        "at": _now(),
    }
    _append_receipt(receipt)

    if run.status != "ok":
        return {
            "ok": False,
            "schema": "zcp-bridge-ingest-v1",
            "task_id": task_id,
            "zcp": asdict(run),
            "receipt": receipt,
            "error": "; ".join(run.validation_errors) or "validation failed",
        }

    result: dict[str, Any] = {
        "ok": True,
        "schema": "zcp-bridge-ingest-v1",
        "task_id": task_id,
        "zcp": {
            "status": run.status,
            "mode": run.mode,
            "route": run.route,
            "prompt": run.prompt,
            "envelope": run.envelope,
            "validation_errors": run.validation_errors,
        },
        "receipt": receipt,
        "plane": resolved_plane,
        "orchestrator_up": orch_up,
    }

    if resolved_plane == "parse_only":
        result["for_founder"] = {"show_this": f"ZCP {run.mode} parsed — copy prompt to Cursor or set plane=cloud"}
        return result

    if dry_run:
        result["dry_run"] = True
        result["for_founder"] = {"show_this": f"ZCP {run.mode} dry-run — would route via {resolved_plane}"}
        return result

    if resolved_plane == "cursor":
        inj = _send_cursor(run.prompt, task_id=task_id)
        result["cursor_bridge"] = inj
        result["ok"] = bool(inj.get("ok"))
        if not inj.get("ok"):
            result["error"] = str(inj.get("error") or "cursor_inbox_failed")
        else:
            result["for_founder"] = {"show_this": f"ZCP {run.mode} → Cursor Worker inbox · {task_id}"}
        return result

    spine = _post_orchestrator(
        {
            "input": input_text,
            "project_id": project_id,
            "complexity": complexity,
            "dispatch": dispatch,
        }
    )
    result["spine"] = spine
    result["ok"] = bool(spine.get("ok"))
    if spine.get("ok"):
        result["for_founder"] = {
            "show_this": f"ZCP {run.mode} → Forge spine · task {spine.get('task_id') or task_id} · route {run.route}",
        }
    else:
        result["error"] = str(spine.get("error") or "spine_ingest_failed")
        if orch_up is False:
            inj = _send_cursor(run.prompt, task_id=task_id)
            result["cursor_fallback"] = inj
            if inj.get("ok"):
                result["ok"] = True
                result["plane"] = "cursor"
                result["for_founder"] = {"show_this": "Orchestrator down — fell back to Cursor inbox"}
    return result


def parse_only(input_text: str, *, complexity: str = "medium") -> dict[str, Any]:
    run = run_executor(input_text, complexity=complexity)  # type: ignore[arg-type]
    return {
        "ok": run.status == "ok",
        "schema": "zcp-bridge-parse-v1",
        "zcp": asdict(run),
        "task_id": task_id_from_envelope(run.envelope),
    }


def critic_gate(output: dict[str, Any]) -> dict[str, Any]:
    gate = critic_validate(output)
    return {"ok": True, "schema": "zcp-bridge-critic-v1", "gate": gate, "output": output}


def list_receipts(limit: int = 20) -> list[dict[str, Any]]:
    if not RECEIPT_LOG.is_file():
        return []
    lines = RECEIPT_LOG.read_text(encoding="utf-8").splitlines()
    out: list[dict[str, Any]] = []
    for line in lines[-limit:]:
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return out
