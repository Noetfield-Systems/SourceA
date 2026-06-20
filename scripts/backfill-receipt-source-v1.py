#!/usr/bin/env python3
"""Backfill missing receipt.source on legacy honest receipts — hygiene only."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECEIPTS = ROOT / "receipts"

sys.path.insert(0, str(ROOT / "scripts"))
from worker_receipt_v1 import ALLOWED_RECEIPT_SOURCES  # noqa: E402

HONEST = frozenset({"DONE", "PASS", "VERIFIED", "CHECK_PASSED"})


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def infer_source(rec: dict) -> str | None:
    existing = str(rec.get("source") or "").strip()
    if existing in ALLOWED_RECEIPT_SOURCES:
        return None
    agent = str(rec.get("agent") or "").strip().lower()
    if agent == "api":
        return "api"
    if agent in ("maintainer_executor", "maintainer"):
        return "maintainer_executor"
    if str(rec.get("source") or "") == "restore-broker-proven-v1":
        return "restore-broker-proven-v1"
    if "restore-broker-proven" in str(rec.get("evidence") or ""):
        return "restore-broker-proven-v1"
    if str(rec.get("engine") or "") == "WORKER" and rec.get("schema") == "sourcea-sa-receipt-v1":
        return "goal1_lane_broker"
    # Legacy worker closeout shape (role/commands_run/summary)
    if rec.get("role") or rec.get("commands_run") or rec.get("validators_run"):
        return "worker_inbox"
    return "worker_inbox"


def backfill(*, dry_run: bool = False) -> dict:
    fixed: list[str] = []
    skipped: list[str] = []
    for p in sorted(RECEIPTS.glob("sa-*-receipt.json")):
        try:
            rec = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        st = str(rec.get("status") or "").upper()
        if st not in HONEST and st != "BLOCKED":
            continue
        src = infer_source(rec)
        if not src:
            skipped.append(p.stem.replace("-receipt", ""))
            continue
        if not dry_run:
            rec["source"] = src
            if not rec.get("schema"):
                rec["schema"] = "sourcea-sa-receipt-v1"
            if not rec.get("at") and rec.get("done_at"):
                rec["at"] = rec["done_at"]
            if not rec.get("at") and rec.get("timestamp"):
                rec["at"] = rec["timestamp"]
            p.write_text(json.dumps(rec, indent=2) + "\n", encoding="utf-8")
        fixed.append(p.stem.replace("-receipt", ""))
    return {
        "ok": True,
        "dry_run": dry_run,
        "fixed": fixed,
        "fixed_count": len(fixed),
        "skipped_has_source": len(skipped),
        "at": _now(),
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out = backfill(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"backfill-receipt-source: fixed={out['fixed_count']} dry_run={args.dry_run}")
        for sa in out["fixed"]:
            print(f"  {sa}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
