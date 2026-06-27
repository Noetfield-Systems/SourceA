#!/usr/bin/env python3
"""Seed Pure Flow (Sunflow) Worker INBOX from 444-plan queue."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BATCH_PATH = ROOT / "data/pureflow-upgrade-queue-444-locked-v1.json"
ACTIVE_PATH = ROOT / "data/pureflow-upgrade-queue-active-v1.json"
STATE_PATH = Path.home() / ".sina/pureflow-worker-queue-state-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _load() -> tuple[dict, dict]:
    if not BATCH_PATH.is_file():
        raise SystemExit(f"Missing batch — run: python3 scripts/generate_pureflow_upgrade_queue_444_v1.py")
    batch = json.loads(BATCH_PATH.read_text(encoding="utf-8"))
    active = json.loads(ACTIVE_PATH.read_text(encoding="utf-8")) if ACTIVE_PATH.is_file() else {}
    return batch, active


def _plan_by_id(batch: dict, plan_id: str) -> dict | None:
    for p in batch.get("plans") or []:
        if p.get("id") == plan_id:
            return p
    return None


def _head_plan(batch: dict, active: dict) -> dict:
    head_id = str(active.get("head_id") or "pf-upg-001")
    plan = _plan_by_id(batch, head_id)
    if not plan:
        plan = (batch.get("plans") or [None])[0]
    if not plan:
        raise SystemExit("Empty batch")
    return plan


def seed_inbox(plan: dict, *, pos: int, total: int) -> dict:
    sys.path.insert(0, str(ROOT / "scripts"))
    from worker_inject_lib import deliver_to_worker_inbox  # noqa: WPS433

    meta = {
        "sa_id": plan["id"],
        "queue_role": plan.get("queue_role") or "act",
        "queue_pos": pos,
        "queue_total": total,
        "stack": "pureflow",
        "worker_lane": "sunflow_worker",
        "pillar": plan.get("pillar"),
        "competitor": plan.get("competitor"),
        "work_root": plan.get("work_root"),
    }
    return deliver_to_worker_inbox(
        plan["prompt"],
        source="pureflow_worker_queue",
        meta=meta,
        mark_pending=True,
        fast=True,
    )


def advance_active(active: dict, completed_id: str) -> dict:
    completed = list(active.get("completed") or [])
    if completed_id not in completed:
        completed.append(completed_id)
    n = int(active.get("head_n") or 1) + 1
    if n > int(active.get("count") or 444):
        active["queue_exhausted"] = True
        active["saved_at"] = _now()
        return active
    head_id = f"pf-upg-{n:03d}"
    active.update(
        {
            "head_id": head_id,
            "head_n": n,
            "completed": completed,
            "saved_at": _now(),
            "queue_exhausted": False,
        }
    )
    return active


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--next", action="store_true", help="Seed head plan into Worker INBOX")
    ap.add_argument("--advance", metavar="ID", help="Mark plan done and advance head")
    ap.add_argument("--status", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    batch, active = _load()
    total = int(batch.get("count") or 444)

    if args.advance:
        active = advance_active(active, args.advance)
        ACTIVE_PATH.write_text(json.dumps(active, indent=2) + "\n", encoding="utf-8")

    if args.status or (not args.next and not args.advance):
        plan = _head_plan(batch, active)
        out = {
            "ok": True,
            "head_id": plan["id"],
            "head_n": plan["n"],
            "total": total,
            "title": plan["title"],
            "pillar": plan.get("pillar"),
            "queue_exhausted": active.get("queue_exhausted"),
            "completed_count": len(active.get("completed") or []),
        }
        print(json.dumps(out, indent=2))
        return 0

    if args.next:
        plan = _head_plan(batch, active)
        pos = int(plan.get("n") or 1)
        result = seed_inbox(plan, pos=pos, total=total)
        state = {
            "schema": "pureflow-worker-queue-state-v1",
            "updated_at": _now(),
            "head_id": plan["id"],
            "head_n": pos,
            "total": total,
            "last_seed": result,
        }
        STATE_PATH.parent.mkdir(parents=True, exist_ok=True)
        STATE_PATH.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
        out = {"ok": result.get("ok", False), "plan_id": plan["id"], "title": plan["title"], "deliver": result}
        print(json.dumps(out, indent=2))
        return 0 if out["ok"] else 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
