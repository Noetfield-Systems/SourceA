#!/usr/bin/env python3
"""POST external-verify receipt to Supabase truth_log (GitHub Actions only).

Law: L4 — the Action proves itself to the sink; no UI observation required.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from typing import Any


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


def post_external_verify_truth(receipt: dict[str, Any]) -> dict[str, Any]:
    autorun_ok = bool((receipt.get("autorun_verify") or {}).get("ok"))
    proof_ok = bool((receipt.get("founder_proof_15") or {}).get("ok"))
    overall_ok = bool(receipt.get("ok")) and autorun_ok and proof_ok
    event = "EXTERNAL_VERIFY_PASS" if overall_ok else "EXTERNAL_VERIFY_FAIL"

    cfg = _supabase_cfg()
    if not cfg["url"] or not cfg["key"]:
        return {"ok": False, "error": "supabase_not_configured"}

    row = {
        "source": "github_actions",
        "event": event,
        "deployment_id": str(receipt.get("github_sha") or "")[:64] or None,
        "receipt_id": f"external-verify-{receipt.get('github_run_id')}",
        "payload": receipt,
    }
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
        with urllib.request.urlopen(req, timeout=30) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            inserted: Any = json.loads(body) if body.strip() else {}
            if isinstance(inserted, list) and inserted:
                inserted = inserted[0]
            row_id = inserted.get("id") if isinstance(inserted, dict) else None
            return {
                "ok": bool(row_id),
                "truth_log_id": row_id,
                "event": event,
                "source": "github_actions",
                "at": _now(),
            }
    except urllib.error.HTTPError as exc:
        return {
            "ok": False,
            "error": exc.read().decode("utf-8", errors="replace")[:500],
            "status": exc.code,
            "event": event,
            "hint": "Apply migration 005_truth_log_external_verify_v1.sql if constraint/payload missing",
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:200], "event": event}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--receipt", required=True, help="Path to external-verify receipt JSON")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    receipt = json.loads(open(args.receipt, encoding="utf-8").read())
    row = post_external_verify_truth(receipt)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(json.dumps(row))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
