#!/usr/bin/env python3
"""Insert Kaizen rows into Supabase improvement_queue via REST (no reports)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _supabase_configured() -> tuple[str, str] | tuple[None, None]:
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        return None, None
    return url, key


def normalize_finding(row: dict[str, Any]) -> dict[str, Any] | None:
    finding = str(row.get("finding") or "").strip()
    source = str(row.get("source") or "").strip()
    if not finding or not source:
        return None
    machine_safe = bool(row.get("machine_safe", False))
    out: dict[str, Any] = {
        "finding": finding[:4000],
        "source": source[:256],
        "machine_safe": machine_safe,
        "status": "open" if machine_safe else "founder_gated",
    }
    roi = row.get("expected_roi")
    if roi is not None:
        try:
            out["expected_roi"] = float(roi)
        except (TypeError, ValueError):
            pass
    return out


def insert_findings(findings: list[dict[str, Any]]) -> dict[str, Any]:
    url, key = _supabase_configured()
    if not url or not key:
        return {
            "ok": False,
            "error": "supabase_not_configured",
            "inserted": 0,
            "skipped": len(findings),
            "at": _now(),
        }

    rows = [r for r in (normalize_finding(f) for f in findings) if r]
    if not rows:
        return {"ok": True, "inserted": 0, "skipped": len(findings), "at": _now()}

    req = urllib.request.Request(
        f"{url}/rest/v1/improvement_queue",
        data=json.dumps(rows).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "return=representation",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=45) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
            inserted = body if isinstance(body, list) else [body]
            ids = [r.get("id") for r in inserted if isinstance(r, dict)]
            return {
                "ok": True,
                "inserted": len(ids),
                "ids": ids[:20],
                "at": _now(),
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "error": exc.read().decode("utf-8", errors="replace")[:500],
            "inserted": 0,
            "at": _now(),
        }


def probe_table() -> dict[str, Any]:
    url, key = _supabase_configured()
    if not url or not key:
        return {"ok": False, "error": "supabase_not_configured"}
    req = urllib.request.Request(
        f"{url}/rest/v1/improvement_queue?select=id&limit=1",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
        method="GET",
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            return {"ok": True, "status": resp.status}
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "error": exc.read().decode("utf-8", errors="replace")[:300],
        }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--findings", help="JSON file with {findings: [...]}")
    ap.add_argument("--probe", action="store_true", help="Probe improvement_queue table")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.probe:
        row = probe_table()
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            print(json.dumps(row))
        return 0 if row.get("ok") else 1

    if not args.findings:
        ap.error("--findings required unless --probe")

    payload = json.loads(open(args.findings, encoding="utf-8").read())
    findings = payload.get("findings") if isinstance(payload, dict) else payload
    if not isinstance(findings, list):
        print("FAIL: findings must be a list", file=sys.stderr)
        return 1

    row = insert_findings(findings)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
