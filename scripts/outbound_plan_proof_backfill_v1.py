#!/usr/bin/env python3
"""Backfill outbound plan execution_proof from disk receipts — reset dishonest done rows.

Scans receipts/ and shipped_evidence on plan rows. Rows marked done without proof
are reset to planned (or in_progress when worker_sa_id assigned).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"
RECEIPTS = ROOT / "receipts"
LOGS = ROOT / "REPO_EXECUTION_LOGS" / "sourcea"
SINA = Path.home() / ".sina"
RECEIPT_OUT = SINA / "outbound-plan-proof-backfill-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _receipt_path_rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


sys.path.insert(0, str(ROOT / "scripts"))
from outbound_receipt_path_v1 import index_receipts_by_upgrade, receipt_exists, resolve_receipt_file  # noqa: E402


def _receipt_exists(u: dict) -> tuple[bool, str, str]:
    """Return ok, receipt_path_rel, sa_id — canonical upgrade match only."""
    uid = str(u.get("id") or "")
    proof = u.get("execution_proof") or {}
    sa_id = str(proof.get("sa_id") or u.get("worker_sa_id") or "")
    if uid and sa_id and receipt_exists(upgrade_id=uid, sa_id=sa_id):
        _, rel = resolve_receipt_file(upgrade_id=uid, sa_id=sa_id)
        return True, rel, sa_id
    return False, "", ""


def _scan_logs_for_upgrade(upgrade_id: str) -> tuple[str, str] | None:
    if not LOGS.is_dir():
        return None
    pat = re.compile(re.escape(upgrade_id))
    for p in sorted(LOGS.glob("*"), reverse=True):
        if p.suffix not in (".yaml", ".json", ".yml"):
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if not pat.search(text):
            continue
        m = re.search(r"(sa-\d{4})", p.name)
        if m:
            sa_id = m.group(1)
            rp = RECEIPTS / f"{sa_id}-receipt.json"
            if rp.is_file():
                return sa_id, _receipt_path_rel(rp)
    return None


def run_backfill(*, write: bool = True, dry_run: bool = False) -> dict:
    plan = _read_json(PLAN)
    upgrades = plan.get("upgrades") or []
    by_upgrade = index_receipts_by_upgrade()

    backfilled: list[str] = []
    reset: list[str] = []
    kept: list[str] = []

    for u in upgrades:
        if u.get("status") != "done":
            continue
        uid = str(u.get("id") or "")
        ok, rp, sa_id = _receipt_exists(u)
        if ok:
            if not u.get("execution_proof") and write and not dry_run:
                u["execution_proof"] = {
                    "sa_id": sa_id,
                    "receipt_path": rp,
                    "pulse_verified": True,
                    "backfill_at": _now(),
                }
            kept.append(uid)
            continue

        found: tuple[str, str] | None = by_upgrade.get(uid)
        if not found:
            found = _scan_logs_for_upgrade(uid)

        if found:
            sa_id, rp = found
            if write and not dry_run:
                u["execution_proof"] = {
                    "sa_id": sa_id,
                    "receipt_path": rp,
                    "pulse_verified": True,
                    "backfill_at": _now(),
                }
            backfilled.append(uid)
            kept.append(uid)
            continue

        shipped = u.get("shipped_evidence") or {}
        if shipped.get("script") and shipped.get("at") and not shipped.get("receipt_path"):
            if write and not dry_run:
                u["shipped_evidence_note"] = "shipped_without_receipt — not sufficient for done"
            # fall through to reset

        new_status = "in_progress" if u.get("worker_sa_id") else "planned"
        if write and not dry_run:
            u["status"] = new_status
            u.pop("done_at", None)
            u.pop("execution_proof", None)
            u.pop("shipped_evidence", None)
            u["reset_note"] = "done_without_receipt — reset by outbound_plan_proof_backfill_v1"
            u["reset_at"] = _now()
        reset.append(uid)

    if write and not dry_run:
        done = sum(1 for x in upgrades if x.get("status") == "done")
        planned = sum(1 for x in upgrades if x.get("status") == "planned")
        in_prog = sum(1 for x in upgrades if x.get("status") == "in_progress")
        p0_done = sum(1 for x in upgrades if x.get("status") == "done" and x.get("tier") == "P0")
        p1_done = sum(1 for x in upgrades if x.get("status") == "done" and x.get("tier") == "P1")
        plan["progress"] = {
            "done_total": done,
            "planned_total": planned + in_prog,
            "in_progress_total": in_prog,
            "p0_done": p0_done,
            "p1_done": p1_done,
            "pct": round(100 * done / max(len(upgrades), 1)),
        }
        plan["saved_at"] = _now()
        PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")

    row = {
        "schema": "outbound-plan-proof-backfill-receipt-v1",
        "at": _now(),
        "dry_run": dry_run,
        "kept_done": kept,
        "backfilled": backfilled,
        "reset_to_planned": reset,
        "kept_count": len(kept),
        "backfilled_count": len(backfilled),
        "reset_count": len(reset),
        "line": (
            f"outbound-proof-backfill · kept={len(kept)} · backfilled={len(backfilled)} · reset={len(reset)}"
        ),
    }
    if write and not dry_run:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT_OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Backfill outbound plan execution proof")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = run_backfill(write=not args.no_write, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row["line"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
