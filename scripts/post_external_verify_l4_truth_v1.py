#!/usr/bin/env python3
"""POST minimal L4 receipt to Supabase truth_log via REST (no psql)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def post_truth(receipt_path: str) -> dict:
    url = os.environ.get("SUPABASE_URL", "").strip()
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        return {"ok": False, "error": "supabase_not_configured"}
    receipt = json.loads(open(receipt_path, encoding="utf-8").read())
    event = "EXTERNAL_VERIFY_PASS" if receipt.get("ok") else "EXTERNAL_VERIFY_FAIL"
    row = {
        "source": "github_actions",
        "event": event,
        "receipt_id": f"external-verify-{receipt.get('github_run_id', '')}",
        "deployment_id": (receipt.get("github_sha") or "")[:64] or None,
        "payload": receipt,
    }
    req = urllib.request.Request(
        f"{url.rstrip('/')}/rest/v1/truth_log",
        data=json.dumps(row).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "return=representation",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
            inserted = body[0] if isinstance(body, list) and body else body
            return {
                "ok": True,
                "truth_log_id": inserted.get("id") if isinstance(inserted, dict) else None,
                "event": event,
                "at": _now(),
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "status": exc.code,
            "error": exc.read().decode("utf-8", errors="replace")[:400],
            "event": event,
        }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--receipt", required=True)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = post_truth(args.receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
