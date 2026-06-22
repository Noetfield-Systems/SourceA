#!/usr/bin/env python3
"""Real cloud slice — competitor evidence dispatch (Architecture A).

GET /api/competitor-evidence/v1?plan_id=CLOUD-SEC-037
Stable artifact: receipts/cloud-dispatch/{plan_id}.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[1]
STORE_DIR = "receipts/cloud-dispatch"


def store_path(plan_id: str, *, root: Path | None = None) -> Path:
    base = root or ROOT
    safe = "".join(c if c.isalnum() or c in "-_" else "_" for c in plan_id)
    return base / STORE_DIR / f"{safe}.json"


def plan_row_to_dispatch(plan_id: str, plan_row: dict[str, Any]) -> dict[str, Any]:
    """Map forge plan row → cloud_worker_dispatch plan dict."""
    meta = plan_row.get("metadata") if isinstance(plan_row.get("metadata"), dict) else {}
    inputs = plan_row.get("inputs") if isinstance(plan_row.get("inputs"), dict) else {}
    return {
        "id": plan_id,
        "plane": str(inputs.get("plane") or plan_row.get("plane") or "cloud_forge"),
        "competitor": str(meta.get("competitor") or inputs.get("competitor") or "Trigger.dev"),
        "workstream": str(meta.get("workstream") or inputs.get("workstream") or "ws-ux"),
        "tier": meta.get("tier") or inputs.get("tier"),
        "maps_registry": meta.get("maps_registry") or inputs.get("maps_registry"),
        "cloud_action": str(inputs.get("action") or plan_row.get("cloud_action") or ""),
    }


def get_evidence(plan_id: str, *, root: Path | None = None) -> dict[str, Any] | None:
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
    parsed = urlparse(path)
    if parsed.path not in ("/api/competitor-evidence/v1", "/api/competitor-evidence/v1/"):
        return 404, {"ok": False, "error": "not_found"}
    qs = parse_qs(parsed.query)
    plan_id = (qs.get("plan_id") or [""])[0].strip()
    if not plan_id:
        return 400, {"ok": False, "error": "plan_id_required"}
    row = get_evidence(plan_id, root=root)
    if not row:
        return 404, {"ok": False, "error": "evidence_not_found", "plan_id": plan_id}
    return 200, {"ok": True, **row}


def preview_url(plan_id: str, *, worker_base: str) -> str:
    return f"{worker_base.rstrip('/')}/api/competitor-evidence/v1?plan_id={plan_id}"


def ship_evidence_for_plan(
    plan_id: str,
    plan_row: dict[str, Any],
    *,
    root: Path | None = None,
    worker_base: str = "",
) -> dict[str, Any]:
    """Run competitor fetch + write stable plan_id receipt on cloud volume."""
    import sys

    base = root or ROOT
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_worker_dispatch_v1 import _run_cloud_plan  # noqa: WPS433

    plan = plan_row_to_dispatch(plan_id, plan_row)
    receipt = _run_cloud_plan(plan)
    ok = bool(receipt.get("ok")) and receipt.get("status") == "PASS"
    snippets = receipt.get("evidence_snippets") or []

    canonical = dict(receipt)
    canonical["canonical_plan_receipt"] = True
    canonical["receipt_url"] = f"/receipts/cloud-dispatch/{plan_id}.json"
    canonical_path = store_path(plan_id, root=base)
    canonical_path.parent.mkdir(parents=True, exist_ok=True)
    canonical_path.write_text(json.dumps(canonical, indent=2) + "\n", encoding="utf-8")

    wb = worker_base or os.environ.get("FBE_CLOUD_WORKER_URL", "").strip() or "https://sourcea-fbe-runner-production.up.railway.app"
    return {
        "ok": ok and bool(snippets),
        "artifact": "competitor_evidence_slice",
        "artifact_path": str(canonical_path.relative_to(base)),
        "preview_url": preview_url(plan_id, worker_base=wb),
        "dispatch_receipt": receipt,
        "evidence_snippets": snippets,
        "source_url": receipt.get("source_url"),
    }
