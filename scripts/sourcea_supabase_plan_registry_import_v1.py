#!/usr/bin/env python3
"""Import SourceA plan registry rows into portfolio-spine Supabase.

Default behavior is safe: --check and --dry-run do not write rows.
Use --import after the table exists and service/server key is present.
"""
from __future__ import annotations

import argparse
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CHAIN = ROOT / "data/sourcea-supabase-plan-registry-chain-v1.json"
BACKLOG = ROOT / "data/all-remaining-plan-backlog-v1.json"
RECEIPT = Path.home() / ".sina/sourcea-supabase-plan-registry-import-v1.json"
SECRETS = Path.home() / ".sourcea-secrets/portfolio-spine.env"
DB_SECRETS = Path.home() / ".sourcea-secrets/portfolio-spine-db.env"


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def load_env_file(path: Path) -> dict[str, str]:
    out: dict[str, str] = {}
    if not path.is_file():
        return out
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        out[key.strip()] = val.strip().strip('"').strip("'")
    return out


def load_cfg() -> dict[str, str]:
    env = {}
    env.update(load_env_file(SECRETS))
    env.update(load_env_file(DB_SECRETS))
    for key in (
        "SUPABASE_URL",
        "SUPABASE_ANON_KEY",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_SERVICE_KEY",
        "SUPABASE_DB_PASSWORD",
        "SUPABASE_DB_URL",
        "DATABASE_URL",
        "SUPABASE_ACCESS_TOKEN",
        "SUPABASE_PAT",
    ):
        if os.environ.get(key):
            env[key] = os.environ[key]
    return env


def public_cfg(cfg: dict[str, str]) -> dict[str, Any]:
    def real(key: str) -> bool:
        val = str(cfg.get(key) or "").strip()
        return bool(val) and "YOUR_" not in val and "PASTE" not in val.upper() and "PLACEHOLDER" not in val.upper()

    return {
        "supabase_url": real("SUPABASE_URL"),
        "anon_key": real("SUPABASE_ANON_KEY"),
        "service_key": real("SUPABASE_SERVICE_ROLE_KEY") or real("SUPABASE_SERVICE_KEY"),
        "db_password": real("SUPABASE_DB_PASSWORD"),
        "db_url": real("SUPABASE_DB_URL") or real("DATABASE_URL"),
        "management_token": real("SUPABASE_ACCESS_TOKEN") or real("SUPABASE_PAT"),
    }


def normalize_item(item: dict[str, Any]) -> dict[str, Any]:
    plan_id = str(item.get("plan_id") or item.get("id") or "").strip()
    title = str(item.get("title") or item.get("name") or plan_id).strip()
    source_registry = str(item.get("source_registry") or item.get("registry") or "")
    source_path = str(item.get("prompt_path") or item.get("path") or "")
    priority_rank = item.get("priority_rank")
    try:
        priority_rank = int(priority_rank) if priority_rank is not None else None
    except (TypeError, ValueError):
        priority_rank = None
    return {
        "plan_id": plan_id,
        "title": title,
        "status": str(item.get("status") or "") or None,
        "tier": str(item.get("tier") or "") or None,
        "lane": str(item.get("lane") or "") or None,
        "phase": str(item.get("phase") or "") or None,
        "workstream": str(item.get("workstream") or "") or None,
        "priority": str(item.get("priority") or "") or None,
        "priority_rank": priority_rank,
        "source_registry": source_registry or None,
        "source_schema": str(item.get("source_schema") or "") or None,
        "prompt_path": str(item.get("prompt_path") or "") or None,
        "source_path": source_path or source_registry or None,
        "payload": item,
        "updated_at": now(),
    }


def load_rows(limit: int = 0) -> list[dict[str, Any]]:
    row = json.loads(BACKLOG.read_text(encoding="utf-8"))
    items = row.get("items") or []
    rows = [normalize_item(item) for item in items if isinstance(item, dict)]
    rows = [row for row in rows if row["plan_id"] and row["title"]]
    return rows[:limit] if limit else rows


def request_json(url: str, *, method: str, headers: dict[str, str], body: Any | None = None) -> dict[str, Any]:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            parsed = json.loads(raw) if raw.strip() else None
            return {"ok": 200 <= resp.status < 300, "status": resp.status, "body": parsed}
    except urllib.error.HTTPError as exc:
        err = exc.read().decode("utf-8", errors="replace")
        return {"ok": False, "status": exc.code, "error": err[:500]}
    except Exception as exc:
        return {"ok": False, "status": 0, "error": str(exc)[:300]}


def table_probe(cfg: dict[str, str]) -> dict[str, Any]:
    base = str(cfg.get("SUPABASE_URL") or "").rstrip("/")
    key = str(cfg.get("SUPABASE_SERVICE_ROLE_KEY") or cfg.get("SUPABASE_SERVICE_KEY") or cfg.get("SUPABASE_ANON_KEY") or "")
    if not base or not key:
        return {"ok": False, "exists": False, "error": "missing_supabase_url_or_key"}
    url = f"{base}/rest/v1/sourcea_plan_registry?{urllib.parse.urlencode({'select': 'plan_id', 'limit': '1'})}"
    row = request_json(
        url,
        method="GET",
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    missing = row.get("status") == 404 or "PGRST" in str(row.get("error") or "")
    return {**row, "exists": bool(row.get("ok")) and not missing}


def upsert_rows(cfg: dict[str, str], rows: list[dict[str, Any]], *, batch_size: int = 500) -> dict[str, Any]:
    base = str(cfg.get("SUPABASE_URL") or "").rstrip("/")
    key = str(cfg.get("SUPABASE_SERVICE_ROLE_KEY") or cfg.get("SUPABASE_SERVICE_KEY") or "")
    if not base or not key:
        return {"ok": False, "error": "missing_service_key"}
    total = 0
    errors = []
    url = f"{base}/rest/v1/sourcea_plan_registry?on_conflict=plan_id"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "Prefer": "resolution=merge-duplicates",
    }
    for i in range(0, len(rows), batch_size):
        batch = rows[i : i + batch_size]
        res = request_json(url, method="POST", headers=headers, body=batch)
        if not res.get("ok"):
            errors.append({"offset": i, "status": res.get("status"), "error": res.get("error")})
            break
        total += len(batch)
    return {"ok": not errors, "imported": total, "errors": errors[:3]}


def run(*, check: bool, do_import: bool, limit: int) -> dict[str, Any]:
    cfg = load_cfg()
    rows = load_rows(limit=limit)
    probe = table_probe(cfg)
    result: dict[str, Any] = {
        "schema": "sourcea-supabase-plan-registry-import-receipt-v1",
        "at": now(),
        "chain": str(CHAIN.relative_to(ROOT)),
        "source": str(BACKLOG.relative_to(ROOT)),
        "loaded_rows": len(rows),
        "secrets": public_cfg(cfg),
        "table_probe": probe,
        "mode": "check" if check and not do_import else "import" if do_import else "dry_run",
        "next": None,
    }
    if do_import:
        if not probe.get("exists"):
            result["ok"] = False
            result["next"] = "Apply infra/supabase/portfolio-spine/migrations/004_sourcea_plan_registry_v1.sql first."
        else:
            result["import"] = upsert_rows(cfg, rows)
            result["ok"] = bool(result["import"].get("ok"))
    else:
        result["ok"] = bool(probe.get("exists"))
        result["next"] = None if result["ok"] else "Table missing. Apply migration SQL or add DB credentials."
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    result["receipt"] = str(RECEIPT)
    return result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--import", dest="do_import", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run(check=args.check, do_import=args.do_import, limit=args.limit)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(("OK" if row.get("ok") else "BLOCK") + f" rows={row['loaded_rows']} receipt={row['receipt']}")
    return 0 if row.get("ok") or (args.check and row["table_probe"].get("status") in (404, 401, 403)) else 1


if __name__ == "__main__":
    raise SystemExit(main())
