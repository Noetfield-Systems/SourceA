#!/usr/bin/env python3
"""gmail_triage_e2e — sweep row + triage verdict + Telegram (PASS definition).

PASS requires: triage processed row + telegram_notified + verdict in allowed set.
Law: data/gmail-sweep-ssot-v1.json
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
SSOT = ROOT / "data/gmail-sweep-ssot-v1.json"
RECEIPT = ROOT / "receipts" / "cloud" / "gmail-triage-e2e" / "gmail-triage-e2e-receipt-v1.json"
SINA_RECEIPT = Path.home() / ".sina/gmail-triage-e2e-receipt-v1.json"
ALLOWED_VERDICTS = frozenset({"PASS", "FAIL", "ROUTE", "MONITOR", "ARCHIVE", "DEFER"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_secrets() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import ensure_env  # noqa: WPS433

    ensure_env()


def _supabase_cfg() -> tuple[str, str]:
    _load_secrets()
    return os.environ.get("SUPABASE_URL", "").strip().rstrip("/"), os.environ.get(
        "SUPABASE_SERVICE_ROLE_KEY", ""
    ).strip()


def _latest_unprocessed() -> dict[str, Any] | None:
    url, key = _supabase_cfg()
    if not url or not key:
        return None
    q = f"{url}/rest/v1/gmail_inbox_signals?select=*&processed=eq.false&order=swept_at.desc&limit=1"
    req = urllib.request.Request(
        q,
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
    return rows[0] if isinstance(rows, list) and rows else None


def _latest_processed() -> dict[str, Any] | None:
    url, key = _supabase_cfg()
    if not url or not key:
        return None
    q = f"{url}/rest/v1/gmail_inbox_signals?select=*&processed=eq.true&order=triage_at.desc&limit=1"
    req = urllib.request.Request(
        q,
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=25) as resp:
        rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
    return rows[0] if isinstance(rows, list) and rows else None


def run_e2e(*, dry_run: bool = False, run_motors: bool = True) -> dict[str, Any]:
    sweep_row: dict[str, Any] = {"ok": True, "skipped": dry_run}
    triage_row: dict[str, Any] = {"ok": True, "skipped": dry_run}

    if run_motors and not dry_run:
        sys.path.insert(0, str(ROOT / "scripts"))
        from gmail_inbox_sweep_v1 import run_sweep  # noqa: WPS433
        from signal_factory_triage_v1 import run_triage  # noqa: WPS433

        sweep_row = run_sweep(max_per_mailbox=5)
        triage_row = run_triage(max_batch=5, notify=True)

    row = None
    if not dry_run:
        row = _latest_processed() or _latest_unprocessed()
    checks = {
        "supabase_row": bool(row) if not dry_run else True,
        "processed": bool(row and row.get("processed")) if not dry_run else True,
        "telegram_notified": bool(row and row.get("telegram_notified")) if not dry_run else True,
        "verdict_valid": bool(row and row.get("triage_verdict") in ALLOWED_VERDICTS)
        if not dry_run
        else True,
    }
    ok = all(checks.values())

    out = {
        "schema": "gmail-triage-e2e-v1",
        "ok": ok,
        "verdict": "PASS" if ok else "FAIL",
        "at": _now(),
        "dry_run": dry_run,
        "sweep": sweep_row,
        "triage": triage_row,
        "checks": checks,
        "sample_row_id": row.get("id") if isinstance(row, dict) else None,
        "pass_definition": list(checks.keys()),
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    try:
        SINA_RECEIPT.parent.mkdir(parents=True, exist_ok=True)
        SINA_RECEIPT.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true", help="Disk/structure only — no motor run")
    ap.add_argument("--no-run", action="store_true", help="Read-back only")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_e2e(dry_run=args.dry_run, run_motors=not args.no_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("verdict", "FAIL"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
