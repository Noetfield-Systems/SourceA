#!/usr/bin/env python3
"""FBE assembly verify — W3 headless proof."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
VERIFY_PATH = SINA / "fbe-assembly-verify-receipt-v1.json"


def _now() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def verify(*, bay_slug: str = "sample-bay") -> dict:
    checks: list[dict] = []
    ok = True

    run_r = {}
    run_path = SINA / "fbe-assembly-run-receipt-v1.json"
    if run_path.is_file():
        run_r = json.loads(run_path.read_text(encoding="utf-8"))
    checks.append({
        "id": "assembly_runner",
        "ok": bool(run_r.get("ok")),
        "steps_executed": run_r.get("steps_executed"),
        "steps_total": run_r.get("steps_total"),
    })
    if not run_r.get("ok"):
        ok = False

    ledger = ROOT / "receipts" / "bays" / bay_slug / "assembly" / "ledger.jsonl"
    ledger_lines = []
    if ledger.is_file():
        ledger_lines = [ln for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    expected = 12
    ledger_ok = len(ledger_lines) >= expected
    checks.append({"id": "assembly_ledger", "ok": ledger_ok, "lines": len(ledger_lines), "expected": expected})
    if not ledger_ok:
        ok = False

    verify_receipt = ROOT / "receipts" / "bays" / bay_slug / "assembly" / "church-verify-v1-v1.json"
    verify_data = {}
    if verify_receipt.is_file():
        verify_data = json.loads(verify_receipt.read_text(encoding="utf-8"))
    verify_ran = verify_receipt.is_file()
    church_verify_ok = bool(verify_data.get("ok"))
    checks.append({
        "id": "church_verify",
        "ok": verify_ran and church_verify_ok,
        "path": str(verify_receipt),
        "church_ok": church_verify_ok,
    })
    if not verify_ran:
        ok = False

    prove_only = run_r.get("deliveryMode") == "prove_only"
    checks.append({"id": "prove_only", "ok": prove_only})

    row = {
        "schema": "fbe-assembly-verify-v1",
        "ok": ok,
        "at": _now(),
        "wave": "W3",
        "bay_slug": bay_slug,
        "mode": "headless",
        "deliveryMode": "prove_only",
        "checks": checks,
        "proof": "assembly_verify PASS" if ok else "assembly_verify FAIL",
        "execution_plane": "headless_w3",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    VERIFY_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    (ROOT / "receipts" / "assembly-verify-v1.json").write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
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
