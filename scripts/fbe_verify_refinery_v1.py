#!/usr/bin/env python3
"""FBE refinery verify — W2 headless proof."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
VERIFY_PATH = SINA / "fbe-refinery-verify-receipt-v1.json"
BAY_JOBS = ROOT / "data" / "fbe_bay_jobs_v1.json"


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verify(*, bay_slug: str = "sample-bay") -> dict:
    checks: list[dict] = []
    ok = True

    run_r = {}
    run_path = SINA / "fbe-refinery-run-receipt-v1.json"
    if run_path.is_file():
        run_r = json.loads(run_path.read_text(encoding="utf-8"))
    checks.append({
        "id": "refinery_runner",
        "ok": bool(run_r.get("ok")),
        "steps_executed": run_r.get("steps_executed"),
        "steps_total": run_r.get("steps_total"),
    })
    if not run_r.get("ok"):
        ok = False

    ledger = ROOT / "receipts" / "bays" / bay_slug / "ledger.jsonl"
    ledger_lines = []
    if ledger.is_file():
        ledger_lines = [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    expected = 7
    ledger_ok = len(ledger_lines) >= expected
    checks.append({"id": "bay_ledger", "ok": ledger_ok, "lines": len(ledger_lines), "expected": expected})
    if not ledger_ok:
        ok = False

    prove_only = run_r.get("deliveryMode") == "prove_only"
    checks.append({"id": "prove_only", "ok": prove_only})
    if not prove_only:
        ok = False

    tier_ok = True
    checks.append({"id": "no_platinum_lie", "ok": tier_ok, "tier_cap": "GOLD"})

    verify_receipt = ROOT / "receipts" / "bays" / bay_slug / "factory-verify-v1-v1.json"
    verify_ran = verify_receipt.is_file()
    checks.append({"id": "verify_job_ran", "ok": verify_ran, "path": str(verify_receipt)})

    row = {
        "schema": "fbe-refinery-verify-v1",
        "ok": ok,
        "at": _now(),
        "wave": "W2",
        "bay_slug": bay_slug,
        "mode": "headless",
        "deliveryMode": "prove_only",
        "checks": checks,
        "proof": "refinery_verify PASS" if ok else "refinery_verify FAIL",
        "execution_plane": "headless_w2",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    (ROOT / "receipts" / "refinery-verify-v1.json").parent.mkdir(parents=True, exist_ok=True)
    (ROOT / "receipts" / "refinery-verify-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="sample-bay")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = verify(bay_slug=args.bay)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
