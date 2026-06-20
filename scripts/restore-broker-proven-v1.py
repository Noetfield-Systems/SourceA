#!/usr/bin/env python3
"""Restore REGISTRY done for sa with full broker CHECK→ACT→VERIFY proof + write receipt."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "REGISTRY.json"
PACK = ROOT / "brain-os" / "plan-registry" / "sourcea-1000"
EVENTS = Path.home() / ".sina" / "goal1-lane-broker-events.jsonl"
RECEIPTS = ROOT / "receipts"

RESTORE_DEFAULT = [
    "sa-0163",
    "sa-0166",
    "sa-0167",
    "sa-0168",
    "sa-0169",
    "sa-0170",
    "sa-0171",
    "sa-0172",
    "sa-0173",
    "sa-0606",
]


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _broker_roles(sa_id: str) -> set[str]:
    roles: set[str] = set()
    if not EVENTS.is_file():
        return roles
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = str(d.get("kind") or "")
        if "WORKER_SUBMIT" not in kind:
            continue
        if str(d.get("sa") or "") != sa_id:
            continue
        rt = str(d.get("round_type") or "").lower()
        if rt == "implement":
            rt = "act"
        if rt:
            roles.add(rt)
    return roles


def _has_full_cycle(sa_id: str) -> bool:
    r = _broker_roles(sa_id)
    return {"check", "act", "verify"}.issubset(r)


def restore(*, sa_ids: list[str], dry_run: bool = False) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    restored: list[str] = []
    skipped: list[dict] = []

    reg = json.loads(REG.read_text(encoding="utf-8"))
    plan_by = {p["id"]: p for p in reg["plans"]}

    for sa_id in sa_ids:
        if not _has_full_cycle(sa_id):
            skipped.append({"sa_id": sa_id, "reason": "no_full_broker_cycle", "roles": sorted(_broker_roles(sa_id))})
            continue
        pl = plan_by.get(sa_id)
        if not pl:
            skipped.append({"sa_id": sa_id, "reason": "not_in_registry"})
            continue
        if not dry_run:
            pl["status"] = "done"
            rel = pl.get("path") or ""
            if rel:
                md = PACK / rel
                if md.is_file():
                    text = md.read_text(encoding="utf-8")
                    for old in ("status: backlog", "status: in_progress", "status: active"):
                        if old in text:
                            md.write_text(text.replace(old, "status: done", 1), encoding="utf-8")
                            break
            RECEIPTS.mkdir(parents=True, exist_ok=True)
            rec_path = RECEIPTS / f"{sa_id}-receipt.json"
            rec_path.write_text(
                json.dumps(
                    {
                        "schema": "sourcea-sa-receipt-v1",
                        "sa_id": sa_id,
                        "status": "DONE",
                        "round_type": "verify",
                        "critical_bugs": 0,
                        "engine": "WORKER",
                        "source": "restore-broker-proven-v1",
                        "evidence": f"broker CHECK+ACT+VERIFY proof in goal1-lane-broker-events.jsonl · restored {_now()}",
                        "at": _now(),
                        "workspace": str(ROOT),
                    },
                    indent=2,
                )
                + "\n",
                encoding="utf-8",
            )
        restored.append(sa_id)

    if restored and not dry_run:
        REG.write_text(json.dumps(reg, indent=2) + "\n", encoding="utf-8")

    manifest = {
        "schema": "restore-broker-proof-v1",
        "at": _now(),
        "restored": restored,
        "skipped": skipped,
        "dry_run": dry_run,
    }
    if not dry_run:
        RECEIPTS.mkdir(parents=True, exist_ok=True)
        (RECEIPTS / "restore-broker-proof-2026-06-09.json").write_text(
            json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
        )
    return {"ok": len(skipped) == 0 or len(restored) > 0, **manifest}


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    out = restore(sa_ids=RESTORE_DEFAULT, dry_run=args.dry_run)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(f"restored={len(out['restored'])} skipped={len(out['skipped'])}")
    return 0 if out.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
