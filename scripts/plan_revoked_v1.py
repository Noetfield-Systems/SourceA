#!/usr/bin/env python3
"""PLAN_REVOKED receipt — INCIDENT-016 ghost plan suppression."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

RECEIPT = Path.home() / ".sina/plan-revoked-receipt-v1.json"


def write_revoked(plan_name: str, reason: str = "founder_stop_or_cancel") -> dict:
    row = {
        "schema": "plan-revoked-receipt-v1",
        "revoked_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "plan_name": plan_name,
        "reason": reason,
        "law": "INCIDENT-016 — cancel ALL todos; do not resume ghost plan",
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--plan", default="session_plan")
    ap.add_argument("--reason", default="founder_stop_or_cancel")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not args.write:
        if RECEIPT.is_file():
            print(RECEIPT.read_text(encoding="utf-8"))
        else:
            print("{}")
        return 0
    row = write_revoked(args.plan, args.reason)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"PLAN_REVOKED {args.plan} -> {RECEIPT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
