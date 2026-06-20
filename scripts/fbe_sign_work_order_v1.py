#!/usr/bin/env python3
"""FBE work order sign — fbe-work-order-v1 schema."""
from __future__ import annotations

import argparse
import json
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
ORDERS_PATH = SINA / "fbe-work-orders-v1.json"
SIGNED_PATH = ROOT / "receipts" / "work-order-signed-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def sign(
    *,
    template_id: str = "web-product-factory-v1",
    tenant: str = "wil_ai_design_partner",
    bay_slug: str = "sample-bay",
    target_tier: str = "GOLD",
    origin: str = "mac_control_plane",
    brand: str = "local-brand",
    locales: list[str] | None = None,
) -> dict:
    locales = locales or ["en-US"]
    work_order_id = f"wo-{uuid.uuid4().hex[:12]}"
    order = {
        "schema": "fbe-work-order-v1",
        "id": work_order_id,
        "template_id": template_id,
        "tenant": tenant,
        "bay_slug": bay_slug,
        "target_tier": target_tier,
        "origin": origin,
        "brand": brand,
        "locales": locales,
        "signed_at": _now(),
        "status": "signed",
        "execution_plane": "cloud_skeleton",
    }

    ledger = _read_json(ORDERS_PATH)
    if ledger.get("schema") != "fbe-work-orders-ledger-v1":
        ledger = {"schema": "fbe-work-orders-ledger-v1", "orders": []}
    orders = list(ledger.get("orders") or [])
    orders.append(order)
    ledger["orders"] = orders
    ledger["updated_at"] = _now()

    signed = {
        "schema": "fbe-work-order-signed-v1",
        "ok": True,
        "at": _now(),
        "work_order": order,
    }

    SINA.mkdir(parents=True, exist_ok=True)
    ORDERS_PATH.write_text(json.dumps(ledger, indent=2) + "\n", encoding="utf-8")
    SIGNED_PATH.parent.mkdir(parents=True, exist_ok=True)
    SIGNED_PATH.write_text(json.dumps(signed, indent=2) + "\n", encoding="utf-8")
    return signed


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--template-id", default="web-product-factory-v1")
    ap.add_argument("--tenant", default="wil_ai_design_partner")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = sign(template_id=args.template_id, tenant=args.tenant)
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
