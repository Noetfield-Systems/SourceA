#!/usr/bin/env python3
"""CREED dealer audit bridge — PLATINUM lift gate for Factory 2."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from fbe_exchange_lib_v1 import append_ledger, creed_root, write_receipt  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
NODE_ID = "exchange-dealer-bridge-v1"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_dealer_bridge(*, bay_slug: str = "trustfield-bay", tenant: str = "trustfield") -> dict:
    creed = creed_root()
    audit_path = creed / ".e2e" / "factory-dealer-audit-report.json"
    dealer_ok = False
    dealer_score = ""
    verify_16 = False
    mode = "w6_dealer_stub"

    if audit_path.is_file():
        try:
            audit = json.loads(audit_path.read_text(encoding="utf-8"))
            passed = audit.get("passed") or audit.get("pass_count")
            total = audit.get("total") or audit.get("check_count") or 15
            dealer_score = f"{passed}/{total}"
            dealer_ok = str(dealer_score) == "15/15" or (passed == 15 and total == 15)
            verify_16 = audit.get("verify_16_steps_ok") is True or audit.get("verify-16-steps") == "PASS"
            mode = "w6_creed_audit"
        except (OSError, json.JSONDecodeError):
            pass

    platinum_eligible = dealer_ok and verify_16
    row = {
        "schema": "fbe-exchange-step-receipt-v1",
        "ok": True,
        "at": _now(),
        "node_id": NODE_ID,
        "bay_slug": bay_slug,
        "tenant": tenant,
        "mode": mode,
        "dealer_score": dealer_score or "unknown",
        "dealer_ok": dealer_ok,
        "verify_16_steps": verify_16,
        "platinum_eligible": platinum_eligible,
        "deliveryMode": "prove_only",
        "note": "PLATINUM only when dealer 15/15 + verify-16-steps PASS",
    }
    write_receipt(bay_slug, NODE_ID, row)
    append_ledger(bay_slug, {"at": row["at"], "node_id": NODE_ID, "ok": True, "platinum_eligible": platinum_eligible})
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="trustfield-bay")
    ap.add_argument("--tenant", default="trustfield")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_dealer_bridge(bay_slug=args.bay, tenant=args.tenant)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
