#!/usr/bin/env python3
"""Ops motors status — one JSON summary from disk receipts + Supabase."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_secrets() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import ensure_env  # noqa: WPS433

    ensure_env()


def _read_json(path: Path) -> dict[str, Any]:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _latest_mtime(glob: str) -> str | None:
    files = sorted(ROOT.glob(glob), key=lambda p: p.stat().st_mtime if p.is_file() else 0)
    if not files:
        return None
    return datetime.fromtimestamp(files[-1].stat().st_mtime, tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _supabase_latest(table: str, *, order_col: str = "created_at") -> str | None:
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        return None
    q = f"{url}/rest/v1/{table}?select={order_col}&order={order_col}.desc&limit=1"
    req = urllib.request.Request(
        q,
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
        if isinstance(rows, list) and rows:
            return str(rows[0].get(order_col) or "")
    except Exception:
        pass
    return None


def status_row() -> dict[str, Any]:
    _load_secrets()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    hb_file = ROOT / "receipts/cloud/ops-heartbeat" / f"ops-heartbeat-{today}-07z-v1.json"
    hb = _read_json(hb_file)
    return {
        "schema": "ops-motors-status-v1",
        "at": _now(),
        "gmail_sweep": {
            "last_receipt_disk": _latest_mtime("receipts/gha/gmail-sweep-findings-v1.json"),
            "last_signal_swept": _supabase_latest("gmail_inbox_signals", order_col="swept_at"),
        },
        "signal_triage": {
            "last_receipt_disk": _latest_mtime("receipts/signal-factory/triage/*.json"),
            "last_triage": _supabase_latest("gmail_inbox_signals", order_col="triage_at"),
        },
        "kaizen_nightly": {
            "last_receipt_disk": _latest_mtime("receipts/cloud/kaizen/nightly/kaizen-nightly-*-v1.json"),
        },
        "ops_heartbeat": {
            "last_fixed_line": hb.get("fixed_line"),
            "last_at": hb.get("at"),
            "path": str(hb_file.relative_to(ROOT)) if hb_file.is_file() else None,
        },
        "ok": True,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = status_row()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("ops_heartbeat", {}).get("last_fixed_line") or json.dumps(row))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
