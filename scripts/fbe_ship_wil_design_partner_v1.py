#!/usr/bin/env python3
"""One-shot Wil AI design-partner ship — Factory 1 sample-bay."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.motor_ensure_v1 import ensure_motor  # noqa: E402
from fbe_run_job_v1 import run_job  # noqa: E402
from fbe_design_partner_receipt_v1 import build_partner_pack  # noqa: E402

TENANT = "wil_ai_design_partner"
BAY = "sample-bay"
TEMPLATE = "web-product-factory-v1"
PACK_PATH = ROOT / "receipts" / "partners" / TENANT / "design-partner-receipt-v1.zip"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def ship() -> dict:
    motor = ensure_motor(wave="W3", bay_slug=BAY, factory_id="factory_1")

    job = run_job(bay_slug=BAY, template_id=TEMPLATE, tenant=TENANT)
    if not job.get("ok"):
        return {"ok": False, "error": "run_job FAIL", "job": job}

    partner = build_partner_pack(tenant=TENANT, bay_slug=BAY)
    ok = bool(partner.get("ok")) and PACK_PATH.is_file()
    row = {
        "schema": "fbe-wil-design-partner-ship-v1",
        "ok": ok,
        "at": _now(),
        "tenant": TENANT,
        "bay_slug": BAY,
        "template_id": TEMPLATE,
        "tier_achieved": job.get("tier_achieved"),
        "partner_pack_uri": partner.get("receipt_pack_uri"),
        "motor_proof": motor.get("proof"),
        "job_ok": job.get("ok"),
        "deliveryMode": "prove_only",
    }
    receipt_path = ROOT / "receipts" / "partners" / TENANT / "ship-receipt-v1.json"
    receipt_path.parent.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    SINA.mkdir(parents=True, exist_ok=True)
    (SINA / "fbe-wil-design-partner-ship-receipt-v1.json").write_text(
        json.dumps(row, indent=2) + "\n", encoding="utf-8"
    )
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = ship()
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
