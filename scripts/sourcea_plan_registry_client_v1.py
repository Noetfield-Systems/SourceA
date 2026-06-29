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
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SECRETS = Path.home() / ".sourcea-secrets/portfolio-spine.env"
TABLE = "sourcea_plan_registry"
STATUS_RECEIPT = Path.home() / ".sina/sourcea-plan-registry-status-v1.json"
PUBLIC_SELECT = "plan_id,title,status,tier,lane,phase,workstream,priority,priority_rank,source_registry,prompt_path,updated_at"
DETAIL_SELECT = f"{PUBLIC_SELECT},payload"
DEFAULT_FBE_URL = "https://sourcea-fbe-runner-production.up.railway.app"
DEFAULT_CF_URL = "https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev"
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


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _request(
    path: str,
    params: dict[str, str],
    *,
    service: bool = False,
    method: str = "GET",
    body: Any | None = None,
) -> dict[str, Any]:
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
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "Prefer": "count=exact,return=representation",
    }
    if body is not None:
        headers["Content-Type"] = "application/json"
    if method == "GET":
        headers["Range"] = (
            f"{params.get('offset', '0')}-{int(params.get('offset', '0')) + int(params.get('limit', '1')) - 1}"
            if params.get("limit")
            else "0-0"
        )
    req = urllib.request.Request(
        url,
        data=None if body is None else json.dumps(body).encode("utf-8"),
        headers=headers,
        method=method,
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
            if isinstance(rows, dict):
                rows = [rows]
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


def _probe_url(url: str, *, timeout: int = 8) -> dict[str, Any]:
    try:
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/json", "User-Agent": "Mozilla/5.0 SourceA-PlanRegistry-Probe/1.0"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            row = json.loads(raw) if raw.strip().startswith(("{", "[")) else {"raw": raw[:120]}
            return {
                "ok": bool(row.get("ok", 200 <= resp.status < 300)),
                "status": resp.status,
                "count": row.get("count"),
                "total": row.get("total"),
                "found": row.get("found"),
                "secret_leak": contains_secret_like(row),
            }
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code, "error": exc.read().decode("utf-8", errors="replace")[:160]}
    except Exception as exc:
        return {"ok": False, "status": 0, "error": str(exc)[:160]}


def operational_status(*, fbe_url: str = "", cf_url: str = "", sample_plan_id: str = "cu-score-0001") -> dict[str, Any]:
    count = count_rows()
    detail = get_plan(sample_plan_id) if sample_plan_id else {"ok": False, "skipped": True}
    fbe_base = (fbe_url or os.environ.get("FBE_CLOUD_WORKER_URL") or DEFAULT_FBE_URL).rstrip("/")
    cf_base = (cf_url or os.environ.get("SOURCEA_PLAN_REGISTRY_CF_URL") or DEFAULT_CF_URL).rstrip("/")
    fbe_probe = _probe_url(f"{fbe_base}/api/sourcea/plan-registry/v1?limit=1") if fbe_base else {"ok": False, "skipped": True}
    cf_probe = _probe_url(f"{cf_base}/plan-registry?limit=1") if cf_base else {"ok": False, "skipped": True}
    row = {
        "schema": "sourcea-plan-registry-operational-status-v1",
        "ok": bool(count.get("ok")) and bool(detail.get("ok")) and bool(fbe_probe.get("ok")) and bool(cf_probe.get("ok")),
        "at": _now(),
        "count": count,
        "sample_plan": {"plan_id": sample_plan_id, "ok": bool(detail.get("ok")), "found": bool(detail.get("found"))},
        "routes": {
            "railway_fbe": {"url": fbe_base, **fbe_probe},
            "cloudflare_proxy": {"url": cf_base, **cf_probe},
        },
    }
    row["last_error"] = next(
        (
            item.get("error")
            for item in [count, detail, fbe_probe, cf_probe]
            if isinstance(item, dict) and not item.get("ok") and item.get("error")
        ),
        "",
    )
    row["secret_leak"] = contains_secret_like(row)
    STATUS_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    STATUS_RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    row["receipt"] = str(STATUS_RECEIPT)
    return row


def attach_execution_receipt(
    *,
    plan_id: str,
    run_id: str = "",
    receipt_path: str = "",
    status: str = "attached",
    completed_at: str = "",
    metadata: dict[str, Any] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    plan_id = plan_id.strip()
    if not plan_id:
        return {"ok": False, "error": "plan_id_required"}
    current = get_plan(plan_id)
    if not current.get("ok") or not current.get("found") or not current.get("rows"):
        return {"ok": False, "error": "plan_not_found", "plan_id": plan_id}
    existing = current["rows"][0]
    payload = existing.get("payload") if isinstance(existing.get("payload"), dict) else {}
    receipts = payload.get("execution_receipts") if isinstance(payload.get("execution_receipts"), list) else []
    link = {
        "run_id": (run_id or "").strip(),
        "receipt_path": (receipt_path or "").strip(),
        "status": (status or "attached").strip(),
        "completed_at": (completed_at or _now()).strip(),
        "attached_at": _now(),
    }
    if metadata:
        link["metadata"] = metadata
    receipts = [r for r in receipts if isinstance(r, dict) and r.get("receipt_path") != link["receipt_path"]]
    receipts.append(link)
    payload = {**payload, "execution_receipts": receipts[-20:], "last_execution_receipt": link}
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "plan_id": plan_id,
            "receipt_link": link,
            "would_update": {"payload": payload, "updated_at": _now()},
            "secret_leak": contains_secret_like(payload),
        }
    row = _request(
        TABLE,
        {"plan_id": f"eq.{plan_id}", "select": DETAIL_SELECT},
        service=True,
        method="PATCH",
        body={"payload": payload, "updated_at": _now()},
    )
    row["plan_id"] = plan_id
    row["receipt_link"] = link
    row["secret_leak"] = contains_secret_like(row)
    return row


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


def handle_status(params: dict[str, list[str]]) -> dict[str, Any]:
    return operational_status(
        fbe_url=(params.get("fbe_url") or [""])[0].strip(),
        cf_url=(params.get("cf_url") or [""])[0].strip(),
        sample_plan_id=(params.get("sample_plan_id") or ["cu-score-0001"])[0].strip(),
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
    ap.add_argument("--ops-status", action="store_true")
    ap.add_argument("--attach-receipt", action="store_true")
    ap.add_argument("--run-id", default="")
    ap.add_argument("--receipt-path", default="")
    ap.add_argument("--receipt-status", default="attached")
    ap.add_argument("--live-write", action="store_true", help="Actually PATCH Supabase when attaching a receipt")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.contract:
        row = contract_summary()
    elif args.ops_status:
        row = operational_status()
    elif args.attach_receipt:
        row = attach_execution_receipt(
            plan_id=args.plan_id,
            run_id=args.run_id,
            receipt_path=args.receipt_path,
            status=args.receipt_status,
            dry_run=not args.live_write,
        )
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

