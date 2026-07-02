#!/usr/bin/env python3
"""Query spine proof rows — L4 EXTERNAL_VERIFY_PASS + mac heartbeat + session cost."""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def _load_env() -> None:
    for path in (
        Path.home() / ".sourcea-secrets" / "portfolio-spine.env",
        Path.home() / ".sourcea-secrets" / "portfolio-spine-db.env",
    ):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            if k and k not in os.environ:
                os.environ[k] = v.strip().strip('"').strip("'")


def _cfg() -> dict[str, str]:
    _load_env()
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
        or os.environ.get("SUPABASE_ANON_KEY", "").strip()
    )
    return {"url": url, "key": key}


def _get(table: str, params: dict[str, str]) -> dict[str, Any]:
    cfg = _cfg()
    if not cfg["url"] or not cfg["key"]:
        return {
            "ok": False,
            "error": "supabase_not_configured",
            "hint": "Set SUPABASE_URL + SUPABASE_SERVICE_ROLE_KEY (or load ~/.sourcea-secrets/portfolio-spine.env). L4 POST also needs SUPABASE_DB_URL in CI for migrations 006+007.",
        }
    q = urllib.parse.urlencode(params)
    req = urllib.request.Request(
        f"{cfg['url'].rstrip('/')}/rest/v1/{table}?{q}",
        headers={"apikey": cfg["key"], "Authorization": f"Bearer {cfg['key']}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            rows = json.loads(resp.read().decode("utf-8", errors="replace"))
            return {"ok": True, "rows": rows if isinstance(rows, list) else []}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "error": exc.read().decode("utf-8", errors="replace")[:400], "status": exc.code}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200]}


def query_l4(*, days: int = 14) -> dict[str, Any]:
    since = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    fetched = _get(
        "truth_log",
        {
            "select": "id,recorded_at,event,source,receipt_id,payload",
            "event": "eq.EXTERNAL_VERIFY_PASS",
            "order": "recorded_at.desc",
            "limit": "1",
        },
    )
    rows = fetched.get("rows") or []
    row = rows[0] if rows else {}
    return {
        "l4_closed": bool(row),
        "truth_log_id": row.get("id"),
        "recorded_at": row.get("recorded_at"),
        "receipt_id": row.get("receipt_id"),
        "payload_keys": list((row.get("payload") or {}).keys()) if isinstance(row.get("payload"), dict) else [],
        "row": row,
        "since_filter": since,
        "fetch": fetched,
    }


def query_spine_live(*, agent_id: str = "cursor") -> dict[str, Any]:
    hb = _get(
        "mac_agent_heartbeat",
        {
            "select": "id,agent_id,repo,sha,dirty_count,at,recorded_at",
            "agent_id": f"eq.{agent_id}",
            "order": "at.desc",
            "limit": "1",
        },
    )
    hb_row = (hb.get("rows") or [{}])[0] if hb.get("ok") else {}
    last_at = str(hb_row.get("at") or hb_row.get("recorded_at") or "")
    stale = True
    if last_at:
        try:
            ts = last_at.replace("Z", "+00:00")
            age_min = (datetime.now(timezone.utc) - datetime.fromisoformat(ts)).total_seconds() / 60.0
            stale = age_min > 30
        except ValueError:
            pass

    cost = _get(
        "truth_log",
        {
            "select": "id,recorded_at,event,payload",
            "event": "eq.AGENT_SESSION_COST",
            "order": "recorded_at.desc",
            "limit": "1",
        },
    )
    cost_row = (cost.get("rows") or [{}])[0] if cost.get("ok") else {}

    return {
        "heartbeat": {
            "row": hb_row,
            "dashboard_status": "STALE_DATA" if stale or not hb_row else "OK",
            "fetch_ok": hb.get("ok"),
            "table_missing_hint": hb.get("status") == 404 or "mac_agent_heartbeat" in str(hb.get("error", "")),
        },
        "session_cost": {
            "truth_log_id": cost_row.get("id"),
            "row": cost_row,
            "fetch_ok": cost.get("ok"),
        },
        "migration_hint": "Apply scripts/apply_portfolio_spine_migrations_v1.sh (006+007) when SUPABASE_DB_URL set",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--agent-id", default="cursor")
    args = ap.parse_args()
    row = {
        "schema": "spine-proof-query-v1",
        "at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "l4": query_l4(),
        "spine": query_spine_live(agent_id=args.agent_id),
    }
    if args.json:
        print(json.dumps(row, indent=2, ensure_ascii=False))
    else:
        print(json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
