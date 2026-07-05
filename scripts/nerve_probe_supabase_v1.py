#!/usr/bin/env python3
"""Nerve probe Supabase wire — migration 013 + table probe (SourceA portfolio-spine)."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MIGRATION = ROOT / "infra/supabase/portfolio-spine/migrations/013_improvement_queue_v1.sql"
TABLES = ("improvement_queue", "nf_intake_submissions", "nerve_probe_receipts")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_secrets() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import ensure_env  # noqa: WPS433

    ensure_env()


def _tables_probe() -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import table_probe  # noqa: WPS433

    rows = {t: table_probe(cfg={"url": os.environ.get("SUPABASE_URL", ""), "key": os.environ.get("SUPABASE_SERVICE_ROLE_KEY", ""), "table": t}) for t in TABLES}
    ok = all(r.get("exists") for r in rows.values())
    return {"ok": ok, "tables": rows}


def apply_migration() -> dict[str, Any]:
    _load_secrets()
    probe = _tables_probe()
    if probe.get("ok"):
        return {"ok": True, "skipped": True, "reason": "tables_exist", "probe": probe}
    if not MIGRATION.is_file():
        return {"ok": False, "error": "migration_missing", "path": str(MIGRATION)}
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import _apply_via_management_api, _apply_via_psycopg  # noqa: WPS433

    sql = MIGRATION.read_text(encoding="utf-8")
    pg = _apply_via_psycopg(sql)
    if pg.get("ok"):
        return {**pg, "migration": "013_improvement_queue_v1", "probe_after": _tables_probe()}
    mgmt = _apply_via_management_api(sql)
    if mgmt.get("ok"):
        return {**mgmt, "migration": "013_improvement_queue_v1", "probe_after": _tables_probe()}
    return {"ok": False, "migration": "013_improvement_queue_v1", "psycopg": pg, "management": mgmt}


def query_recent(*, limit: int = 10) -> dict[str, Any]:
    _load_secrets()
    url = os.environ.get("SUPABASE_URL", "").rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")
    if not url or not key:
        return {"ok": False, "error": "supabase_not_configured"}
    import urllib.request

    out: dict[str, Any] = {"ok": True, "at": _now(), "rows": {}}
    for table in TABLES:
        req = urllib.request.Request(
            f"{url}/rest/v1/{table}?select=*&order=recorded_at.desc.nullslast,created_at.desc&limit={limit}",
            headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=25) as resp:
                out["rows"][table] = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            out["ok"] = False
            out["rows"][table] = {"error": str(exc)[:200]}
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--apply-migration", action="store_true")
    ap.add_argument("--probe", action="store_true")
    ap.add_argument("--query", action="store_true")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if args.apply_migration:
        row = apply_migration()
    elif args.query:
        row = query_recent(limit=args.limit)
    else:
        _load_secrets()
        row = _tables_probe()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
