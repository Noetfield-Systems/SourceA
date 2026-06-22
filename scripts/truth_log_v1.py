#!/usr/bin/env python3
"""Truth Layer v2 — TRUTH_LOG in Supabase (cloud writers only · independent verifier).

Writers: Cloudflare cron/worker · Railway runtime (/app headless).
Forbidden: Mac · Cursor · local scripts (blocked before HTTP + RLS has no INSERT policy).
"""
from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any

TRUTH_EVENTS = frozenset(
    {
        "CRON_FIRED",
        "JOB_STARTED",
        "JOB_COMPLETED",
        "JOB_FAILED",
        "QUEUE_ADVANCED",
    }
)
TRUTH_SOURCES = frozenset(
    {
        "cloudflare_cron",
        "cloudflare_worker",
        "railway_runtime",
    }
)


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _supabase_cfg() -> dict[str, str]:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    table = os.environ.get("TRUTH_LOG_TABLE", "truth_log").strip() or "truth_log"
    return {"url": url, "key": key, "table": table}


def _deployment_id() -> str:
    for key in (
        "RAILWAY_DEPLOYMENT_ID",
        "RAILWAY_DEPLOYMENT_INSTANCE_ID",
        "RAILWAY_REPLICA_ID",
    ):
        val = os.environ.get(key, "").strip()
        if val:
            return val
    return ""


def _railway_runtime() -> bool:
    if os.environ.get("RAILWAY_ENVIRONMENT") or os.environ.get("RAILWAY_SERVICE_NAME"):
        return True
    if str(os.environ.get("FBE_MODE", "")).lower() == "headless" and os.environ.get("FBE_HOME", "").strip() == "/app":
        return True
    return False


def cloud_writer_allowed(*, source: str) -> bool:
    """Mac/Cursor/local terminal must never pass."""
    if source not in TRUTH_SOURCES:
        return False
    if source == "railway_runtime":
        return _railway_runtime()
    return False


def _row_to_api(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": row.get("id"),
        "timestamp": row.get("recorded_at"),
        "source": row.get("source"),
        "event": row.get("event"),
        "deployment_id": row.get("deployment_id"),
        "queue_head": row.get("queue_head"),
        "old_queue_head": row.get("old_queue_head"),
        "receipt_id": row.get("receipt_id"),
    }


def write_truth_event(
    event: str,
    *,
    source: str = "railway_runtime",
    queue_head: str | None = None,
    old_queue_head: str | None = None,
    receipt_id: str | None = None,
    deployment_id: str | None = None,
) -> dict[str, Any]:
    event = str(event or "").strip().upper()
    source = str(source or "").strip().lower()
    if event not in TRUTH_EVENTS:
        return {"ok": False, "error": "invalid_event", "event": event}
    if not cloud_writer_allowed(source=source):
        return {"ok": False, "error": "forbidden_non_cloud_writer", "source": source}

    row: dict[str, Any] = {
        "source": source,
        "event": event,
        "deployment_id": (deployment_id or _deployment_id()) or None,
        "queue_head": (queue_head or None) if queue_head else None,
        "old_queue_head": (old_queue_head or None) if old_queue_head else None,
        "receipt_id": (receipt_id or None) if receipt_id else None,
    }
    if event == "QUEUE_ADVANCED" and not (old_queue_head and queue_head):
        return {"ok": False, "error": "queue_advanced_requires_old_and_new_head"}

    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured", "event": event}

    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}"
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
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            inserted: Any = json.loads(body) if body.strip() else {}
            if isinstance(inserted, list) and inserted:
                inserted = inserted[0]
            row_id = inserted.get("id") if isinstance(inserted, dict) else None
            return {
                "ok": 200 <= resp.status < 300 and bool(row_id),
                "truth_log_id": row_id,
                "event": event,
                "source": source,
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "error": exc.read().decode("utf-8", errors="replace")[:300],
            "status": exc.code,
            "event": event,
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "event": event}


def write_queue_advanced(*, old_head: str, new_head: str, receipt_id: str | None = None) -> dict[str, Any]:
    return write_truth_event(
        "QUEUE_ADVANCED",
        source="railway_runtime",
        queue_head=str(new_head),
        old_queue_head=str(old_head),
        receipt_id=receipt_id,
    )


def _fetch_rows(*, event: str | None = None, limit: int = 1) -> dict[str, Any]:
    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured", "rows": []}
    params: dict[str, str] = {
        "select": "*",
        "order": "recorded_at.desc",
        "limit": str(max(1, min(limit, 200))),
    }
    if event:
        params["event"] = f"eq.{event}"
    q = urllib.parse.urlencode(params)
    url = f"{cfg['url'].rstrip('/')}/rest/v1/{cfg['table']}?{q}"
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
            return {"ok": True, "rows": rows}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error": exc.read().decode("utf-8", errors="replace")[:300], "rows": []}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "rows": []}


def _minutes_since(ts_raw: str | None) -> float | None:
    if not ts_raw:
        return None
    try:
        text = str(ts_raw).replace("Z", "+00:00")
        ts = datetime.fromisoformat(text)
        if ts.tzinfo is None:
            ts = ts.replace(tzinfo=timezone.utc)
        delta = datetime.now(timezone.utc) - ts.astimezone(timezone.utc)
        return round(delta.total_seconds() / 60.0, 2)
    except ValueError:
        return None


def _last_event_row(event: str) -> dict[str, Any] | None:
    fetched = _fetch_rows(event=event, limit=1)
    if not fetched.get("ok"):
        return None
    rows = fetched.get("rows") or []
    if not rows:
        return None
    return _row_to_api(rows[0])


def build_truth() -> dict[str, Any]:
    """GET /truth — last row per category from Supabase only."""
    cron_events = ("CRON_FIRED",)
    job_events = ("JOB_COMPLETED", "JOB_STARTED")
    cfg = _supabase_cfg()
    supabase_ok = bool(cfg["url"] and cfg["key"])

    last_cron = _last_event_row("CRON_FIRED")
    last_job = _last_event_row("JOB_COMPLETED") or _last_event_row("JOB_STARTED")
    last_queue_advance = _last_event_row("QUEUE_ADVANCED")
    last_failure = _last_event_row("JOB_FAILED")

    return {
        "schema": "truth-log-summary-v1",
        "at": _now(),
        "proof_source": "supabase_truth_log",
        "supabase_configured": supabase_ok,
        "last_cron": last_cron,
        "last_job": last_job,
        "last_queue_advance": last_queue_advance,
        "last_failure": last_failure,
    }


def build_truth_live() -> dict[str, Any]:
    """GET /truth/live — minutes since last cloud events."""
    summary = build_truth()
    last_cron = summary.get("last_cron") or {}
    last_job = summary.get("last_job") or {}
    last_q = summary.get("last_queue_advance") or {}

    return {
        "schema": "truth-log-live-v1",
        "at": _now(),
        "proof_source": "supabase_truth_log",
        "supabase_configured": summary.get("supabase_configured"),
        "minutes_since_last_cron": _minutes_since(last_cron.get("timestamp")),
        "minutes_since_last_job": _minutes_since(last_job.get("timestamp")),
        "minutes_since_last_queue_advance": _minutes_since(last_q.get("timestamp")),
        "last_cron": last_cron,
        "last_job": last_job,
        "last_queue_advance": last_q,
    }


def emit_job_lifecycle(
    payload: dict[str, Any],
    ctx: dict[str, Any],
) -> None:
    """Railway-only: JOB_COMPLETED/FAILED + optional QUEUE_ADVANCED."""
    if not ctx.get("active"):
        return
    event = "JOB_COMPLETED" if payload.get("ok") else "JOB_FAILED"
    receipt_id = str(
        payload.get("receipt_row_id")
        or payload.get("cycle_receipt_path")
        or payload.get("cycle_id")
        or ctx.get("cycle_id")
        or ""
    ).strip() or None
    queue_after = str(ctx.get("queue_head_before") or "")
    try:
        from fbe.lib.cloud_drain_queue_v1 import read_head  # noqa: WPS433

        queue_after = str(read_head().get("cloud_drain_head") or queue_after)
    except Exception:
        pass

    write_truth_event(
        event,
        source="railway_runtime",
        queue_head=queue_after or None,
        receipt_id=receipt_id,
        deployment_id=str(ctx.get("execution_id") or "") or None,
    )

    before = str(ctx.get("queue_head_before") or "")
    if before and queue_after and before != queue_after:
        write_queue_advanced(
            old_head=before,
            new_head=queue_after,
            receipt_id=receipt_id,
        )


def emit_job_started(ctx: dict[str, Any]) -> None:
    if not ctx.get("active"):
        return
    write_truth_event(
        "JOB_STARTED",
        source="railway_runtime",
        queue_head=str(ctx.get("queue_head_before") or "") or None,
        deployment_id=str(ctx.get("execution_id") or "") or None,
        receipt_id=str(ctx.get("cycle_id") or "") or None,
    )
