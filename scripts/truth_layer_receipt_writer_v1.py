#!/usr/bin/env python3
"""Truth Layer v1 — write cycle_receipts to Supabase (objective evidence only)."""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_FIELDS = (
    "cycle_id",
    "execution_id",
    "queue_head_before",
    "queue_head_after",
    "started_at",
    "finished_at",
    "duration_ms",
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _supabase_cfg() -> dict[str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    table = os.environ.get("TRUTH_CYCLE_RECEIPTS_TABLE", "cycle_receipts").strip()
    fallback = os.environ.get("TRUTH_CYCLE_RECEIPTS_FALLBACK_TABLE", "telemetry_logs").strip()
    return {"url": url, "key": key, "table": table or "cycle_receipts", "fallback_table": fallback or "telemetry_logs"}


def _parse_ts(raw: str) -> datetime | None:
    text = (raw or "").strip()
    if not text:
        return None
    try:
        if text.endswith("Z"):
            text = text[:-1] + "+00:00"
        return datetime.fromisoformat(text)
    except ValueError:
        return None


def _contract_ok(row: dict[str, Any]) -> bool:
    for field in REQUIRED_FIELDS:
        val = row.get(field)
        if val is None or val == "":
            return False
    if not isinstance(row.get("duration_ms"), int) or row["duration_ms"] < 0:
        return False
    if _parse_ts(str(row.get("started_at") or "")) is None:
        return False
    if _parse_ts(str(row.get("finished_at") or "")) is None:
        return False
    return True


ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "infra/supabase/portfolio-spine/migrations/001_truth_layer_cycle_receipts_v1.sql"


def _apply_truth_migration_if_missing() -> dict[str, Any]:
    if not MIGRATION.is_file():
        return {"ok": False, "error": "migration_missing"}
    try:
        from cloud_forge_run_supabase_v1 import (  # noqa: WPS433
            _apply_via_management_api,
            _apply_via_psycopg,
            ensure_env,
            table_probe,
        )

        ensure_env()
        cfg = _supabase_cfg()
        probe = table_probe(cfg={**cfg, "table": cfg["table"]})
        if probe.get("exists"):
            return {"ok": True, "skipped": True, "reason": "table_exists"}
        sql = MIGRATION.read_text(encoding="utf-8")
        for fn in (_apply_via_management_api, _apply_via_psycopg):
            result = fn(sql)
            if result.get("ok"):
                return result
        return {"ok": False, "error": "truth_migration_not_applied", "migration_path": str(MIGRATION)}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _post_json_row(*, cfg: dict[str, str], table: str, row: dict[str, Any]) -> dict[str, Any]:
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{table}"
    req = urllib.request.Request(
        url,
        data=json.dumps(row).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Prefer": "return=representation",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        body = resp.read().decode("utf-8", errors="replace")
        inserted = json.loads(body) if body.strip().startswith("[") else json.loads(body or "{}")
        if isinstance(inserted, list) and inserted:
            inserted = inserted[0]
        receipt_id = inserted.get("id") if isinstance(inserted, dict) else None
        return {"ok": 200 <= resp.status < 300 and bool(receipt_id), "receipt_row_id": receipt_id, "status": resp.status}


def _write_telemetry_fallback(
    row: dict[str, Any],
    *,
    cfg: dict[str, str],
    verdict: str,
    contract_complete: bool,
    cycle_id: str,
    execution_id: str,
) -> dict[str, Any]:
    """Portfolio-spine fallback when cycle_receipts migration not yet applied (DDL needs DB password)."""
    fb = cfg.get("fallback_table") or "telemetry_logs"
    payload_row = {
        "content": f"truth cycle {row.get('cycle_id')}",
        "memory_type": "truth_cycle_receipt",
        "metadata": {
            **row,
            "schema": "truth-layer-receipt-v1",
            "fallback_from": cfg["table"],
            "verdict": verdict,
        },
    }
    try:
        posted = _post_json_row(cfg=cfg, table=fb, row=payload_row)
        receipt_id = posted.get("receipt_row_id")
        return {
            "ok": bool(posted.get("ok")),
            "schema": "truth-layer-receipt-write-v1",
            "at": _now(),
            "verdict": verdict,
            "contract_complete": contract_complete,
            "receipt_row_id": receipt_id,
            "execution_id": execution_id,
            "cycle_id": cycle_id,
            "supabase_status": posted.get("status"),
            "storage_table": fb,
            "fallback": True,
        }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "schema": "truth-layer-receipt-write-v1",
            "at": _now(),
            "verdict": "FAIL",
            "contract_complete": contract_complete,
            "error": exc.read().decode("utf-8", errors="replace")[:300],
            "supabase_status": exc.code,
            "storage_table": fb,
            "fallback": True,
        }
    except Exception as exc:
        return {
            "ok": False,
            "schema": "truth-layer-receipt-write-v1",
            "at": _now(),
            "verdict": "FAIL",
            "contract_complete": contract_complete,
            "error": str(exc)[:200],
            "storage_table": fb,
            "fallback": True,
        }


def write_cycle_receipt(
    *,
    cycle_id: str,
    execution_id: str,
    queue_head_before: str,
    queue_head_after: str,
    started_at: str,
    finished_at: str,
    duration_ms: int,
    trigger_source: str,
    job_ok: bool,
) -> dict[str, Any]:
    """Insert one cycle_receipts row. verdict=GREEN only if job_ok and contract complete."""
    row = {
        "cycle_id": str(cycle_id or "").strip(),
        "execution_id": str(execution_id or "").strip(),
        "queue_head_before": str(queue_head_before or "").strip(),
        "queue_head_after": str(queue_head_after or "").strip(),
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_ms": max(0, int(duration_ms)),
        "trigger_source": str(trigger_source or "unknown").strip() or "unknown",
    }
    contract_complete = _contract_ok(row)
    verdict = "GREEN" if (job_ok and contract_complete) else "FAIL"
    row["verdict"] = verdict

    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {
            "ok": False,
            "schema": "truth-layer-receipt-write-v1",
            "at": _now(),
            "verdict": "FAIL",
            "error": "supabase_not_configured",
            "contract_complete": contract_complete,
            "row": row,
        }

    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}"
    payload = json.dumps(row).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Prefer": "return=representation",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            inserted = json.loads(body) if body.strip().startswith("[") else json.loads(body or "{}")
            if isinstance(inserted, list) and inserted:
                inserted = inserted[0]
            receipt_id = inserted.get("id") if isinstance(inserted, dict) else None
            return {
                "ok": 200 <= resp.status < 300 and bool(receipt_id),
                "schema": "truth-layer-receipt-write-v1",
                "at": _now(),
                "verdict": verdict,
                "contract_complete": contract_complete,
                "receipt_row_id": receipt_id,
                "execution_id": execution_id,
                "cycle_id": cycle_id,
                "supabase_status": resp.status,
            }
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        if exc.code in (404, 400) and ("42P01" in err or "does not exist" in err.lower() or "PGRST205" in err):
            applied = _apply_truth_migration_if_missing()
            if applied.get("ok") and applied.get("applied"):
                return write_cycle_receipt(
                    cycle_id=cycle_id,
                    execution_id=execution_id,
                    queue_head_before=queue_head_before,
                    queue_head_after=queue_head_after,
                    started_at=started_at,
                    finished_at=finished_at,
                    duration_ms=duration_ms,
                    trigger_source=trigger_source,
                    job_ok=job_ok,
                )
            return _write_telemetry_fallback(
                row,
                cfg=cfg,
                verdict=verdict,
                contract_complete=contract_complete,
                cycle_id=cycle_id,
                execution_id=execution_id,
            )
        return {
            "ok": False,
            "schema": "truth-layer-receipt-write-v1",
            "at": _now(),
            "verdict": "FAIL",
            "contract_complete": contract_complete,
            "error": err[:300],
            "supabase_status": exc.code,
        }
    except Exception as exc:
        return {
            "ok": False,
            "schema": "truth-layer-receipt-write-v1",
            "at": _now(),
            "verdict": "FAIL",
            "contract_complete": contract_complete,
            "error": str(exc)[:200],
        }


def finalize_proceed_truth(
    payload: dict[str, Any],
    *,
    started_at: str,
    started_mono: float,
    cycle_id: str,
    execution_id: str,
    queue_head_before: str,
    trigger_source: str,
    queue_head_after: str | None = None,
) -> dict[str, Any]:
    import time

    finished_at = _now()
    duration_ms = max(0, int((time.perf_counter() - started_mono) * 1000))
    if queue_head_after is None:
        queue_head_after = queue_head_before
        try:
            from fbe.lib.cloud_forge_run_queue_v1 import read_head  # noqa: WPS433

            queue_head_after = str(read_head().get("cloud_forge_run_head") or queue_head_before)
        except Exception:
            pass

    truth = write_cycle_receipt(
        cycle_id=cycle_id,
        execution_id=execution_id,
        queue_head_before=queue_head_before,
        queue_head_after=queue_head_after,
        started_at=started_at,
        finished_at=finished_at,
        duration_ms=duration_ms,
        trigger_source=trigger_source,
        job_ok=bool(payload.get("ok")),
    )
    out = dict(payload)
    out["truth_layer"] = truth
    out["execution_id"] = execution_id
    out["cycle_id"] = cycle_id
    out["truth_verdict"] = truth.get("verdict")
    out["receipt_row_id"] = truth.get("receipt_row_id")
    return out


def execution_id_from_env() -> str:
    import uuid

    for key in ("RAILWAY_DEPLOYMENT_INSTANCE_ID", "RAILWAY_REPLICA_ID", "RAILWAY_DEPLOYMENT_ID"):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return str(uuid.uuid4())
