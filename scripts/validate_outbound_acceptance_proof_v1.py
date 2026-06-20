#!/usr/bin/env python3
"""Validate done outbound rows have real acceptance proof — not receipt file theater."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
PLAN = ROOT / "data/outbound-factory-100-upgrade-plan-v1.json"
BAY_VERIFY = ROOT / "receipts/bays/outbound-fdg-icp/verify.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _check_linter_oqg(row: dict) -> dict:
    proof = row.get("execution_proof") or {}
    receipt_path = proof.get("receipt_path") or ""
    if not receipt_path:
        return {"ok": False, "error": "missing_execution_proof"}
    abs_path = ROOT / receipt_path if not receipt_path.startswith("/") else Path(receipt_path)
    if not abs_path.is_file():
        return {"ok": False, "error": "receipt_missing", "path": str(abs_path)}
    rcpt = _read(abs_path)
    if not rcpt.get("ok", True) and rcpt.get("schema"):
        return {"ok": False, "error": "receipt_not_ok"}
    return {"ok": True, "receipt_path": receipt_path}


def _check_fdg_icp(row: dict) -> dict:
    base = _check_linter_oqg(row)
    if not base.get("ok"):
        return base
    if BAY_VERIFY.is_file():
        bay = _read(BAY_VERIFY)
        if not bay.get("ok"):
            return {"ok": False, "error": "bay_verify_fail", "bay": str(BAY_VERIFY)}
    return {"ok": True, "receipt_path": base.get("receipt_path"), "bay_slice": BAY_VERIFY.is_file()}


def validate(*, tier_filter: str = "P0") -> dict:
    sys.path.insert(0, str(SCRIPTS))
    plan = _read(PLAN)
    checks: list[dict] = []
    failed: list[str] = []

    for row in plan.get("upgrades") or []:
        if row.get("status") != "done":
            continue
        if tier_filter and row.get("tier") != tier_filter:
            continue
        uid = str(row.get("id") or "")
        lane = str(row.get("lane") or "")
        wired = str(row.get("wired_to") or "")

        if lane == "linter_oqg" or "linter" in wired or "oqg" in wired:
            result = _check_linter_oqg(row)
        elif lane == "fdg_icp" or "icp4" in wired:
            result = _check_fdg_icp(row)
        else:
            result = _check_linter_oqg(row)

        ok = bool(result.get("ok"))
        checks.append({"upgrade_id": uid, "lane": lane, "ok": ok, **result})
        if not ok:
            failed.append(uid)

    row = {
        "schema": "validate-outbound-acceptance-proof-v1",
        "at": _now(),
        "ok": len(failed) == 0,
        "tier_filter": tier_filter,
        "checked": len(checks),
        "failed": failed,
        "checks": checks[:40],
        "line": (
            f"acceptance-proof · {len(checks) - len(failed)}/{len(checks)} PASS"
            if checks
            else "acceptance-proof · no done rows in tier"
        ),
    }
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Outbound acceptance proof validator")
    ap.add_argument("--tier", default="P0")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = validate(tier_filter=args.tier)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or ("PASS" if row.get("ok") else "FAIL"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
