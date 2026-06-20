#!/usr/bin/env python3
"""FBE fleet orchestrator — W6 three-factory run + partner packs."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "fbe-fleet-run-receipt-v1.json"
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.motor_ensure_v1 import ensure_motor  # noqa: E402
from fbe_assembly_runner_v1 import run_bay as run_assembly_planned  # noqa: E402
from fbe_run_job_v1 import run_job  # noqa: E402
from fbe_design_partner_receipt_v1 import build_partner_pack  # noqa: E402
from fbe_receipt_federate_v1 import federate  # noqa: E402
from fbe_billing_meter_v1 import record_fleet_run  # noqa: E402
from fbe_spawn_factory_v1 import mark_w6_ready  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def run_fleet() -> dict:
    motor = ensure_motor(wave="W2", bay_slug="sample-bay", factory_id="factory_1")
    if not motor.get("ok"):
        return {"ok": False, "error": "motor_verify FAIL", "motor": motor}

    planned = run_assembly_planned(
        bay_slug="sample-bay",
        tenant="wil_ai_design_partner",
        pipeline_id="assembly_planned_w6",
    )

    factories = [
        ("factory_1", "web-product-factory-v1", "sample-bay", "wil_ai_design_partner"),
        ("factory_2", "exchange-factory-v1", "trustfield-bay", "trustfield"),
        ("factory_3", "forge-app-factory-v1", "forge-bay", "forge"),
    ]
    results: list[dict] = []
    all_ok = bool(planned.get("ok"))

    for factory_id, template_id, bay, tenant in factories:
        ensure_motor(wave="W2", bay_slug=bay, factory_id=factory_id)
        job = run_job(bay_slug=bay, template_id=template_id, tenant=tenant)
        results.append({
            "factory_id": factory_id,
            "template_id": template_id,
            "bay_slug": bay,
            "tenant": tenant,
            "ok": bool(job.get("ok")),
            "tier_achieved": job.get("tier_achieved"),
        })
        if not job.get("ok"):
            all_ok = False

    wil_pack = build_partner_pack(tenant="wil_ai_design_partner", bay_slug="sample-bay")
    tf_pack = build_partner_pack(tenant="trustfield", bay_slug="trustfield-bay")

    row = {
        "schema": "fbe-fleet-run-receipt-v1",
        "ok": all_ok,
        "at": _now(),
        "wave": "W6",
        "fleet_id": "fleet_3",
        "execution_plane": "headless_w6_fleet",
        "deliveryMode": "prove_only",
        "planned_pipeline_ok": planned.get("ok"),
        "factories": results,
        "partner_packs": {
            "wil_ai_design_partner": wil_pack.get("receipt_pack_uri"),
            "trustfield": tf_pack.get("receipt_pack_uri"),
        },
        "federated_ok": False,
    }
    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")

    fed = federate(work_order_id="wo-fleet-w6", bay_slug="sample-bay", wave="W6", factory_id="fleet_3")
    row["federated_ok"] = fed.get("ok")
    row["ok"] = all_ok and bool(fed.get("ok"))
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    record_fleet_run(fleet_receipt=row)
    if row.get("ok"):
        mark_w6_ready()
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_fleet()
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
