#!/usr/bin/env python3
"""FBE first-bay pulse — MARKET_READY receipt bridge for E12/E09 commerce score."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
PULSE = SINA / "fbe-first-bay-pulse-v1.json"
RECEIPT = SINA / "fbe-run-job-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def run_pulse(*, write: bool = True) -> dict:
    market: dict = {}
    try:
        proc = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "fbe_verify_market_ready_v1.py"), "--json"],
            capture_output=True,
            text=True,
            timeout=60,
            cwd=str(ROOT),
        )
        if proc.returncode == 0 and proc.stdout.strip():
            market = json.loads(proc.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        pass

    job = _read_json(RECEIPT)
    bundle = _read_json(ROOT / "data" / "fbe_factory_builder_bundle_v1.json")
    tier = market.get("tier_achieved") or market.get("tier_target")
    ok = bool(market.get("ok"))
    commerce_score = 55 if ok and tier else 35

    row = {
        "schema": "fbe-first-bay-pulse-v1",
        "at": _now(),
        "epic": "E12",
        "commerce_epic": "E09",
        "market_ready_ok": ok,
        "tier_achieved": tier,
        "run_job_receipt": str(RECEIPT) if RECEIPT.is_file() else None,
        "catalog_hero": "exchange-factory-v1",
        "commerce_score_estimate": commerce_score,
        "fbe_cloud_worker_url": bundle.get("live_snapshot", {}).get("cloud_worker_url") or "",
        "pulse_line": f"fbe-bay · tier={tier or 'pending'} · commerce≈{commerce_score}/100 · MARKET_READY={'OK' if ok else 'RED'}",
        "commands": {
            "run_job": "python3 scripts/fbe_run_job_v1.py --template exchange-factory-v1 --json",
            "verify": "python3 scripts/fbe_verify_market_ready_v1.py --json",
            "catalog": "bash scripts/validate-fbe-catalog-spec-v1.sh",
        },
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        PULSE.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="FBE first-bay pulse")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_pulse(write=True)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("pulse_line"))
    return 0 if row.get("market_ready_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
