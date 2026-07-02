#!/usr/bin/env python3
"""Ensure truth_log schema exists before L4 POST — probe + psycopg/management apply."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SQL_002 = ROOT / "infra/supabase/portfolio-spine/migrations/002_truth_log_v1.sql"
SQL_005 = ROOT / "infra/supabase/portfolio-spine/migrations/005_truth_log_external_verify_v1.sql"
SQL_006 = ROOT / "infra/supabase/portfolio-spine/migrations/006_mac_spine_bridge_v1.sql"
SQL_007 = ROOT / "infra/supabase/portfolio-spine/migrations/007_agent_session_cost_v1.sql"
MIGRATION_SQL = (SQL_002, SQL_005, SQL_006, SQL_007)


def _load_env_files() -> None:
    for path in (
        Path.home() / ".sourcea-secrets" / "portfolio-spine.env",
        Path.home() / ".sourcea-secrets" / "portfolio-spine-db.env",
    ):
        if not path.is_file():
            continue
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            if k and k not in os.environ:
                os.environ[k] = v.strip().strip('"').strip("'")


def _supabase_cfg() -> dict[str, str]:
    _load_env_files()
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
        or os.environ.get("SUPABASE_SERVICE_KEY", "").strip()
    )
    return {"url": url, "key": key, "ref": os.environ.get("SUPABASE_PROJECT_ID", "").strip()}


def _apply_via_psycopg(sql: str) -> dict[str, Any]:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import _apply_via_psycopg  # noqa: WPS433

    return _apply_via_psycopg(sql)


def probe_table(table: str) -> dict[str, Any]:
    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured", "table": table}
    req = urllib.request.Request(
        f"{cfg['url'].rstrip('/')}/rest/v1/{table}?select=id&limit=1",
        headers={
            "apikey": cfg["key"],
            "Authorization": f"Bearer {cfg['key']}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return {"ok": True, "http_code": resp.status, "table": table}
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "http_code": exc.code,
            "table": table,
            "error": exc.read().decode("utf-8", errors="replace")[:300],
        }
    except Exception as exc:
        return {"ok": False, "table": table, "error": str(exc)[:200]}


def probe_truth_log() -> dict[str, Any]:
    return probe_table("truth_log")


def apply_migrations(*, files: tuple[Path, ...] | None = None) -> dict[str, Any]:
    targets = files or MIGRATION_SQL
    results: list[dict[str, Any]] = []
    for sql_path in targets:
        if not sql_path.is_file():
            return {"ok": False, "error": f"missing_{sql_path.name}"}
        sql = sql_path.read_text(encoding="utf-8")
        row = _apply_via_psycopg(sql)
        results.append({"file": sql_path.name, **row})
        if not row.get("ok"):
            return {"ok": False, "results": results}
    reload = _apply_via_psycopg("NOTIFY pgrst, 'reload schema';")
    results.append({"file": "pgrst_reload", **reload})
    return {"ok": True, "results": results}


def ensure(*, apply: bool = True) -> dict[str, Any]:
    truth = probe_truth_log()
    mac_hb = probe_table("mac_agent_heartbeat")
    worker_inbox = probe_table("worker_inbox")
    spine_ok = truth.get("ok") and mac_hb.get("ok") and worker_inbox.get("ok")
    if spine_ok:
        return {
            "ok": True,
            "action": "probe_pass",
            "probe": {"truth_log": truth, "mac_agent_heartbeat": mac_hb, "worker_inbox": worker_inbox},
        }
    if not apply:
        return {
            "ok": False,
            "action": "probe_fail",
            "probe": {"truth_log": truth, "mac_agent_heartbeat": mac_hb, "worker_inbox": worker_inbox},
        }

    if not truth.get("ok"):
        mig = apply_migrations(files=MIGRATION_SQL)
    else:
        mig = apply_migrations(files=(SQL_006, SQL_007))

    truth2 = probe_truth_log()
    mac_hb2 = probe_table("mac_agent_heartbeat")
    worker_inbox2 = probe_table("worker_inbox")
    ok = bool(mig.get("ok")) and truth2.get("ok") and mac_hb2.get("ok") and worker_inbox2.get("ok")
    return {
        "ok": ok,
        "action": "migrate_then_probe",
        "probe_before": {"truth_log": truth, "mac_agent_heartbeat": mac_hb, "worker_inbox": worker_inbox},
        "migration": mig,
        "probe_after": {"truth_log": truth2, "mac_agent_heartbeat": mac_hb2, "worker_inbox": worker_inbox2},
        "hint": "Set SUPABASE_DB_URL or SUPABASE_DB_PASSWORD + SUPABASE_PROJECT_ID for psycopg apply",
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--probe-only", action="store_true")
    args = ap.parse_args()
    row = ensure(apply=not args.probe_only)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())

