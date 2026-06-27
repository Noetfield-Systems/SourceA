#!/usr/bin/env python3
"""Read SourceA plan registry rows from portfolio-spine Supabase."""
from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request
import argparse
from pathlib import Path
from typing import Any

SECRETS = Path.home() / ".sourcea-secrets/portfolio-spine.env"
TABLE = "sourcea_plan_registry"
PUBLIC_SELECT = "plan_id,title,status,tier,lane,phase,workstream,priority,priority_rank,source_registry,prompt_path,updated_at"
DETAIL_SELECT = f"{PUBLIC_SELECT},payload"
SECRET_PATTERNS = [
    re.compile(r"SUPABASE_(?:SERVICE|DB|ANON|URL|PASSWORD|KEY)", re.I),
    re.compile(r"service[_-]?role", re.I),
    re.compile(r"postgres(?:ql)?://", re.I),
    re.compile(r"sb_secret_", re.I),
    re.compile(r"eyJ[A-Za-z0-9_-]{20,}"),
]


def _load_env_file(path: Path) -> dict[str, str]:
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


def _cfg() -> dict[str, str]:
    env = _load_env_file(SECRETS)
    for key in ("SUPABASE_URL", "SUPABASE_ANON_KEY", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_SERVICE_KEY"):
        if os.environ.get(key):
            env[key] = os.environ[key]
    return env


def _request(path: str, params: dict[str, str], *, service: bool = False) -> dict[str, Any]:
    cfg = _cfg()
    base = str(cfg.get("SUPABASE_URL") or "").rstrip("/")
    if service:
        key = str(cfg.get("SUPABASE_SERVICE_ROLE_KEY") or cfg.get("SUPABASE_SERVICE_KEY") or "")
        auth_mode = "service"
    else:
        key = str(cfg.get("SUPABASE_ANON_KEY") or "")
        auth_mode = "anon"
    if not base or not key:
        return {"ok": False, "error": "supabase_not_configured", "rows": [], "auth_mode": auth_mode}

    url = f"{base}/rest/v1/{path}?{urllib.parse.urlencode(params, safe='(),.*')}"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
            "Prefer": "count=exact",
            "Range": f"{params.get('offset', '0')}-{int(params.get('offset', '0')) + int(params.get('limit', '1')) - 1}" if params.get("limit") else "0-0",
        },
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            rows = json.loads(raw) if raw.strip() else []
            total: int | None = None
            content_range = resp.headers.get("Content-Range", "")
            if "/" in content_range:
                try:
                    total = int(content_range.rsplit("/", 1)[-1])
                except ValueError:
                    total = None
            return {
                "ok": True,
                "rows": rows,
                "count": len(rows),
                "total": total,
                "content_range": content_range,
                "table": path,
                "auth_mode": auth_mode,
                "filters": {k: v for k, v in params.items() if k not in {"select", "order"}},
                "secret_leak": contains_secret_like(rows),
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": exc.read().decode("utf-8", errors="replace")[:300], "rows": []}
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "rows": []}


def count_rows() -> dict[str, Any]:
    return _request(TABLE, {"select": "plan_id", "limit": "1", "offset": "0"})


def get_plan(plan_id: str) -> dict[str, Any]:
    plan_id = plan_id.strip()
    if not plan_id:
        return {"ok": False, "error": "plan_id_required", "rows": []}
    row = _request(
        TABLE,
        {
            "select": "plan_id,title,status,tier,lane,phase,workstream,priority,priority_rank,source_registry,prompt_path,updated_at,payload",
            "plan_id": f"eq.{plan_id}",
            "limit": "1",
            "offset": "0",
        },
    )
    row["plan_id"] = plan_id
    row["found"] = bool(row.get("rows"))
    return row


def query_rows(*, limit: int = 20, offset: int = 0, status: str = "", lane: str = "") -> dict[str, Any]:
    safe_limit = max(1, min(limit, 500))
    safe_offset = max(0, offset)
    params = {
        "select": PUBLIC_SELECT,
        "order": "priority_rank.asc.nullslast,plan_id.asc",
        "limit": str(safe_limit),
        "offset": str(safe_offset),
    }
    if status:
        params["status"] = f"eq.{status}"
    if lane:
        params["lane"] = f"eq.{lane}"
    return _request(TABLE, params)


def contains_secret_like(row: Any) -> bool:
    text = json.dumps(row, sort_keys=True, default=str)
    return any(pattern.search(text) for pattern in SECRET_PATTERNS)


def contract_summary() -> dict[str, Any]:
    return {
        "schema": "sourcea-plan-registry-client-contract-v1",
        "table": TABLE,
        "public_select": PUBLIC_SELECT.split(","),
        "detail_select": DETAIL_SELECT.split(","),
        "filters": ["plan_id", "status", "lane", "limit", "offset"],
        "default_auth_mode": "anon",
        "service_auth": "server-only explicit opt-in",
    }


def handle_query(params: dict[str, list[str]]) -> dict[str, Any]:
    plan_id = (params.get("plan_id") or [""])[0].strip()
    if plan_id:
        return get_plan(plan_id)
    try:
        limit = int((params.get("limit") or ["20"])[0])
    except ValueError:
        limit = 20
    try:
        offset = int((params.get("offset") or ["0"])[0])
    except ValueError:
        offset = 0
    return query_rows(
        limit=limit,
        offset=offset,
        status=(params.get("status") or [""])[0].strip(),
        lane=(params.get("lane") or [""])[0].strip(),
    )


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--count", action="store_true")
    ap.add_argument("--plan-id", default="")
    ap.add_argument("--status", default="")
    ap.add_argument("--lane", default="")
    ap.add_argument("--limit", type=int, default=20)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--contract", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.contract:
        row = contract_summary()
    elif args.count:
        row = count_rows()
    elif args.plan_id:
        row = get_plan(args.plan_id)
    else:
        row = query_rows(limit=args.limit, offset=args.offset, status=args.status, lane=args.lane)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(("OK" if row.get("ok", True) else "BLOCK") + f" table={row.get('table', TABLE)} count={row.get('count', '-')}")
    return 0 if row.get("ok", True) and not row.get("secret_leak") else 1


if __name__ == "__main__":
    raise SystemExit(main())

