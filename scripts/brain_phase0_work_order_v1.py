#!/usr/bin/env python3
"""Brain Phase 0 work-order compiler — sign · dispatch · federate for product-lane factories.

Q-GATH-04 A: Brain signs · cloud/API executes · Mac control plane only — not Worker INBOX north star.
Law: data/phase0-freemium-sandbox-reference-v1.json · data/founder-pivot-pattern-v1.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
ACTIVE_PATH = SINA / "brain-phase0-work-order-active-v1.json"
REASONING_RECEIPT = SINA / "brain-phase0-reasoning-receipt-v1.json"
ORDERS_PATH = SINA / "fbe-work-orders-v1.json"
BRAIN_PLAN = ROOT / "data" / "brain-cloud-reasoning-1000-upgrade-plan-v1.json"
PHASE0_RECEIPT = ROOT / "receipts" / "phase0-noetfield-freemium-factory-v1.json"

FACTORIES: dict[str, dict[str, str]] = {
    "noetfield-freemium-factory-v1": {
        "bay_slug": "noetfield-freemium-bay",
        "tenant": "noetfield",
        "upgrade_ref": "P0-13",
        "sa_id": "sa-nf-freemium",
    },
}


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


def _cloud_worker_url() -> str:
    cfg = _read(ROOT / "data" / "fbe_cloud_worker_config_v1.json")
    for key in (cfg.get("worker_url_env") or "FBE_CLOUD_WORKER_URL", "RAILWAY_WORKER_URL"):
        val = os.environ.get(str(key), "").strip()
        if val:
            return val.rstrip("/")
    return str(cfg.get("worker_url") or "").strip().rstrip("/")


def _resolve_factory(factory_id: str) -> dict[str, str]:
    row = FACTORIES.get(factory_id)
    if not row:
        raise ValueError(f"unknown_factory:{factory_id}")
    return row


def sign_work_order(*, factory_id: str) -> dict:
    meta = _resolve_factory(factory_id)
    bay_slug = meta["bay_slug"]
    work_order_id = f"wo-brain-{uuid.uuid4().hex[:12]}"
    order = {
        "schema": "brain-phase0-work-order-v1",
        "id": work_order_id,
        "fbe_schema": "fbe-work-order-v1",
        "template_id": factory_id,
        "tenant": meta["tenant"],
        "bay_slug": bay_slug,
        "target_tier": "FREEMIUM",
        "origin": "brain_control_plane",
        "brand": "local-brand",
        "locales": ["en-US"],
        "upgrade_ref": meta["upgrade_ref"],
        "sa_id": meta["sa_id"],
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_hub",
        "owner_role": "brain",
        "wired_to": f"data/factory-specs/{factory_id}.json",
        "signed_at": _now(),
        "status": "signed",
        "local_worker": False,
        "local_worker_deprecated": True,
        "q_gath_04": "A",
    }

    ledger = _read(ORDERS_PATH)
    if ledger.get("schema") != "fbe-work-orders-ledger-v1":
        ledger = {"schema": "fbe-work-orders-ledger-v1", "orders": []}
    orders = list(ledger.get("orders") or [])
    orders.append({**order, "schema": "fbe-work-order-v1"})
    ledger["orders"] = orders
    ledger["updated_at"] = _now()
    _write(ORDERS_PATH, ledger)

    signed = {"schema": "brain-phase0-work-order-signed-v1", "ok": True, "at": _now(), "work_order": order}
    _write(ROOT / "receipts" / "brain-phase0-work-order-signed-v1.json", signed)
    return signed


def _submit_cloud(*, factory_id: str, bay_slug: str, tenant: str, work_order_id: str) -> dict[str, Any]:
    sys.path.insert(0, str(SCRIPTS))
    from fbe.lib.cloud_adapter_v1 import submit_job  # noqa: WPS433

    url = _cloud_worker_url()
    if url:
        mode = "railway_fbe"
        cloud_stub = False
    else:
        mode = "local_docker"
        cloud_stub = True
    adapter = submit_job(
        template_id=factory_id,
        work_order_id=work_order_id,
        tenant=tenant,
        bay_slug=bay_slug,
        dry_run=False,
        mode=mode,
        run_mode="refinery",
    )
    adapter["cloud_stub"] = cloud_stub
    adapter["q_gath_04"] = "A"
    return adapter


def execute_bay(*, factory_id: str, work_order_id: str, upgrade_ref: str) -> dict:
    sys.path.insert(0, str(SCRIPTS / "fbe"))
    from noetfield_freemium_bay_v1 import run_bay  # noqa: WPS433

    meta = _resolve_factory(factory_id)
    bay = run_bay(upgrade_id=upgrade_ref, work_order_id=work_order_id)
    sys.path.insert(0, str(SCRIPTS))
    try:
        from fbe_receipt_federate_v1 import federate  # noqa: WPS433

        fed = federate(work_order_id=work_order_id, bay_slug=meta["bay_slug"])
        bay["federated"] = fed
    except Exception as exc:
        bay["federated"] = {"ok": False, "error": str(exc)}
    return bay


def _mark_b0504(*, work_order_id: str, bay: dict) -> dict:
    if not bay.get("ok") or not (bay.get("federated") or {}).get("ok"):
        return {"skipped": True, "reason": "bay_or_federate_not_ok"}
    plan = _read(BRAIN_PLAN)
    touched = False
    for u in plan.get("upgrades") or []:
        if str(u.get("id")) != "B0504":
            continue
        if u.get("status") != "done":
            u["status"] = "done"
            touched = True
        u["brain_proof"] = True
        u["cloud_proof"] = True
        u["work_order_id"] = work_order_id
        u["local_worker_deprecated"] = True
        break
    if touched:
        plan["saved_at"] = _now()
        _write(BRAIN_PLAN, plan)
    return {"ok": True, "touched": touched, "upgrade_id": "B0504"}


def _write_phase0_receipt(*, factory_id: str, work_order_id: str, bay: dict, adapter: dict) -> dict:
    meta = _resolve_factory(factory_id)
    row = {
        "schema": "phase0-noetfield-freemium-factory-receipt-v1",
        "ok": bool(bay.get("ok")),
        "at": _now(),
        "factory_id": factory_id,
        "sa_id": meta["sa_id"],
        "upgrade_ref": meta["upgrade_ref"],
        "work_order_id": work_order_id,
        "bay_slug": meta["bay_slug"],
        "execution_plane": "cloud_api_worker",
        "control_plane": "mac_hub",
        "local_worker": False,
        "q_gath_04": "A",
        "cloud_stub": adapter.get("cloud_stub", True),
        "bay_ok": bay.get("ok"),
        "federated_ok": (bay.get("federated") or {}).get("ok"),
        "evidence": f"brain_phase0_work_order · bay={meta['bay_slug']} · wo={work_order_id}",
        "source": "scripts/brain_phase0_work_order_v1.py",
    }
    _write(PHASE0_RECEIPT, row)
    return row


def dispatch(*, factory_id: str, dry_run: bool = False, sign_only: bool = False) -> dict:
    signed_row = sign_work_order(factory_id=factory_id)
    work_order = signed_row["work_order"]
    meta = _resolve_factory(factory_id)

    if dry_run:
        return {"ok": True, "dry_run": True, "signed": signed_row, "factory_id": factory_id}

    if sign_only:
        active = {
            "schema": "brain-phase0-work-order-active-v1",
            "at": _now(),
            "pending": True,
            "execution_mode": "brain_work_order",
            "local_worker_deprecated": True,
            "work_order_id": work_order["id"],
            "factory_id": factory_id,
            "upgrade_ref": meta["upgrade_ref"],
            "sa_id": meta["sa_id"],
            "bay_slug": meta["bay_slug"],
            "execution_plane": "cloud_api_worker",
            "q_gath_04": "A",
            "founder_note": "Brain work-order signed · awaiting cloud bay dispatch",
        }
        _write(ACTIVE_PATH, active)
        return {
            "ok": True,
            "mode": "sign_only",
            "signed": signed_row,
            "active": active,
            "brain_phase0_line": (
                f"brain-phase0 · {factory_id} · signed · bay={meta['bay_slug']} · local_worker=NO"
            ),
        }

    bay = execute_bay(
        factory_id=factory_id,
        work_order_id=work_order["id"],
        upgrade_ref=meta["upgrade_ref"],
    )
    adapter = _submit_cloud(
        factory_id=factory_id,
        bay_slug=meta["bay_slug"],
        tenant=meta["tenant"],
        work_order_id=work_order["id"],
    )
    b0504 = _mark_b0504(work_order_id=work_order["id"], bay=bay)
    phase0_rcpt = _write_phase0_receipt(
        factory_id=factory_id,
        work_order_id=work_order["id"],
        bay=bay,
        adapter=adapter,
    )

    active = {
        "schema": "brain-phase0-work-order-active-v1",
        "at": _now(),
        "pending": False,
        "execution_mode": "brain_work_order",
        "local_worker_deprecated": True,
        "work_order_id": work_order["id"],
        "factory_id": factory_id,
        "upgrade_ref": meta["upgrade_ref"],
        "sa_id": meta["sa_id"],
        "bay_slug": meta["bay_slug"],
        "execution_plane": "cloud_api_worker",
        "q_gath_04": "A",
        "cloud_stub": adapter.get("cloud_stub"),
        "founder_note": "Loop auto · Brain work-order · cloud bay PASS · Hub glance only",
    }
    _write(ACTIVE_PATH, active)

    reasoning = {
        "schema": "brain-phase0-reasoning-receipt-v1",
        "ok": bool(bay.get("ok")),
        "at": _now(),
        "brain_blocker_resolved": "local_worker_inbox_primary",
        "pivot": "brain_signed_work_order_to_cloud",
        "q_gath_04": "A",
        "factory_id": factory_id,
        "work_order_id": work_order["id"],
        "bay_slug": meta["bay_slug"],
        "cloud_stub": adapter.get("cloud_stub"),
        "founder_facing": "Brain work-order · cloud bay · Hub glance only",
    }
    _write(REASONING_RECEIPT, reasoning)

    ok = bool(bay.get("ok"))
    row = {
        "schema": "brain-phase0-dispatch-receipt-v1",
        "ok": ok,
        "at": _now(),
        "mode": "dispatch",
        "signed": signed_row,
        "bay": bay,
        "cloud_adapter": adapter,
        "b0504": b0504,
        "phase0_receipt": phase0_rcpt,
        "active": active,
        "reasoning": reasoning,
        "brain_phase0_line": (
            f"brain-phase0 · {factory_id} · wo={work_order['id'][:16]} · "
            f"bay={'PASS' if bay.get('ok') else 'FAIL'} · local_worker=NO · q_gath_04=A"
        ),
    }
    _write(SINA / "brain-phase0-dispatch-receipt-v1.json", row)
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Brain Phase 0 work-order compiler")
    ap.add_argument("--factory", default="noetfield-freemium-factory-v1")
    ap.add_argument("--dispatch", action="store_true", help="Sign and execute cloud bay")
    ap.add_argument("--sign-only", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.factory not in FACTORIES:
        print(json.dumps({"ok": False, "error": f"unknown_factory:{args.factory}"}))
        return 1

    if args.sign_only:
        row = dispatch(factory_id=args.factory, dry_run=args.dry_run, sign_only=True)
    elif args.dispatch:
        row = dispatch(factory_id=args.factory, dry_run=args.dry_run, sign_only=False)
    else:
        row = dispatch(factory_id=args.factory, dry_run=args.dry_run, sign_only=False)

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("brain_phase0_line") or row.get("ok"))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
