#!/usr/bin/env python3
"""Brain outbound work-order compiler (B0501) — sign · dispatch · federate · clear INBOX theater.

Replaces local Worker INBOX paste with Brain-signed work-orders → headless/cloud bay.
Law: docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md · data/brain-cloud-reasoning-1000-upgrade-plan-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
ACTIVE_PATH = SINA / "brain-outbound-work-order-active-v1.json"
REASONING_RECEIPT = SINA / "brain-outbound-reasoning-receipt-v1.json"
ORDERS_PATH = SINA / "fbe-work-orders-v1.json"
OUTBOUND_PLAN = ROOT / "data" / "outbound-factory-100-upgrade-plan-v1.json"
BRAIN_PLAN = ROOT / "data" / "brain-cloud-reasoning-1000-upgrade-plan-v1.json"
FULL_STACK_PLAN = ROOT / "data" / "sourcea-full-stack-100-fix-plan-v1.json"
BAY_SLUG = "outbound-fdg-icp"
BAY_BY_WIRED = {
    "icp4_one_product_line": BAY_SLUG,
}
LOCAL_WORKER_LANES: dict[str, str] = {
    "linter_oqg": "sourcea-local-linter",
    "telemetry": "sourcea-local-telemetry",
    "rrl_intelligence": "sourcea-local-rrl",
    "research_ingest": "sourcea-local-research",
    "sina_founder": "sourcea-local-founder",
    "anti_template": "sourcea-local-anti-template",
    "deferred_volume": "sourcea-local-deferred",
    "fdg_icp": "sourcea-local-fdg-icp",
    "icp4_one_product_line": "sourcea-local-fdg-icp",
}
BRAIN_MARK_IDS = ("B0501", "B0502", "B0503", "B0006")


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _write(path: Path, row: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")


def brain_work_order_enabled() -> bool:
    """Loop auto ON + outbound queue → Brain work-order primary (not Worker INBOX)."""
    cfg = _read(SINA / "loop-specialist-config-v1.json")
    if not cfg.get("loop_auto_dispatch_enabled"):
        return False
    hq = _read(SINA / "healthy-queue-30-active.json")
    phase = str(hq.get("phase") or "")
    product = str(hq.get("product") or "")
    thread = str(hq.get("thread") or "")
    return (
        "outbound-factory" in phase
        or product.startswith("Outbound Factory")
        or thread == "OUTBOUND-FACTORY"
    )


def _upgrade_row(upgrade_id: str) -> dict:
    plan = _read(OUTBOUND_PLAN)
    for u in plan.get("upgrades") or []:
        if str(u.get("id")) == upgrade_id:
            return u
    return {}


def _bay_for_upgrade(upgrade: dict) -> str | None:
    wired = str(upgrade.get("wired_to") or "")
    for key, bay in BAY_BY_WIRED.items():
        if key in wired:
            return bay
    lane = str(upgrade.get("lane") or "")
    if lane in LOCAL_WORKER_LANES:
        return LOCAL_WORKER_LANES[lane]
    if lane == "fdg_icp":
        return LOCAL_WORKER_LANES["fdg_icp"]
    return None


def _is_local_worker_bay(bay_slug: str | None) -> bool:
    return bool(bay_slug and bay_slug.startswith("sourcea-local-"))


def _can_mark_done(*, upgrade: dict, bay: dict) -> bool:
    if not bay.get("ok"):
        return False
    return _bay_for_upgrade(upgrade) is not None


def queue_head() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from queue_ssot_unify_v1 import queue_head as qh  # noqa: WPS433

    return qh()


def sign_work_order(*, head: dict) -> dict:
    upgrade_id = str(head.get("upgrade_id") or head.get("hp_id") or "")
    sa_id = str(head.get("sa_id") or "")
    upgrade = _upgrade_row(upgrade_id)
    bay_slug = _bay_for_upgrade(upgrade) or "unmapped"
    local = _is_local_worker_bay(bay_slug)
    work_order_id = f"wo-brain-{uuid.uuid4().hex[:12]}"
    order = {
        "schema": "brain-outbound-work-order-v1",
        "id": work_order_id,
        "fbe_schema": "fbe-work-order-v1",
        "template_id": "outbound-factory-upgrade-v1",
        "tenant": "wil_ai_design_partner",
        "bay_slug": bay_slug,
        "target_tier": "MARKET_READY",
        "origin": "brain_control_plane",
        "brand": "local-brand",
        "locales": ["en-US"],
        "upgrade_ref": upgrade_id,
        "sa_id": sa_id,
        "queue_pos": head.get("queue_pos"),
        "execution_plane": "sourcea_worker" if local else "cloudflare_worker",
        "control_plane": "mac_hub",
        "owner_role": "brain",
        "wired_to": head.get("sa_path") or f"data/outbound-factory-100-upgrade-plan-v1.json#{upgrade_id}",
        "signed_at": _now(),
        "status": "signed",
        "local_worker": local,
    }

    ledger = _read(ORDERS_PATH)
    if ledger.get("schema") != "fbe-work-orders-ledger-v1":
        ledger = {"schema": "fbe-work-orders-ledger-v1", "orders": []}
    orders = list(ledger.get("orders") or [])
    orders.append({**order, "schema": "fbe-work-order-v1"})
    ledger["orders"] = orders
    ledger["updated_at"] = _now()
    _write(ORDERS_PATH, ledger)

    signed = {"schema": "brain-outbound-work-order-signed-v1", "ok": True, "at": _now(), "work_order": order}
    _write(ROOT / "receipts" / "brain-outbound-work-order-signed-v1.json", signed)
    return signed


def execute_bay(*, upgrade_id: str, work_order_id: str) -> dict:
    sys.path.insert(0, str(SCRIPTS / "fbe"))
    from outbound_fdg_icp_bay_v1 import run_bay  # noqa: WPS433

    bay = run_bay(upgrade_id=upgrade_id, work_order_id=work_order_id)
    sys.path.insert(0, str(SCRIPTS))
    try:
        from fbe_receipt_federate_v1 import federate  # noqa: WPS433

        fed = federate(work_order_id=work_order_id, bay_slug=BAY_SLUG)
        bay["federated"] = fed
    except Exception as exc:
        bay["federated"] = {"ok": False, "error": str(exc)}
    return bay


def _mark_outbound_done(*, upgrade_id: str, sa_id: str, work_order_id: str, bay: dict) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from outbound_receipt_path_v1 import LAW, canonical_receipt_rel  # noqa: WPS433

    plan = _read(OUTBOUND_PLAN)
    touched = False
    receipt_path = canonical_receipt_rel(upgrade_id=upgrade_id, sa_id=sa_id)
    for u in plan.get("upgrades") or []:
        if str(u.get("id")) != upgrade_id:
            continue
        if u.get("status") != "done":
            u["status"] = "done"
            touched = True
        u["worker_status"] = "cloud_done"
        u["shipped_evidence"] = {
            "script": "scripts/brain_outbound_work_order_v1.py",
            "bay": bay.get("bay_slug") or BAY_SLUG,
            "work_order_id": work_order_id,
            "at": _now(),
            "sa_id": sa_id,
            "receipt_path": receipt_path,
            "receipt_law": LAW,
            "execution_plane": "cloudflare_worker",
            "brain_signed": True,
        }
        break
    if touched:
        plan["saved_at"] = _now()
        _write(OUTBOUND_PLAN, plan)
    return {"ok": True, "upgrade_id": upgrade_id, "touched": touched}


def _write_sa_receipt(*, head: dict, work_order_id: str, bay: dict) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from outbound_receipt_path_v1 import write_receipt  # noqa: WPS433

    upgrade_id = str(head.get("upgrade_id") or "")
    sa_id = str(head.get("sa_id") or "sa-XXXX")
    bay_slug = str(bay.get("bay_slug") or work_order_id)
    return write_receipt(
        upgrade_id=upgrade_id,
        sa_id=sa_id,
        title=str(head.get("sa_title") or head.get("title") or ""),
        evidence=(
            f"brain_outbound_work_order · bay={bay_slug} · "
            f"wo={work_order_id} · gate_ok={bay.get('ok')}"
        ),
        extra={
            "engine": "BRAIN_WORK_ORDER",
            "execution_plane": "cloudflare_worker",
            "work_order_id": work_order_id,
            "source": "brain_outbound_work_order_v1",
        },
    )


def _mark_b0503_consumer(*, upgrade_id: str, work_order_id: str) -> dict:
    """B0503 — local fdg_icp consumer reads active work-order (Fly billing interim)."""
    plan = _read(BRAIN_PLAN)
    marked: list[str] = []
    active = _read(ACTIVE_PATH)
    for u in plan.get("upgrades") or []:
        if u.get("id") != "B0503":
            continue
        u["status"] = "done"
        u["brain_proof"] = True
        u["cloud_proof"] = False
        u["local_worker_fallback"] = True
        u["work_order_id"] = work_order_id
        u["consumer_reads"] = str(ACTIVE_PATH)
        u["upgrade_ref"] = upgrade_id
        marked.append("B0503")
    if marked:
        plan["saved_at"] = _now()
        _write(BRAIN_PLAN, plan)
    return {"ok": bool(marked), "marked": marked, "active_wo": bool(active.get("work_order_id"))}


def _mark_brain_plan(*, work_order_id: str) -> dict:
    plan = _read(BRAIN_PLAN)
    marked: list[str] = []
    for u in plan.get("upgrades") or []:
        if u.get("id") not in BRAIN_MARK_IDS:
            continue
        u["status"] = "done"
        u["brain_proof"] = True
        u["cloud_proof"] = True
        u["work_order_id"] = work_order_id
        u["local_worker_deprecated"] = True
        marked.append(u["id"])
    if marked:
        plan["saved_at"] = _now()
        _write(BRAIN_PLAN, plan)
    return {"ok": True, "marked": marked}


def _mark_full_stack_f001() -> dict:
    plan = _read(FULL_STACK_PLAN)
    for f in plan.get("fixes") or []:
        if f.get("id") != "F001":
            continue
        f["status"] = "done"
        f["lane"] = "work_order"
        f["lane_label"] = "Brain work-order dispatch"
        f["owner_role"] = "brain"
        f["wired_to"] = "scripts/brain_outbound_work_order_v1.py"
        f["live_note"] = "B0501 work-order dispatched · INBOX cleared"
        plan["saved_at"] = _now()
        _write(FULL_STACK_PLAN, plan)
        return {"ok": True, "id": "F001"}
    return {"ok": False, "error": "F001 not found"}


def clear_inbox_work_order(*, work_order: dict, bay: dict) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from worker_inject_lib import clear_inbox  # noqa: WPS433

    cleared = clear_inbox(reason="brain_outbound_work_order")
    active = {
        "schema": "brain-outbound-work-order-active-v1",
        "at": _now(),
        "pending": False,
        "execution_mode": "brain_work_order",
        "work_order_id": work_order.get("id"),
        "upgrade_ref": work_order.get("upgrade_ref"),
        "sa_id": work_order.get("sa_id"),
        "bay_slug": work_order.get("bay_slug"),
        "execution_plane": work_order.get("execution_plane"),
        "bay_ok": bool(bay.get("ok")),
        "founder_note": "Loop auto · Brain work-order dispatched · Hub glance only",
        "local_worker_deprecated": True,
    }
    _write(ACTIVE_PATH, active)
    return {"ok": True, "cleared": cleared, "active": active}


def rebuild_queue(*, deliver_next: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from outbound_factory_queue_assign_v1 import (  # noqa: WPS433
        build_assignment,
        deliver_head,
        sync_truth,
        write_queue,
    )

    bundle = build_assignment()
    write_row = write_queue(bundle)
    deliver_row = {"skipped": True}
    if deliver_next and bundle.get("head"):
        deliver_row = deliver_head(bundle)
    sync_row = sync_truth()
    return {"assign": write_row, "deliver": deliver_row, "sync": sync_row}


def dispatch_current(
    *,
    dry_run: bool = False,
    advance_queue: bool = True,
    mode: str = "auto",
) -> dict:
    head_item = queue_head()
    hq = _read(SINA / "healthy-queue-30-active.json")
    queue = hq.get("queue") or []
    head = queue[0] if queue else head_item
    if not head.get("sa_id") and not head_item.get("sa_id"):
        return {"ok": False, "error": "empty_queue"}

    head = {**head_item, **head}
    upgrade_id = str(head.get("upgrade_id") or "")
    sa_id = str(head.get("sa_id") or "")
    upgrade = _upgrade_row(upgrade_id)
    bay_slug = _bay_for_upgrade(upgrade)

    if upgrade.get("status") == "done" and mode in ("auto", "execute_pending"):
        signed = {"skipped": True, "reason": "upgrade_already_done"}
        inbox = clear_inbox_work_order(work_order={"id": "", "upgrade_ref": upgrade_id, "sa_id": sa_id}, bay={"ok": True})
        queue_row = rebuild_queue(deliver_next=False) if advance_queue else {"skipped": True}
        return {
            "ok": True,
            "at": _now(),
            "mode": "stale_inbox_clear",
            "upgrade_id": upgrade_id,
            "inbox": inbox,
            "queue": queue_row,
            "brain_outbound_line": f"brain-outbound · {upgrade_id} · stale INBOX cleared · local_worker=NO",
        }

    signed_row = sign_work_order(head=head)
    work_order = signed_row["work_order"]
    if dry_run:
        return {"ok": True, "dry_run": True, "signed": signed_row, "bay_slug": bay_slug}

    if mode == "sign_only" or not bay_slug or _is_local_worker_bay(bay_slug):
        local = _is_local_worker_bay(bay_slug)
        active = {
            "schema": "brain-outbound-work-order-active-v1",
            "at": _now(),
            "pending": not local,
            "pending_cloud_bay": not local and not bay_slug,
            "execution_mode": "local_worker" if local else "brain_work_order",
            "work_order_id": work_order["id"],
            "upgrade_ref": upgrade_id,
            "sa_id": sa_id,
            "bay_slug": bay_slug or "unmapped",
            "execution_plane": work_order.get("execution_plane"),
            "founder_note": (
                "Loop auto · local Worker RUN INBOX · Hub glance"
                if local
                else "Loop auto · Brain work-order signed · awaiting cloud bay"
            ),
            "local_worker_deprecated": not local,
        }
        _write(ACTIVE_PATH, active)
        dispatch_mode = "local_worker" if local else "sign_only"
        b0503 = {"skipped": True}
        if local and upgrade.get("lane") in ("fdg_icp", "icp4_one_product_line"):
            b0503 = _mark_b0503_consumer(upgrade_id=upgrade_id, work_order_id=work_order["id"])
        return {
            "ok": True,
            "at": _now(),
            "mode": dispatch_mode,
            "signed": signed_row,
            "active": active,
            "b0503": b0503,
            "brain_outbound_line": (
                f"brain-outbound · {upgrade_id} · signed · bay={bay_slug or 'unmapped'} · "
                f"local_worker={'YES' if local else 'NO'}"
            ),
        }

    bay = execute_bay(upgrade_id=upgrade_id, work_order_id=work_order["id"])
    sa_rcpt = _write_sa_receipt(head=head, work_order_id=work_order["id"], bay=bay)
    outbound = {"skipped": True}
    if _can_mark_done(upgrade=upgrade, bay=bay):
        outbound = _mark_outbound_done(
            upgrade_id=upgrade_id, sa_id=sa_id, work_order_id=work_order["id"], bay=bay
        )
    brain_plan = _read(BRAIN_PLAN)
    brain = {"skipped": True}
    if not any(u.get("id") == "B0501" and u.get("status") == "done" for u in brain_plan.get("upgrades") or []):
        brain = _mark_brain_plan(work_order_id=work_order["id"])
    f001 = _mark_full_stack_f001()
    inbox = clear_inbox_work_order(work_order=work_order, bay=bay)

    queue_row: dict[str, Any] = {"skipped": True}
    if advance_queue and outbound.get("touched"):
        queue_row = rebuild_queue(deliver_next=False)

    reasoning = {
        "schema": "brain-outbound-reasoning-receipt-v1",
        "ok": bool(bay.get("ok")),
        "at": _now(),
        "brain_blocker_resolved": "local_worker_inbox_primary",
        "pivot": "brain_signed_work_order_to_cloud",
        "upgrade_id": upgrade_id,
        "sa_id": sa_id,
        "work_order_id": work_order["id"],
        "bay_slug": bay_slug,
        "b0501": True,
        "founder_facing": "Loop auto · Brain work-order · Hub glance only",
    }
    _write(REASONING_RECEIPT, reasoning)

    row = {
        "schema": "brain-outbound-dispatch-receipt-v1",
        "ok": bool(bay.get("ok")),
        "at": _now(),
        "mode": "execute",
        "signed": signed_row,
        "bay": bay,
        "sa_receipt": sa_rcpt,
        "outbound_plan": outbound,
        "brain_plan": brain,
        "full_stack_f001": f001,
        "inbox": inbox,
        "queue": queue_row,
        "reasoning": reasoning,
        "brain_outbound_line": (
            f"brain-outbound · {upgrade_id} · {sa_id} · wo={work_order['id'][:16]} · "
            f"bay={'PASS' if bay.get('ok') else 'FAIL'} · local_worker=NO"
        ),
    }
    _write(SINA / "brain-outbound-dispatch-receipt-v1.json", row)
    return row


def handle_hub_post(body: dict | None = None) -> dict:
    body = body or {}
    dry = bool(body.get("dry_run"))
    return dispatch_current(dry_run=dry, advance_queue=not dry)


def main() -> int:
    ap = argparse.ArgumentParser(description="Brain outbound work-order compiler (B0501)")
    ap.add_argument("command", nargs="?", default="dispatch", choices=("dispatch", "sign", "status"))
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.command == "status":
        row = {
            "ok": True,
            "enabled": brain_work_order_enabled(),
            "active": _read(ACTIVE_PATH),
            "last": _read(SINA / "brain-outbound-dispatch-receipt-v1.json"),
        }
    elif args.command == "sign":
        head = queue_head()
        row = sign_work_order(head=head)
    else:
        row = dispatch_current(dry_run=args.dry_run)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("brain_outbound_line") or row.get("ok"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
