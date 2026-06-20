#!/usr/bin/env python3
"""Migrate legacy sa-only receipts to canonical upgrade-sa receipts + fix plan paths."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"
RECEIPTS = ROOT / "receipts"
SINA = Path.home() / ".sina"

sys.path.insert(0, str(ROOT / "scripts"))
from outbound_receipt_path_v1 import (  # noqa: E402
    LAW,
    canonical_receipt_path,
    canonical_receipt_rel,
)


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def migrate(*, write: bool = True) -> dict:
    plan = _read_json(PLAN)
    migrated: list[str] = []
    plan_fixed: list[str] = []
    skipped: list[str] = []

    for p in sorted(RECEIPTS.glob("sa-*-receipt.json")):
        row = _read_json(p)
        uid = str(row.get("upgrade_id") or "")
        sa_id = str(row.get("sa_id") or p.stem.replace("-receipt", ""))
        if not uid:
            skipped.append(p.name)
            continue
        canon = canonical_receipt_path(upgrade_id=uid, sa_id=sa_id)
        if canon.is_file():
            skipped.append(f"{p.name}->exists")
            continue
        if write:
            row["receipt_law"] = LAW
            row["migrated_from"] = str(p.relative_to(ROOT))
            row["migrated_at"] = _now()
            canon.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
        migrated.append(f"{uid}:{sa_id}")

    for u in plan.get("upgrades") or []:
        if u.get("status") != "done":
            continue
        uid = str(u.get("id") or "")
        proof = u.get("execution_proof") or {}
        sa_id = str(proof.get("sa_id") or u.get("worker_sa_id") or "")
        if not uid or not sa_id:
            continue
        rel = canonical_receipt_rel(upgrade_id=uid, sa_id=sa_id)
        canon = ROOT / rel
        if canon.is_file() and proof.get("receipt_path") != rel:
            if write:
                proof["receipt_path"] = rel
                proof["receipt_law"] = LAW
                proof["migrated_at"] = _now()
                u["execution_proof"] = proof
            plan_fixed.append(uid)

    if write:
        plan["execution_proof_law"] = LAW
        plan["saved_at"] = _now()
        PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
        receipt = {
            "schema": "outbound-receipt-migrate-receipt-v1",
            "at": _now(),
            "law": LAW,
            "migrated": migrated,
            "plan_fixed": plan_fixed,
            "skipped": skipped,
        }
        SINA.mkdir(parents=True, exist_ok=True)
        (SINA / "outbound-receipt-migrate-receipt-v1.json").write_text(
            json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
        )

    return {
        "ok": True,
        "law": LAW,
        "migrated_count": len(migrated),
        "plan_fixed_count": len(plan_fixed),
        "migrated": migrated,
        "plan_fixed": plan_fixed,
        "line": f"receipt-migrate · canon={len(migrated)} · plan_fixed={len(plan_fixed)}",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    row = migrate(write=not args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
