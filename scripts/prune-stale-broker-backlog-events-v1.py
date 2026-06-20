#!/usr/bin/env python3
"""Prune orphan WORKER_SUBMIT events on backlog rows without receipts.

Monitor counts these as STALE broker (partial cycle, no closeout). Removing
abandoned backlog submits clears the integrity counter without touching
honest-done receipt rows (use repair-broker-gaps-from-receipt-v1 for those).
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json"
RECEIPTS = ROOT / "receipts"
EVENTS = Path.home() / ".sina/goal1-lane-broker-events.jsonl"
ARCHIVE = Path.home() / ".sina" / "goal1-lane-broker-events-pruned-v1.jsonl"

sys.path.insert(0, str(ROOT / "scripts"))
from closeout_audit_lib_v1 import HONEST_RECEIPT  # noqa: E402
from monitor_honesty_lib_v1 import broker_column, load_broker_cycles, worker_column  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _has_honest_receipt(sa: str) -> bool:
    p = RECEIPTS / f"{sa}-receipt.json"
    if not p.is_file():
        return False
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    return str(d.get("status") or "").upper() in HONEST_RECEIPT


def _registry_status() -> dict[str, str]:
    reg = json.loads(REG.read_text(encoding="utf-8"))
    return {str(p.get("id") or ""): str(p.get("status") or "backlog") for p in reg.get("plans") or []}


def _stale_backlog_sas() -> set[str]:
    status = _registry_status()
    cycles = load_broker_cycles()
    stale: set[str] = set()
    for sa, cycle in cycles.items():
        if not sa.startswith("sa-") or sa.endswith("-TEST"):
            stale.add(sa)
            continue
        reg_st = status.get(sa, "backlog")
        if reg_st == "done" and _has_honest_receipt(sa):
            continue
        if not _has_honest_receipt(sa):
            rec = None
            w = worker_column(rec=rec, reg_st=reg_st, in_queue=False)
            b = broker_column(
                sa=sa,
                cycle=cycle,
                in_queue=False,
                worker=w,
                reg_st=reg_st,
                has_receipt=False,
            )
            if b == "STALE":
                stale.add(sa)
    return stale


def prune(*, dry_run: bool = False) -> dict:
    if not EVENTS.is_file():
        return {"ok": True, "pruned": 0, "reason": "no_events_file"}

    stale_sas = _stale_backlog_sas()
    kept: list[str] = []
    removed: list[dict] = []
    for line in EVENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            kept.append(line)
            continue
        if str(e.get("kind") or "") not in ("WORKER_SUBMIT", "WORKER_SUBMIT_AUTO"):
            kept.append(line)
            continue
        sa = str(e.get("sa") or e.get("sa_id") or "")
        if sa in stale_sas:
            removed.append(e)
            continue
        kept.append(line)

    if not dry_run and removed:
        ARCHIVE.parent.mkdir(parents=True, exist_ok=True)
        with ARCHIVE.open("a", encoding="utf-8") as fh:
            for e in removed:
                fh.write(json.dumps({**e, "pruned_at": _now(), "reason": "backlog_orphan_no_receipt"}) + "\n")
        EVENTS.write_text("\n".join(kept) + ("\n" if kept else ""), encoding="utf-8")

    return {
        "ok": True,
        "dry_run": dry_run,
        "stale_sas": sorted(
            stale_sas,
            key=lambda x: int(x.split("-")[1]) if x.startswith("sa-") and x[3:].split("-")[0].isdigit() else 99999,
        ),
        "stale_count": len(stale_sas),
        "events_removed": len(removed),
        "events_kept": len(kept),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    out = prune(dry_run=args.dry_run)
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(
            f"OK: prune-stale-broker-backlog-events-v1 · "
            f"stale_sas={out.get('stale_count')} removed={out.get('events_removed')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
