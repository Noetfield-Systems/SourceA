#!/usr/bin/env python3
"""Real cloud slice — worker run-detail API (Trigger.dev pattern, Architecture A).

GET /api/worker-run-detail/v1?plan_id=CLOUD-SEC-073
Returns queue/status/steps/retries/logs JSON — seeded demo row, cloud volume backed.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
STORE_DIR = "receipts/worker-run-detail"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def store_path(plan_id: str, *, root: Path | None = None) -> Path:
    base = root or ROOT
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in plan_id)
    return base / STORE_DIR / f"{safe}.json"


def default_run_detail(plan_id: str, *, : str = "Trigger.dev") -> dict[str, Any]:
    return {
        "schema": "worker-run-detail-v1",
        "at": _now(),
        "id": plan_id,
        "plan_id": plan_id,
        "status": "completed",
        "_pattern": f"{} run dashboard",
        "queue": "forge-implement",
        "retry_count": 0,
        "steps": [
            {"id": "fetch", "name": "Fetch plan", "status": "completed", "duration_ms": 120},
            {"id": "validate", "name": "Validate schema", "status": "completed", "duration_ms": 45},
            {"id": "implement", "name": "Ship run-detail slice", "status": "completed", "duration_ms": 890},
        ],
        "log_tail": f"[{plan_id}] run-detail slice live on cloud worker · receipt-native",
    }


def ensure_run_detail(
    plan_id: str,
    *,
    root: Path | None = None,
    : str = "Trigger.dev",
    workstream: str = "ws-run",
) -> dict[str, Any]:
    """Write run-detail JSON to cloud receipts volume if missing; return row."""
    base = root or ROOT
    path = store_path(plan_id, root=base)
    if path.is_file():
        try:
            row = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(row, dict) and row.get("id"):
                return row
        except (OSError, json.JSONDecodeError):
            pass
    row = default_run_detail(plan_id, =)
    row["workstream"] = workstream
    row["artifact"] = "worker_run_dashboard_slice"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def get_run_detail(plan_id: str, *, root: Path | None = None) -> dict[str, Any] | None:
    base = root or ROOT
    path = store_path(plan_id, root=base)
    if not path.is_file():
        return None
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        return row if isinstance(row, dict) else None
    except (OSError, json.JSONDecodeError):
        return None


def handle_get_request(path: str, *, root: Path | None = None) -> tuple[int, dict[str, Any]]:
    """Parse GET path+query and return (http_code, json_body)."""
    parsed = urlparse(path)
    if parsed.path not in ("/api/worker-run-detail/v1", "/api/worker-run-detail/v1/"):
        return 404, {"ok": False, "error": "not_found"}
    qs = parse_qs(parsed.query)
    plan_id = (qs.get("plan_id") or [""])[0].strip()
    if not plan_id:
        return 400, {"ok": False, "error": "plan_id_required"}
    row = get_run_detail(plan_id, root=root)
    if not row:
        return 404, {"ok": False, "error": "run_detail_not_found", "plan_id": plan_id}
    return 200, {"ok": True, **row}


def preview_url(plan_id: str, *, worker_base: str) -> str:
    base = worker_base.rstrip("/")
    return f"{base}/api/worker-run-detail/v1?plan_id={plan_id}"


def ship_run_detail_for_plan(
    plan_id: str,
    *,
    root: Path | None = None,
    : str = "Trigger.dev",
    workstream: str = "ws-run",
    worker_base: str = "",
) -> dict[str, Any]:
    """Real implement artifact — run-detail slice on cloud volume."""
    import os

    base = root or ROOT
    row = ensure_run_detail(plan_id, root=base, =, workstream=workstream)
    wb = worker_base or os.environ.get("FBE_CLOUD_WORKER_URL", "").strip() or "https://sourcea-fbe-runner-production.up.railway.app"
    return {
        "ok": True,
        "artifact": "worker_run_dashboard_slice",
        "artifact_path": str(store_path(plan_id, root=base).relative_to(base)),
        "preview_url": preview_url(plan_id, worker_base=wb),
        "run_detail": row,
    }
