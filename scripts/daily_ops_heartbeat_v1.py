#!/usr/bin/env python3
"""07:00 UTC daily ops heartbeat — fixed format line + truth_log."""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
HB_DIR = ROOT / "receipts/cloud/ops-heartbeat"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load_secrets() -> None:
    sys.path.insert(0, str(ROOT / "scripts"))
    from cloud_forge_run_supabase_v1 import ensure_env  # noqa: WPS433

    ensure_env()


def _count_table(table: str, *, filter_q: str = "") -> int:
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        return -1
    q = f"{url}/rest/v1/{table}?select=id{filter_q}&limit=1"
    headers = {
        "apikey": key,
        "Authorization": f"Bearer {key}",
        "Accept": "application/json",
        "Prefer": "count=exact",
    }
    req = urllib.request.Request(q, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            cr = resp.headers.get("Content-Range", "")
            if "/" in cr:
                return int(cr.split("/")[-1])
    except (urllib.error.URLError, ValueError):
        pass
    return -1


def _motor_line() -> str:
    proc = subprocess.run(
        [sys.executable, str(ROOT / "scripts/autorun_pending_v1.py"), "--json"],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        row = json.loads(proc.stdout or "{}")
        return str(row.get("motor_status") or row.get("report_line") or "UNKNOWN")[:80]
    except json.JSONDecodeError:
        return "UNKNOWN"


def build_heartbeat() -> dict[str, Any]:
    _load_secrets()
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    ts = _now()
    motor = _motor_line()
    improvement_open = _count_table("improvement_queue", filter_q="&status=eq.open")
    machine_safe_open = _count_table(
        "improvement_queue", filter_q="&status=eq.open&machine_safe=eq.true"
    )
    gmail_pending = _count_table("gmail_inbox_signals", filter_q="&processed=eq.false")

    fixed_line = (
        f"SOURCEA_OPS_HEARTBEAT_v1 · {ts} · motor={motor} · "
        f"improvement_open={improvement_open} machine_safe={machine_safe_open} · "
        f"gmail_unprocessed={gmail_pending}"
    )

    doc = {
        "schema": "sourcea-ops-heartbeat-v1",
        "version": "1.0.0",
        "date": today,
        "at": ts,
        "fixed_line": fixed_line,
        "motor": motor,
        "counts": {
            "improvement_open": improvement_open,
            "machine_safe_open": machine_safe_open,
            "gmail_unprocessed": gmail_pending,
        },
    }
    return doc


def _truth_exists(receipt_id: str) -> bool:
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        return False
    q = f"{url}/rest/v1/truth_log?select=id&receipt_id=eq.{receipt_id}&limit=1"
    req = urllib.request.Request(
        q,
        headers={"apikey": key, "Authorization": f"Bearer {key}", "Accept": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            rows = json.loads(resp.read().decode("utf-8", errors="replace") or "[]")
        return bool(isinstance(rows, list) and rows)
    except (urllib.error.URLError, json.JSONDecodeError):
        return False


def post_truth(doc: dict[str, Any]) -> dict[str, Any]:
    url = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
    key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()
    if not url or not key:
        return {"ok": False, "error": "supabase_not_configured"}
    receipt_id = f"ops-heartbeat-{doc.get('date')}"
    if _truth_exists(receipt_id):
        return {"ok": True, "deduped": True, "receipt_id": receipt_id}
    row = {
        "source": "ops_heartbeat",
        "event": "OPS_HEARTBEAT",
        "receipt_id": receipt_id,
        "payload": doc,
    }
    req = urllib.request.Request(
        f"{url}/rest/v1/truth_log",
        data=json.dumps(row).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Prefer": "return=minimal",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return {"ok": 200 <= resp.status < 300}
    except urllib.error.HTTPError as exc:
        return {"ok": False, "status": exc.code}


def run_heartbeat(*, notify: bool = True) -> dict[str, Any]:
    doc = build_heartbeat()
    HB_DIR.mkdir(parents=True, exist_ok=True)
    path = HB_DIR / f"ops-heartbeat-{doc['date']}-07z-v1.json"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    truth = post_truth(doc)
    telegram = {"ok": False, "skipped": True}
    if notify:
        sys.path.insert(0, str(ROOT / "scripts"))
        from telegram_alert_v1 import send_telegram_alert  # noqa: WPS433

        telegram = send_telegram_alert(f"<code>{doc['fixed_line']}</code>")
    return {
        "ok": True,
        "at": doc["at"],
        "fixed_line": doc["fixed_line"],
        "path": str(path.relative_to(ROOT)),
        "truth_log": truth,
        "telegram": telegram,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-telegram", action="store_true")
    args = ap.parse_args()
    row = run_heartbeat(notify=not args.no_telegram)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("fixed_line", ""))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
