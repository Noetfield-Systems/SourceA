#!/usr/bin/env python3
"""Assign remaining outbound-factory upgrade plan items to loop dispatch queue.

Reads: data/outbound-factory-100-upgrade-plan-v1.json (v2)
Writes: data/outbound-factory-worker-queue-v1.json
        ~/.sina/healthy-queue-30-active.json
        ~/.sina/worker-prompt-inbox-v1.json (legacy relay — Brain work-order primary when Auto Runtime)
        .sina-loop/INBOX.md
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
PLAN = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"
QUEUE_SSOT = ROOT / "data" / "outbound-factory-worker-queue-v1.json"
QUEUE_HOME = SINA / "healthy-queue-30-active.json"
QUEUE_REPO = ROOT / "brain-os" / "plan-registry" / "sourcea-1000" / "prompts" / "healthy-queue-30-active.json"
STATE_HOME = SINA / "healthy-queue-state-v1.json"
PROMPT_COMPOSER_RECEIPT = SINA / "prompt-composer-receipt-v1.json"
PHASE = "phase-s6-outbound-factory-upgrade"
SA_BASE = 1100

sys.path.insert(0, str(SCRIPTS))
from outbound_receipt_path_v1 import canonical_receipt_rel  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _pending_upgrades(plan: dict) -> list[dict]:
    rows = [u for u in (plan.get("upgrades") or []) if u.get("status") != "done"]
    rows.sort(key=lambda u: u.get("id", ""))
    return rows


def _sa_id(n: int) -> str:
    return f"sa-{SA_BASE + n - 1:04d}"


def _advisory_block(item: dict) -> str:
    adv = _read_json(SINA / "future-loop-prompt-advisory-v1.json")
    if not adv or adv.get("schema") != "future-loop-prompt-advisory-v1":
        return ""
    top = (adv.get("ranked_prompts") or [{}])[0]
    if str(top.get("upgrade_id") or "") != str(item.get("id") or ""):
        top = next(
            (r for r in (adv.get("ranked_prompts") or []) if r.get("upgrade_id") == item.get("id")),
            top,
        )
    return (
        f"ADVISORY — hash `{adv.get('deterministic_hash', '?')}` · "
        f"top={top.get('upgrade_id', '?')} conf={top.get('confidence', '?')} · "
        f"{adv.get('compile_sequence', '')}\n\n"
    )


def _prompt_for(item: dict, *, pos: int, total: int, sa_id: str) -> str:
    uid = item.get("id", "")
    title = item.get("title", "")
    wired = item.get("wired_to", "")
    acceptance = item.get("acceptance", "")
    lane = item.get("lane_label") or item.get("lane", "")
    advisory = _advisory_block(item)
    return (
        f"[GOAL1_HEALTHY_DRAIN pos={pos}/{total}] sa={sa_id} role=act · outbound-factory-upgrade\n\n"
        f"{advisory}"
        f"WORK: Implement **{uid}** — {title}\n"
        f"Lane: {lane}\n"
        f"Plan SSOT: data/outbound-factory-100-upgrade-plan-v1.json\n"
        f"Salvage law: data/outbound-factory-salvage-spec-v1.json\n"
        f"Wired to: {wired}\n"
        f"Acceptance: {acceptance}\n\n"
        f"RECEIPT — close with `receipts/{uid}-{sa_id}-receipt.json` · mark plan row `{uid}` status=done\n\n"
        f"ACT — wire minimal diff · verify acceptance · mark {uid} status=done in plan JSON · "
        f"run `python3 scripts/outbound_factory_upgrade_pulse_v1.py` · broker-submit · STOP\n"
        f"Do NOT auto-send email · Sina read remains ship authority"
    )


def build_assignment(*, plan: dict | None = None) -> dict:
    plan = plan or _read_json(PLAN)
    pending = _pending_upgrades(plan)
    total = len(pending)
    queue_items: list[dict] = []
    catalog: list[dict] = []

    for pos, item in enumerate(pending, start=1):
        sa_id = _sa_id(pos)
        prompt = _prompt_for(item, pos=pos, total=total, sa_id=sa_id)
        row = {
            "queue_pos": pos,
            "hp_id": f"ofu-{item.get('id', pos)}",
            "queue_role": "act",
            "step_type": "implement",
            "sa_id": sa_id,
            "sa_path": f"data/outbound-factory-100-upgrade-plan-v1.json#{item.get('id')}",
            "sa_title": f"{item.get('id')} — {item.get('title', '')[:80]}",
            "sa_tier": str(item.get("tier") or "P1"),
            "phase": PHASE,
            "upgrade_id": item.get("id"),
            "upgrade_lane": item.get("lane"),
            "title": f"[ACT] {item.get('id')} — {item.get('title', '')[:72]}",
            "instruction": prompt,
            "verify": f"acceptance: {item.get('acceptance', '')}",
            "closeout": True,
            "one_sa_per_turn": True,
        }
        queue_items.append(row)
        catalog.append(
            {
                "upgrade_id": item.get("id"),
                "tier": item.get("tier"),
                "lane": item.get("lane"),
                "sa_id": sa_id,
                "queue_pos": pos,
                "title": item.get("title"),
                "status": "assigned",
            }
        )

    sa_range = [_sa_id(1), _sa_id(total)] if total else []
    doc = {
        "schema": "healthy-queue-30-active.v1",
        "product": f"Outbound Factory Upgrade drain — {total} items (W3–W5)",
        "thread": "OUTBOUND-FACTORY",
        "repo": "sourcea",
        "count": total,
        "rhythm": "1 act per upgrade · verify · mark done in plan",
        "law": "data/outbound-factory-salvage-spec-v1.json · outbound-factory-upgrade-plan-v2",
        "generated_at": _now(),
        "phase_strict": False,
        "phase_strict_complete": total == 0,
        "queue_exhausted": total == 0,
        "stop_reason": "outbound_factory_complete" if total == 0 else None,
        "pick_floor": None,
        "sa_range": sa_range,
        "upgrade_plan_schema": plan.get("schema"),
        "maturity_level": (plan.get("maturity") or {}).get("current_level"),
        "active_wave": plan.get("active_wave"),
        "queue": queue_items,
    }
    ssot = {
        "schema": "outbound-factory-worker-queue-v1",
        "version": "1.0.0",
        "saved_at": _now(),
        "plan_path": str(PLAN.relative_to(ROOT)),
        "phase": PHASE,
        "sa_range": sa_range,
        "total": total,
        "assignments": catalog,
        "command": "python3 scripts/outbound_factory_queue_assign_v1.py --deliver-first",
    }
    return {"queue_doc": doc, "ssot": ssot, "head": queue_items[0] if queue_items else None, "total": total}


def write_prompt_composer_receipt(*, head: dict | None, deliver: dict, blocked: bool = False) -> dict:
    row = {
        "schema": "prompt-composer-receipt-v1",
        "at": _now(),
        "sa_id": (head or {}).get("sa_id"),
        "upgrade_id": (head or {}).get("upgrade_id"),
        "queue_pos": (head or {}).get("queue_pos"),
        "phase": PHASE,
        "blocked": blocked,
        "deliver_ok": deliver.get("ok"),
        "blocked_by_freeze": deliver.get("blocked_by_freeze"),
        "prompt_blocked_by_freeze": deliver.get("prompt_blocked_by_freeze"),
        "receipt_path": canonical_receipt_rel(
            upgrade_id=str((head or {}).get("upgrade_id") or "U000"),
            sa_id=str((head or {}).get("sa_id") or "sa-XXXX"),
        ),
        "plan_row": f"data/outbound-factory-100-upgrade-plan-v1.json#{(head or {}).get('upgrade_id')}",
        "command": "python3 scripts/outbound_factory_queue_assign_v1.py --deliver-first",
    }
    SINA.mkdir(parents=True, exist_ok=True)
    PROMPT_COMPOSER_RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def write_queue(bundle: dict, *, write_plan_tags: bool = True) -> dict:
    doc = bundle["queue_doc"]
    ssot = bundle["ssot"]
    total = bundle["total"]
    QUEUE_SSOT.parent.mkdir(parents=True, exist_ok=True)
    QUEUE_SSOT.write_text(json.dumps(ssot, indent=2) + "\n", encoding="utf-8")
    SINA.mkdir(parents=True, exist_ok=True)
    QUEUE_HOME.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    if QUEUE_REPO.parent.is_dir():
        QUEUE_REPO.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    STATE_HOME.write_text(
        json.dumps(
            {
                "next_pos": 1,
                "queue_exhausted": total == 0,
                "last_advanced_at": _now(),
                "last_completed_pos": 0,
                "reset_by": "outbound_factory_queue_assign_v1",
                "phase": PHASE,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    if write_plan_tags and PLAN.is_file():
        plan = _read_json(PLAN)
        by_id = {a["upgrade_id"]: a for a in ssot.get("assignments") or []}
        for u in plan.get("upgrades") or []:
            if u.get("id") in by_id:
                u["worker_sa_id"] = by_id[u["id"]]["sa_id"]
                u["worker_queue_pos"] = by_id[u["id"]]["queue_pos"]
                u["worker_status"] = "assigned"
        plan["worker_queue"] = {
            "assigned_at": _now(),
            "phase": PHASE,
            "total": total,
            "sa_range": ssot.get("sa_range"),
            "ssot": str(QUEUE_SSOT.relative_to(ROOT)),
        }
        plan["saved_at"] = _now()
        PLAN.write_text(json.dumps(plan, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "total": total, "sa_range": ssot.get("sa_range"), "ssot": str(QUEUE_SSOT)}


def deliver_head(bundle: dict) -> dict:
    head = bundle.get("head")
    if not head:
        return {"ok": False, "error": "empty_queue"}
    sys.path.insert(0, str(SCRIPTS))
    from brain_outbound_work_order_v1 import (  # noqa: WPS433
        LOCAL_WORKER_LANES,
        brain_work_order_enabled,
        dispatch_current,
    )

    upgrade_lane = str(head.get("upgrade_lane") or "")
    local_lane = upgrade_lane in LOCAL_WORKER_LANES

    if brain_work_order_enabled() and not local_lane:
        deliver = dispatch_current(dry_run=False, advance_queue=False, mode="sign_only")
        write_prompt_composer_receipt(
            head=head,
            deliver={"ok": bool(deliver.get("ok")), "brain_work_order": True, **deliver},
            blocked=not deliver.get("ok"),
        )
        return deliver

    if brain_work_order_enabled() and local_lane:
        dispatch_current(dry_run=False, advance_queue=False, mode="sign_only")

    from worker_inject_lib import act_blocked_by_freeze, deliver_to_worker_inbox  # noqa: WPS433

    def _deliver_local() -> dict:
        meta = {
            "sa_id": head["sa_id"],
            "queue_role": head["queue_role"],
            "queue_pos": head["queue_pos"],
            "queue_total": bundle["total"],
            "queue_exhausted": False,
            "phase": PHASE,
            "upgrade_id": head.get("upgrade_id"),
        }
        return deliver_to_worker_inbox(
            head["instruction"],
            source="healthy-drain-orchestrator",
            meta=meta,
            mark_pending=True,
            fast=True,
        )

    if local_lane:
        deliver = _deliver_local()
        if not deliver.get("ok") and deliver.get("error") in (
            "SA_ALREADY_IN_CURSOR_QUEUE_TURN_BIND",
            "COOLDOWN_SAME_TURN",
        ):
            from healthy_pack_bind_lib_v1 import clear_stale_turn_bind  # noqa: WPS433
            from worker_turn_lib import close_turn  # noqa: WPS433
            from duplicate_inject_guard_v1 import clear_inject_lock  # noqa: WPS433

            clear_stale_turn_bind()
            close_turn(sa_id=str(head.get("sa_id") or ""), force=True)
            clear_inject_lock()
            deliver = _deliver_local()
        write_prompt_composer_receipt(head=head, deliver=deliver, blocked=not deliver.get("ok"))
        return deliver

    freeze = act_blocked_by_freeze(queue_role=str(head.get("queue_role") or "act"))
    if freeze.get("blocked"):
        from worker_inject_lib import clear_inbox  # noqa: WPS433

        cleared = clear_inbox(reason="outbound_assign_freeze_blocked")
        deliver = {
            "ok": True,
            "blocked_by_freeze": True,
            "prompt_blocked_by_freeze": True,
            "action": freeze.get("action"),
            "cleared_inbox": cleared,
        }
        write_prompt_composer_receipt(head=head, deliver=deliver, blocked=True)
        return deliver

    meta = {
        "sa_id": head["sa_id"],
        "queue_role": head["queue_role"],
        "queue_pos": head["queue_pos"],
        "queue_total": bundle["total"],
        "queue_exhausted": False,
        "phase": PHASE,
        "upgrade_id": head.get("upgrade_id"),
    }
    deliver = deliver_to_worker_inbox(
        head["instruction"],
        source="healthy-drain-orchestrator",
        meta=meta,
        mark_pending=True,
        fast=True,
    )
    write_prompt_composer_receipt(head=head, deliver=deliver, blocked=bool(deliver.get("blocked_by_freeze")))
    return deliver


def sync_truth() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    try:
        from queue_ssot_unify_v1 import unify_queue_ssot  # noqa: WPS433

        return unify_queue_ssot(write_brain=True, rebuild_factory=True, fast=True)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def main() -> int:
    ap = argparse.ArgumentParser(description="Assign outbound factory upgrades to Worker queue")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--deliver-first", action="store_true", help="Deliver queue head to worker inbox")
    ap.add_argument("--sync", action="store_true", help="Run queue_ssot_unify after write")
    args = ap.parse_args()
    bundle = build_assignment()
    if args.dry_run:
        out = {"dry_run": True, "total": bundle["total"], "head_sa": (bundle.get("head") or {}).get("sa_id")}
        print(json.dumps(out, indent=2) if args.json else f"dry-run · {out['total']} items · head {out['head_sa']}")
        return 0
    write_row = write_queue(bundle)
    deliver_row = deliver_head(bundle) if args.deliver_first else {"skipped": True}
    sync_row = sync_truth() if args.sync or args.deliver_first else {"skipped": True}
    out = {"assign": write_row, "deliver": deliver_row, "sync": sync_row}
    if args.json:
        print(json.dumps(out, indent=2))
    else:
        print(
            f"OK: assigned {write_row['total']} upgrades · "
            f"sa {write_row['sa_range'][0]}–{write_row['sa_range'][-1]} · "
            f"deliver={deliver_row.get('ok', deliver_row.get('skipped'))}"
        )
    return 0 if write_row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
