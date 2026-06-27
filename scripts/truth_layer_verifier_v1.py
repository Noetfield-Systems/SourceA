#!/usr/bin/env python3
"""Truth Layer v1 — verify cycles from Supabase only (anti-theatre)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from typing import Any

from truth_layer_receipt_writer_v1 import REQUIRED_FIELDS, _contract_ok, _supabase_cfg

RUNTIME_EXECUTION_ID_KEYS = (
    "RAILWAY_DEPLOYMENT_INSTANCE_ID",
    "RAILWAY_REPLICA_ID",
    "RAILWAY_DEPLOYMENT_ID",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _runtime_execution_id() -> str:
    for key in RUNTIME_EXECUTION_ID_KEYS:
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return ""


def _fetch_supabase(*, select: str, filters: str = "", limit: int = 50) -> dict[str, Any]:
    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured", "rows": []}
    q = urllib.parse.urlencode({"select": select, "order": "created_at.desc", "limit": str(limit)})
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}?{q}{filters}"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Accept": "application/json",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
            if not isinstance(rows, list):
                rows = []
            return {"ok": True, "rows": rows, "status": resp.status}
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "error": exc.read().decode("utf-8", errors="replace")[:300],
            "status": exc.code,
            "rows": [],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "rows": []}


def verify_receipt_row(row: dict[str, Any]) -> dict[str, Any]:
    """Contract check — any missing field => FAIL."""
    missing = [f for f in REQUIRED_FIELDS if row.get(f) in (None, "")]
    contract_ok = _contract_ok(row) and not missing
    runtime_eid = _runtime_execution_id()
    eid = str(row.get("execution_id") or "")
    eid_match = bool(runtime_eid and eid and runtime_eid == eid)
    stored_verdict = str(row.get("verdict") or "")
    green = contract_ok and stored_verdict == "GREEN" and eid_match
    if not runtime_eid:
        green = contract_ok and stored_verdict == "GREEN"
        eid_match = None
    return {
        "schema": "truth-layer-verify-receipt-v1",
        "verdict": "GREEN" if green else "FAIL",
        "contract_ok": contract_ok,
        "missing_fields": missing,
        "execution_id_match": eid_match,
        "receipt_row_id": row.get("id"),
        "execution_id": eid,
        "cycle_id": row.get("cycle_id"),
        "stored_verdict": stored_verdict,
    }


def verify_last_cycle() -> dict[str, Any]:
    fetched = _fetch_supabase(select="*", limit=1)
    if not fetched.get("ok"):
        return {
            "schema": "truth-layer-verify-v1",
            "at": _now(),
            "verdict": "FAIL",
            "error": fetched.get("error") or "supabase_fetch_failed",
            "proof_source": "supabase",
        }
    rows = fetched.get("rows") or []
    if not rows:
        return {
            "schema": "truth-layer-verify-v1",
            "at": _now(),
            "verdict": "FAIL",
            "error": "no_receipts",
            "proof_source": "supabase",
        }
    check = verify_receipt_row(rows[0])
    check["schema"] = "truth-layer-verify-v1"
    check["at"] = _now()
    check["proof_source"] = "supabase"
    return check


def build_truth_status() -> dict[str, Any]:
    """GET /truth/status payload — Supabase is sole truth for display."""
    cfg = _supabase_cfg()
    fetched = _fetch_supabase(select="*", limit=100)
    rows = fetched.get("rows") or [] if fetched.get("ok") else []

    last_cycle = None
    last_verdict = "FAIL"
    last_success_at = None
    last_row_id = None
    last_execution_id = None

    if rows:
        last = rows[0]
        last_cycle = str(last.get("cycle_id") or "")
        check = verify_receipt_row(last)
        last_verdict = check.get("verdict") or "FAIL"
        last_row_id = last.get("id")
        last_execution_id = last.get("execution_id")
        if str(last.get("verdict") or "") == "GREEN" and check.get("contract_ok"):
            last_success_at = last.get("finished_at") or last.get("created_at")

    since = datetime.now(timezone.utc) - timedelta(hours=24)
    cycles_24h = 0
    for row in rows:
        created = row.get("created_at") or row.get("finished_at")
        if not created:
            continue
        try:
            ts = datetime.fromisoformat(str(created).replace("Z", "+00:00"))
            if ts >= since:
                cycles_24h += 1
        except ValueError:
            continue

    current_head = None
    try:
        from fbe.lib.cloud_forge_run_queue_v1 import read_head  # noqa: WPS433

        current_head = read_head().get("cloud_forge_run_head")
    except Exception:
        current_head = None

    display = "RED"
    if last_verdict == "GREEN" and last_row_id and last_execution_id:
        runtime_eid = _runtime_execution_id()
        if runtime_eid:
            display = "GREEN" if runtime_eid == last_execution_id else "RED"
        else:
            display = "GREEN"

    return {
        "last_cycle": last_cycle,
        "last_verdict": last_verdict,
        "cycles_24h": cycles_24h,
        "last_success_at": last_success_at,
        "current_head": current_head,
        "proof_source": "supabase",
        "display": display,
        "receipt_row_id": last_row_id,
        "execution_id": last_execution_id,
        "supabase_configured": bool(cfg["url"] and cfg["key"]),
        "supabase_ok": bool(fetched.get("ok")),
        "at": _now(),
        "schema": "truth-layer-status-v1",
    }
