#!/usr/bin/env python3
"""nf_intake_e2e — Telegram+DB PASS definition for Noetfield intelligence intake.

PASS requires ALL:
  1. POST /api/noetfield/intake/v1 returns ok:true with intake_id
  2. Supabase nf_intake_submissions read-back matches intake_id (probe=true)
  3. telegram_notified=true on the read-back row

Law: data/noetfield-nerve-probe-ssot-v1.json · data/nerve-probe-cloud-cron-v1.json
Worker: cloud/workers/loop-specialist-tick-v1 (SourceA piggyback cron)
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SSOT = ROOT / "data" / "noetfield-nerve-probe-ssot-v1.json"
DEFAULT_WORKER = "https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _http_json(url: str, *, method: str = "GET", body: dict | None = None, timeout: float = 30.0) -> dict[str, Any]:
    data = None
    headers = {"User-Agent": "nf-intake-e2e/1.0", "Accept": "application/json"}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(url, data=data, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
            status = int(getattr(resp, "status", 200) or 200)
            row = json.loads(raw) if raw.strip() else {}
            row["_http_status"] = status
            return row
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            row = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            row = {"error": raw[:200]}
        row["_http_status"] = exc.code
        row["ok"] = False
        return row
    except (urllib.error.URLError, OSError, TimeoutError) as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _supabase_read(env: dict[str, str], intake_id: str) -> dict[str, Any]:
    base = (env.get("SUPABASE_URL") or "").rstrip("/")
    key = env.get("SUPABASE_SERVICE_ROLE_KEY") or env.get("SUPABASE_ANON_KEY") or ""
    if not base or not key:
        return {"ok": False, "skipped": True, "reason": "supabase_env_missing"}
    url = f"{base}/rest/v1/nf_intake_submissions?intake_id=eq.{intake_id}&limit=1"
    req = urllib.request.Request(
        url,
        headers={
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Accept": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
        row = rows[0] if isinstance(rows, list) and rows else None
        return {"ok": bool(row), "row": row}
    except (urllib.error.URLError, OSError, json.JSONDecodeError) as exc:
        return {"ok": False, "error": str(exc)[:200]}


def _load_supabase_env() -> dict[str, str]:
    out: dict[str, str] = {}
    for key in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_ANON_KEY"):
        if os.environ.get(key):
            out[key] = os.environ[key]
    secrets = Path.home() / ".sourcea-secrets" / "portfolio-spine.env"
    if secrets.is_file():
        for line in secrets.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            k = k.strip()
            if k in ("SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_ANON_KEY") and k not in out:
                out[k] = v.strip().strip('"').strip("'")
    return out


def evaluate_pass(*, post: dict[str, Any], read_back: dict[str, Any]) -> dict[str, Any]:
    row = read_back.get("row") if isinstance(read_back.get("row"), dict) else {}
    checks = {
        "post_ok": bool(post.get("ok")),
        "supabase_read_back": bool(read_back.get("ok") and row.get("intake_id") == post.get("intake_id")),
        "telegram_notified": bool(row.get("telegram_notified")),
    }
    ok = all(checks.values())
    return {
        "ok": ok,
        "verdict": "PASS" if ok else "FAIL",
        "checks": checks,
        "pass_definition": ["post_ok", "supabase_read_back", "telegram_notified"],
        "intake_id": post.get("intake_id"),
        "read_back": row,
    }


def run_probe(*, worker_url: str, dry_run: bool = False) -> dict[str, Any]:
    ssot = _read_json(SSOT)
    cfg = ssot.get("nf_intake_e2e") or {}
    payload = dict(cfg.get("probe_payload") or {})
    payload["probe"] = True
    base = worker_url.rstrip("/")
    if dry_run:
        return {
            "ok": True,
            "dry_run": True,
            "schema": "nf-intake-e2e-v1",
            "at": _now(),
            "worker_url": base,
            "payload": payload,
            "pass_definition": cfg.get("pass_requires") or ["post_ok", "supabase_read_back", "telegram_notified"],
        }
    post = _http_json(f"{base}/api/noetfield/intake/v1", method="POST", body=payload)
    intake_id = str(post.get("intake_id") or "")
    read_back = _supabase_read(_load_supabase_env(), intake_id) if intake_id else {"ok": False}
    verdict = evaluate_pass(post=post, read_back=read_back)
    return {
        "schema": "nf-intake-e2e-v1",
        "at": _now(),
        "worker_url": base,
        "post": post,
        **verdict,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description="nf_intake_e2e — Telegram+DB PASS probe")
    ap.add_argument("--worker-url", default=os.environ.get("NERVE_PROBE_URL", DEFAULT_WORKER))
    ap.add_argument("--dry-run", action="store_true", help="Print PASS definition + payload only")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_probe(worker_url=args.worker_url, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"nf_intake_e2e: {row.get('verdict', 'FAIL')} · intake={row.get('intake_id')}")
        for k, v in (row.get("checks") or {}).items():
            print(f"  {k}: {'OK' if v else 'FAIL'}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    sys.exit(main())
