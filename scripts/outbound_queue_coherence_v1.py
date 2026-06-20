#!/usr/bin/env python3
"""Outbound queue ↔ plan ↔ inbox coherence — anti-theater SSOT checks + heal."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
DEBUG_LOG = ROOT / ".cursor" / "debug-e6507c.log"
PLAN = ROOT / "data/outbound-factory-100-upgrade-plan-v1.json"
UNIFIED_QUEUE = ROOT / "data/plans-unified-worker-queue-v1.json"
PHASE0_REF = ROOT / "data/phase0-freemium-sandbox-reference-v1.json"
FULL_STACK = ROOT / "data/sourcea-full-stack-100-fix-plan-v1.json"
BRAIN_PLAN = ROOT / "data/brain-cloud-reasoning-1000-upgrade-plan-v1.json"
RECEIPT = SINA / "outbound-queue-coherence-receipt-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _queue_head() -> dict:
    q = _read(SINA / "healthy-queue-30-active.json")
    items = q.get("queue") or []
    return items[0] if items else {}


def _dbg(hypothesis_id: str, location: str, message: str, data: dict) -> None:
    # #region agent log
    try:
        import json
        import time

        DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with DEBUG_LOG.open("a", encoding="utf-8") as fh:
            fh.write(
                json.dumps(
                    {
                        "sessionId": "e6507c",
                        "hypothesisId": hypothesis_id,
                        "location": location,
                        "message": message,
                        "data": data,
                        "timestamp": int(time.time() * 1000),
                        "runId": "pre-fix",
                    }
                )
                + "\n"
            )
    except OSError:
        pass
    # #endregion


def _plan_row(upgrade_id: str) -> dict:
    """Resolve plan status across outbound + unified plans queue (anti-fragmentation)."""
    if not upgrade_id:
        return {}

    phase0 = _read(PHASE0_REF)
    for item in phase0.get("inventory") or []:
        if str(item.get("id")) == upgrade_id:
            return {
                "id": upgrade_id,
                "status": item.get("status") or "planned",
                "plan_source": "phase0_freemium",
                "execution_proof": item.get("execution_proof"),
                "completed_at": item.get("completed_at"),
            }

    plan = _read(PLAN)
    for u in plan.get("upgrades") or []:
        if str(u.get("id")) == upgrade_id:
            return u

    uq = _read(UNIFIED_QUEUE)
    fs = _read(FULL_STACK)
    brain = _read(BRAIN_PLAN)

    # Authoritative plan rows beat unified assignment mirror (F* full-stack · B* brain).
    for fix in fs.get("fixes") or []:
        if str(fix.get("id")) == upgrade_id:
            row = dict(fix)
            row["plan_source"] = "full_stack_100"
            return row

    for u in brain.get("upgrades") or []:
        if str(u.get("id")) == upgrade_id:
            row = dict(u)
            row["plan_source"] = "brain_cloud_1000"
            return row

    # #region agent log
    candidates: dict[str, str] = {}
    for item in phase0.get("inventory") or []:
        if str(item.get("id")) == upgrade_id:
            candidates["phase0"] = str(item.get("status") or "")
    for u in plan.get("upgrades") or []:
        if str(u.get("id")) == upgrade_id:
            candidates["outbound"] = str(u.get("status") or "")
    for a in uq.get("assignments") or []:
        if str(a.get("upgrade_id")) == upgrade_id:
            candidates["unified_queue"] = str(a.get("status") or "")
    for fix in fs.get("fixes") or []:
        if str(fix.get("id")) == upgrade_id:
            candidates["full_stack"] = str(fix.get("status") or "")
    for u in brain.get("upgrades") or []:
        if str(u.get("id")) == upgrade_id:
            candidates["brain"] = str(u.get("status") or "")
    # #endregion

    for a in uq.get("assignments") or []:
        if str(a.get("upgrade_id")) == upgrade_id:
            # #region agent log
            _dbg(
                "H1",
                "outbound_queue_coherence_v1.py:_plan_row",
                "unified_queue_fallback",
                {
                    "upgrade_id": upgrade_id,
                    "chosen": "unified_queue",
                    "chosen_status": a.get("status"),
                    "candidates": candidates,
                },
            )
            # #endregion
            return {
                "id": upgrade_id,
                "status": a.get("status") or "planned",
                "plan_source": a.get("plan"),
                "execution_proof": (
                    {"receipt_path": a.get("receipt_path")}
                    if a.get("receipt_path")
                    else None
                ),
            }

    return {}


def assess_queue_coherence() -> dict:
    """Machine checks validators were missing — stale head · orphans · inbox latch."""
    head = _queue_head()
    head_uid = str(head.get("upgrade_id") or "")
    head_sa = str(head.get("sa_id") or "")
    plan_row = _plan_row(head_uid)
    plan_status = str(plan_row.get("status") or "")

    plan = _read(PLAN)
    queue = _read(SINA / "healthy-queue-30-active.json")
    queue_ids = {str(i.get("upgrade_id") or "") for i in (queue.get("queue") or [])}
    orphans = [
        str(u.get("id") or "")
        for u in plan.get("upgrades") or []
        if u.get("status") == "in_progress" and str(u.get("id") or "") not in queue_ids
    ]

    inbox = _read(SINA / "worker-prompt-inbox-v1.json")
    inbox_pending = bool(inbox.get("pending"))
    inbox_sa = str(inbox.get("sa_id") or (inbox.get("meta") or {}).get("sa_id") or "")
    inbox_uid = str((inbox.get("meta") or {}).get("upgrade_id") or "")

    active_wo = _read(SINA / "brain-outbound-work-order-active-v1.json")
    local_worker = active_wo.get("execution_mode") == "local_worker"

    sys.path.insert(0, str(SCRIPTS))
    from outbound_receipt_path_v1 import receipt_done_exists  # noqa: WPS433

    head_receipt = (
        receipt_done_exists(upgrade_id=head_uid, sa_id=head_sa) if head_uid and head_sa else False
    )

    # #region agent log
    _dbg(
        "H2",
        "outbound_queue_coherence_v1.py:assess_queue_coherence",
        "head_coherence_state",
        {
            "head_uid": head_uid,
            "head_sa": head_sa,
            "plan_status": plan_status,
            "plan_source": plan_row.get("plan_source") or plan_row.get("plan") or "unknown",
            "head_receipt": head_receipt,
            "inbox_pending": inbox_pending,
        },
    )
    # #endregion

    checks = {
        "queue_head_not_done": plan_status != "done",
        "no_orphan_in_progress": len(orphans) == 0,
        "no_head_receipt_without_done": not (head_receipt and plan_status != "done"),
        "inbox_matches_head_when_pending": (
            (not inbox_pending)
            or (inbox_sa == head_sa and (not inbox_uid or inbox_uid == head_uid))
        ),
        "local_worker_inbox_latch": (
            (not local_worker)
            or (str(active_wo.get("upgrade_ref") or "") != head_uid)
            or inbox_pending
        ),
    }

    issues: list[str] = []
    if not checks["queue_head_not_done"]:
        issues.append(f"stale_queue_head:{head_uid}:plan=done:queue_pos=1")
    if orphans:
        issues.append(f"orphan_in_progress:{','.join(orphans)}")
    if head_receipt and plan_status != "done":
        issues.append(f"head_receipt_without_plan_done:{head_uid}")
    if plan_status != "done" and local_worker and str(active_wo.get("upgrade_ref") or "") == head_uid:
        if not inbox_pending:
            issues.append(f"inbox_missing_local_worker:{head_sa}:{head_uid}")
    if inbox_pending and inbox_uid and inbox_uid != head_uid:
        issues.append(f"inbox_upgrade_mismatch:inbox={inbox_uid}:head={head_uid}")

    done_total = sum(1 for u in plan.get("upgrades") or [] if u.get("status") == "done")
    ok = all(checks.values())

    return {
        "schema": "outbound-queue-coherence-v1",
        "at": _now(),
        "ok": ok,
        "head": {"upgrade_id": head_uid, "sa_id": head_sa, "plan_status": plan_status},
        "orphan_in_progress": orphans,
        "outbound_done": done_total,
        "outbound_total": len(plan.get("upgrades") or []),
        "checks": checks,
        "issues": issues,
        "line": (
            f"queue-coherence · head={head_uid} · plan={plan_status}"
            + ("" if ok else f" · BLOCK:{issues[0]}")
        ),
    }


def compose_outbound_progress_line() -> str:
    """Separate outbound factory progress from factory-now Valid YES 1000."""
    row = assess_queue_coherence()
    head = row.get("head") or {}
    done = int(row.get("outbound_done") or 0)
    total = int(row.get("outbound_total") or 100)
    uid = head.get("upgrade_id") or "?"
    sa = head.get("sa_id") or "?"
    status = head.get("plan_status") or "?"
    return f"outbound · {done}/{total} done · head={uid} · plan={status} · sa={sa}"


def heal_orphan_in_progress(*, write: bool = True) -> dict:
    row = assess_queue_coherence()
    orphans = row.get("orphan_in_progress") or []
    if not orphans or not write:
        return {"ok": True, "reset": [], "skipped": not orphans}
    plan = _read(PLAN)
    reset: list[str] = []
    for u in plan.get("upgrades") or []:
        if str(u.get("id") or "") not in orphans:
            continue
        u["status"] = "planned"
        u.pop("done_at", None)
        u.pop("execution_proof", None)
        u["heal_note"] = "orphan_in_progress reset by outbound_queue_coherence_v1"
        u["heal_at"] = _now()
        reset.append(u["id"])
    if reset:
        plan["saved_at"] = _now()
        PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "reset": reset}


def rebuild_queue_and_deliver(*, sync: bool = True) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from outbound_factory_queue_assign_v1 import (  # noqa: WPS433
        build_assignment,
        deliver_head,
        sync_truth,
        write_queue,
    )

    bundle = build_assignment()
    write_row = write_queue(bundle)
    deliver_row = deliver_head(bundle)
    sync_row = sync_truth() if sync else {"skipped": True}
    head = bundle.get("head") or {}
    return {
        "ok": bool(write_row.get("ok")),
        "head_upgrade": head.get("upgrade_id"),
        "head_sa": head.get("sa_id"),
        "total": bundle.get("total"),
        "write": write_row,
        "deliver": deliver_row,
        "sync": sync_row,
    }


def heal_stale_queue(*, write: bool = True) -> dict:
    """Rebuild queue when head upgrade is already done on plan."""
    row = assess_queue_coherence()
    if row.get("checks", {}).get("queue_head_not_done"):
        return {"ok": True, "skipped": True, "reason": "head_not_stale"}
    if not write:
        return {"ok": False, "dry_run": True, "would_rebuild": True, "issues": row.get("issues")}
    heal_orphan_in_progress(write=True)
    rebuilt = rebuild_queue_and_deliver(sync=True)
    after = assess_queue_coherence()
    return {
        "ok": after.get("ok"),
        "rebuilt": rebuilt,
        "before_issues": row.get("issues"),
        "after": after,
    }


def heal_all(*, write: bool = True) -> dict:
    steps = {
        "orphans": heal_orphan_in_progress(write=write),
        "stale_queue": heal_stale_queue(write=write),
    }
    final = assess_queue_coherence()
    row = {
        "schema": "outbound-queue-coherence-heal-v1",
        "at": _now(),
        "ok": final.get("ok"),
        "steps": steps,
        "coherence": final,
        "line": final.get("line"),
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    ap = argparse.ArgumentParser(description="Outbound queue coherence assess/heal")
    ap.add_argument("command", nargs="?", default="assess", choices=("assess", "heal"))
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = heal_all() if args.command == "heal" else assess_queue_coherence()
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line") or row.get("coherence", {}).get("line"))
    ok = row.get("ok")
    if ok is None:
        ok = (row.get("coherence") or {}).get("ok")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
