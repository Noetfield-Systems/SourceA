#!/usr/bin/env python3
"""FBE run bay — headless refinery + verify + federate + mono bridge."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.cloud_adapter_v1 import submit_job  # noqa: E402
from fbe_verify_refinery_v1 import verify  # noqa: E402
from fbe_receipt_federate_v1 import federate  # noqa: E402
from fbe_mono_bridge_v1 import mirror_bay  # noqa: E402
from fbe_cloud_sync_v1 import pull_bay_receipts  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def run_bay_job(
    *,
    bay_slug: str = "sample-bay",
    template_id: str = "web-product-factory-v1",
    tenant: str = "wil_ai_design_partner",
    work_order_id: str = "",
) -> dict:
    woid = work_order_id or f"wo-{bay_slug}"
    adapter = submit_job(
        template_id=template_id,
        work_order_id=woid,
        tenant=tenant,
        bay_slug=bay_slug,
        dry_run=False,
        mode="local_docker",
    )
    refinery_verify = verify(bay_slug=bay_slug)
    mirror = mirror_bay(bay_slug=bay_slug, template_id=template_id)
    sync = pull_bay_receipts(bay_slug=bay_slug)
    fed = federate(work_order_id=woid, bay_slug=bay_slug)
    ok = bool(adapter.get("ok")) and bool(refinery_verify.get("ok"))
    return {
        "ok": ok,
        "schema": "fbe-run-bay-receipt-v1",
        "at": _now(),
        "bay_slug": bay_slug,
        "template_id": template_id,
        "execution_plane": "headless_w2",
        "adapter_ok": adapter.get("ok"),
        "refinery_verify": refinery_verify.get("proof"),
        "mono_bridge": mirror.get("farm_status"),
        "federated_ok": fed.get("ok"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="sample-bay")
    ap.add_argument("--template-id", default="web-product-factory-v1")
    ap.add_argument("--tenant", default="wil_ai_design_partner")
    ap.add_argument("--work-order-id", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = run_bay_job(
        bay_slug=args.bay,
        template_id=args.template_id,
        tenant=args.tenant,
        work_order_id=args.work_order_id,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
