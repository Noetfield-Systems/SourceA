#!/usr/bin/env python3
"""FBE spawn W1 — sign work order · cloud adapter skeleton · registry."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
REGISTRY_PATH = SINA / "fbe-factory-registry-v1.json"
COMPILE_RECEIPT = SINA / "fbe-compile-receipt-v1.json"
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.cloud_adapter_v1 import submit_job  # noqa: E402
from fbe_sign_work_order_v1 import sign  # noqa: E402
from fbe_motor_delegate_v1 import delegate  # noqa: E402
from fbe_receipt_federate_v1 import federate  # noqa: E402
from fbe_verify_motor_v1 import verify  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _delegate_fresh(max_age_sec: int = 300) -> bool:
    p = SINA / "fbe-motor-delegate-receipt-v1.json"
    if not p.is_file():
        return False
    try:
        row = json.loads(p.read_text(encoding="utf-8"))
        if not row.get("ok"):
            return False
        at = str(row.get("at") or "")
        if not at.endswith("Z"):
            return False
        from datetime import datetime, timezone

        ts = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - ts).total_seconds()
        return age <= max_age_sec
    except (OSError, json.JSONDecodeError, ValueError):
        return False


def mark_w3_ready(*, template_id: str = "web-product-factory-v1") -> dict:
    registry = _read_json(REGISTRY_PATH)
    if registry.get("schema") != "fbe-factory-registry-v1":
        registry = {"schema": "fbe-factory-registry-v1", "instances": []}
    instances = list(registry.get("instances") or [])
    job = _read_json(SINA / "fbe-run-job-receipt-v1.json")
    for inst in instances:
        if inst.get("template_id") == template_id:
            inst["w3_market_ready_candidate"] = bool(job.get("ok"))
            inst["status"] = "w3_market_ready_candidate" if job.get("ok") else inst.get("status")
            inst["tier_achieved"] = job.get("tier_achieved")
            inst["execution_plane"] = job.get("execution_plane")
    registry["instances"] = instances
    registry["updated_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return {"ok": bool(job.get("ok")), "template_id": template_id, "tier_achieved": job.get("tier_achieved")}


def mark_w4_ready(*, template_id: str = "exchange-factory-v1") -> dict:
    registry = _read_json(REGISTRY_PATH)
    if registry.get("schema") != "fbe-factory-registry-v1":
        registry = {"schema": "fbe-factory-registry-v1", "instances": []}
    instances = list(registry.get("instances") or [])
    job = _read_json(SINA / "fbe-run-job-receipt-v1.json")
    for inst in instances:
        if inst.get("template_id") == template_id:
            inst["w4_exchange_ready"] = bool(job.get("ok"))
            inst["status"] = "w4_exchange_ready" if job.get("ok") else inst.get("status")
            inst["tier_achieved"] = job.get("tier_achieved")
            inst["execution_plane"] = job.get("execution_plane")
            inst["factory_id"] = "factory_2"
    if not any(i.get("template_id") == template_id for i in instances):
        instances.append({
            "template_id": template_id,
            "status": "w4_exchange_ready" if job.get("ok") else "w1_adapter_ready",
            "w4_exchange_ready": bool(job.get("ok")),
            "tier_achieved": job.get("tier_achieved"),
            "execution_plane": job.get("execution_plane"),
            "factory_id": "factory_2",
            "lines": ["trust_motor", "refinery", "assembly"],
        })
    registry["instances"] = instances
    registry["updated_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return {"ok": bool(job.get("ok")), "template_id": template_id, "tier_achieved": job.get("tier_achieved")}


def mark_w5_ready(*, template_id: str = "forge-app-factory-v1") -> dict:
    registry = _read_json(REGISTRY_PATH)
    if registry.get("schema") != "fbe-factory-registry-v1":
        registry = {"schema": "fbe-factory-registry-v1", "instances": []}
    instances = list(registry.get("instances") or [])
    job = _read_json(SINA / "fbe-run-job-receipt-v1.json")
    for inst in instances:
        if inst.get("template_id") == template_id:
            inst["w5_forge_ready"] = bool(job.get("ok"))
            inst["status"] = "w5_forge_ready" if job.get("ok") else inst.get("status")
            inst["tier_achieved"] = job.get("tier_achieved")
            inst["execution_plane"] = job.get("execution_plane")
            inst["factory_id"] = "factory_3"
    if not any(i.get("template_id") == template_id for i in instances):
        instances.append({
            "template_id": template_id,
            "status": "w5_forge_ready" if job.get("ok") else "w1_adapter_ready",
            "w5_forge_ready": bool(job.get("ok")),
            "tier_achieved": job.get("tier_achieved"),
            "execution_plane": job.get("execution_plane"),
            "factory_id": "factory_3",
            "lines": ["trust_motor", "refinery", "assembly"],
        })
    registry["instances"] = instances
    registry["updated_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return {"ok": bool(job.get("ok")), "template_id": template_id, "tier_achieved": job.get("tier_achieved")}


def mark_w6_ready() -> dict:
    registry = _read_json(REGISTRY_PATH)
    if registry.get("schema") != "fbe-factory-registry-v1":
        registry = {"schema": "fbe-factory-registry-v1", "instances": []}
    fleet = _read_json(SINA / "fbe-fleet-run-receipt-v1.json")
    registry["w6_fleet_ready"] = bool(fleet.get("ok"))
    registry["fleet_id"] = "fleet_3"
    registry["fleet_factories"] = fleet.get("factories")
    registry["updated_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")
    return {"ok": bool(fleet.get("ok")), "fleet_id": "fleet_3"}


def spawn(*, template_id: str = "web-product-factory-v1", tenant: str = "") -> dict:
    if not tenant:
        if template_id == "exchange-factory-v1":
            tenant = "trustfield"
        elif template_id == "forge-app-factory-v1":
            tenant = "forge"
        else:
            tenant = "wil_ai_design_partner"
    compile_r = _read_json(COMPILE_RECEIPT)
    if not compile_r.get("ok"):
        return {"ok": False, "error": "compile receipt not PASS"}

    signed = sign(template_id=template_id, tenant=tenant)
    work_order = signed.get("work_order") or {}
    work_order_id = str(work_order.get("id") or "")

    if not _delegate_fresh():
        delegate(skip_federate=True, fbe_prove=True)
    adapter = submit_job(template_id=template_id, work_order_id=work_order_id, tenant=tenant, dry_run=True)
    federate(work_order_id=work_order_id)
    motor_verify = verify()

    registry = _read_json(REGISTRY_PATH)
    if registry.get("schema") != "fbe-factory-registry-v1":
        registry = {"schema": "fbe-factory-registry-v1", "instances": []}

    instances = list(registry.get("instances") or [])
    row = {
        "template_id": template_id,
        "status": (
            "w5_forge_ready" if template_id == "forge-app-factory-v1"
            else "w4_exchange_ready" if template_id == "exchange-factory-v1"
            else "w1_adapter_ready"
        ),
        "lines": ["trust_motor", "refinery", "assembly"],
        "spawned_at": _now(),
        "work_order_id": work_order_id,
        "execution_plane": "cloud_skeleton",
        "motor_verify_ok": motor_verify.get("ok"),
        "factory_id": (
            "factory_3" if template_id == "forge-app-factory-v1"
            else "factory_2" if template_id == "exchange-factory-v1"
            else "factory_1"
        ),
    }
    existing = next((i for i in instances if i.get("template_id") == template_id), None)
    if existing:
        existing.update(row)
    else:
        instances.append(row)
    registry["instances"] = instances
    registry["updated_at"] = _now()
    SINA.mkdir(parents=True, exist_ok=True)
    REGISTRY_PATH.write_text(json.dumps(registry, indent=2) + "\n", encoding="utf-8")

    job_r = _read_json(SINA / "fbe-run-job-receipt-v1.json")
    if job_r.get("ok"):
        if template_id == "exchange-factory-v1":
            mark_w4_ready(template_id=template_id)
        elif template_id == "forge-app-factory-v1":
            mark_w5_ready(template_id=template_id)
        else:
            mark_w3_ready(template_id=template_id)

    status = (
        "w5_forge_ready" if template_id == "forge-app-factory-v1"
        else "w4_exchange_ready" if template_id == "exchange-factory-v1"
        else "w1_adapter_ready"
    )
    ok = bool(adapter.get("ok")) and bool(motor_verify.get("ok"))
    return {
        "ok": ok,
        "schema": "fbe-spawn-receipt-v1",
        "at": _now(),
        "template_id": template_id,
        "status": status,
        "work_order_id": work_order_id,
        "execution_plane": "cloud_skeleton",
        "motor_verify": motor_verify.get("proof"),
        "adapter_mode": adapter.get("mode"),
        "w1_note": "Signed work order + adapter skeleton — headless execution W2",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template-id", default="web-product-factory-v1")
    ap.add_argument("--tenant", default="wil_ai_design_partner")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = spawn(template_id=args.template_id, tenant=args.tenant)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
