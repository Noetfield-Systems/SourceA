#!/usr/bin/env python3
"""Open SourceA autorun 24h DECLARED→VERIFIED window from HEAD SHA."""
from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WINDOW_DIR = ROOT / "receipts" / "cloud" / "autorun-verified-window"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _head_sha() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=str(ROOT), text=True).strip()


def write_window(*, hours: float = 24.0, sha: str = "") -> dict:
    head = sha or _head_sha()
    started = datetime.now(timezone.utc)
    closes = started + timedelta(hours=hours)
    doc = {
        "schema": "autorun-declared-window-v1",
        "version": "1.0.0",
        "status": "DECLARED",
        "started_at": started.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "closes_at": closes.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "window_hours": hours,
        "head_sha": head,
        "law": "governed-autorun — DECLARED until 24h green on external receipts",
        "criteria": {
            "zero_manual": "no manual trigger_source in cycle receipts",
            "cycle_receipt_v2": "every cycle autonomous-forge-run-cycle-receipt-v2",
            "sink_invariant": "sink_invariant on every cycle receipt",
            "daily_heartbeat": "heartbeat receipt each UTC day",
            "external_verify_pass": "≥1 truth_log EXTERNAL_VERIFY_PASS per UTC day",
        },
        "verify_command": "python3 scripts/verify_autorun_zero_manual_v1.py --hours 24 --json",
        "ok": True,
        "report_line": f"autorun window DECLARED · sha {head[:8]} · closes {closes.strftime('%Y-%m-%dT%H:%M:%SZ')}",
    }
    WINDOW_DIR.mkdir(parents=True, exist_ok=True)
    path = WINDOW_DIR / f"declared-window-{head[:8]}-v1.json"
    path.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    doc["receipt_path"] = str(path)
    return doc


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--hours", type=float, default=24.0)
    ap.add_argument("--sha", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = write_window(hours=args.hours, sha=args.sha)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["report_line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
