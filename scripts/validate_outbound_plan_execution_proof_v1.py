#!/usr/bin/env python3
"""Validate outbound plan v3 — done rows require canonical execution_proof receipt on disk."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"

sys.path.insert(0, str(ROOT / "scripts"))
from outbound_receipt_path_v1 import LAW, receipt_exists, resolve_receipt_file  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _receipt_exists(u: dict) -> tuple[bool, str]:
    uid = str(u.get("id") or "")
    proof = u.get("execution_proof") or {}
    sa_id = str(proof.get("sa_id") or u.get("worker_sa_id") or "")
    if uid and sa_id and receipt_exists(upgrade_id=uid, sa_id=sa_id):
        _, rel = resolve_receipt_file(upgrade_id=uid, sa_id=sa_id)
        return True, rel
    return False, ""


def validate(*, fix_schema: bool = False) -> dict:
    plan = _read_json(PLAN)
    upgrades = plan.get("upgrades") or []
    violations: list[dict] = []
    verified = 0
    done_total = 0

    for u in upgrades:
        if u.get("status") != "done":
            continue
        done_total += 1
        ok, path = _receipt_exists(u)
        if ok:
            verified += 1
            if fix_schema and not u.get("execution_proof"):
                u["execution_proof"] = {
                    "sa_id": u.get("worker_sa_id"),
                    "receipt_path": path,
                    "receipt_law": LAW,
                    "pulse_verified": True,
                }
        else:
            violations.append(
                {
                    "id": u.get("id"),
                    "worker_sa_id": u.get("worker_sa_id"),
                    "issue": "done_without_receipt",
                }
            )

    ok = len(violations) == 0
    row = {
        "schema": "outbound-plan-execution-proof-validation-v1",
        "at": _now(),
        "ok": ok,
        "plan_schema": plan.get("schema"),
        "receipt_law": LAW,
        "done_total": done_total,
        "verified_done": verified,
        "violations": violations,
        "violation_count": len(violations),
        "line": (
            f"plan-proof · {verified}/{done_total} verified"
            + ("" if ok else f" · FAIL {len(violations)} done-without-receipt")
        ),
    }

    if fix_schema and PLAN.is_file():
        plan["schema"] = "outbound-factory-100-upgrade-plan-v3"
        plan["version"] = "3.0.0"
        plan["execution_proof_law"] = LAW
        plan["saved_at"] = _now()
        PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Validate outbound plan execution proof")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--fix-schema", action="store_true", help="Bump plan to v3 schema")
    args = ap.parse_args()
    row = validate(fix_schema=args.fix_schema)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["line"])
        for v in row.get("violations") or []:
            print(f"  FAIL · {v.get('id')} · {v.get('issue')}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
