#!/usr/bin/env python3
"""FBE billing webhook stub — purchase/tier gate + receipt (billing-first thin slice).

Does NOT call Apple/Stripe APIs — validates payload shape and records entitlement event.
StoreKit live wire deferred until iOS project named in WORK order.

Law: data/fbe_billing_contract_v1.json · data/architecture-ledger-v1.json
"""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
CONTRACT_PATH = DATA / "fbe_billing_contract_v1.json"
EVENTS_PATH = SINA / "fbe-billing-events-v1.jsonl"
RECEIPT_PATH = SINA / "fbe-billing-webhook-receipt-v1.json"

TIER_ALIASES = {
    "bronze": "BRONZE",
    "gold": "GOLD",
    "gold_plus": "GOLD+assembly_wired",
    "platinum": "PLATINUM",
    "market_ready": "MARKET_READY",
    "BRONZE": "BRONZE",
    "GOLD": "GOLD",
    "GOLD+assembly_wired": "GOLD+assembly_wired",
    "PLATINUM": "PLATINUM",
    "MARKET_READY": "MARKET_READY",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def validate_purchase_payload(payload: dict) -> dict:
    required = ("event", "tenant", "tier")
    missing = [k for k in required if not payload.get(k)]
    if missing:
        raise ValueError(f"missing fields: {missing}")
    tier_raw = str(payload["tier"])
    tier = TIER_ALIASES.get(tier_raw) or TIER_ALIASES.get(tier_raw.lower())
    if not tier:
        raise ValueError(f"unknown tier: {tier_raw}")
    return {
        "event": str(payload["event"]),
        "tenant": str(payload["tenant"]),
        "tier": tier,
        "transaction_id": payload.get("transaction_id") or payload.get("storekit_original_transaction_id"),
        "credits_delta": int(payload.get("credits_delta") or 0),
        "source": str(payload.get("source") or "webhook_stub"),
    }


def record_purchase(payload: dict) -> dict:
    contract = _read_json(CONTRACT_PATH)
    bands = contract.get("bands") or {}
    normalized = validate_purchase_payload(payload)
    band = bands.get(normalized["tier"]) or bands.get("BRONZE") or {}
    unit_usd = int(band.get("unit_usd") or 0)

    event = {
        "schema": "fbe-billing-event-v1",
        "at": _now(),
        "event": normalized["event"],
        "tenant": normalized["tenant"],
        "tier_achieved": normalized["tier"],
        "unit_usd": unit_usd,
        "transaction_id": normalized.get("transaction_id"),
        "credits_delta": normalized["credits_delta"],
        "source": normalized["source"],
        "webhook_stub": True,
    }

    SINA.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, separators=(",", ":")) + "\n")

    receipt = {
        "schema": "fbe-billing-webhook-receipt-v1",
        "ok": True,
        "at": _now(),
        "verdict": "PASS",
        "tier_gate": normalized["tier"],
        "unit_usd": unit_usd,
        "shippable": band.get("shippable"),
        "event": event,
        "honest_label": "stub only — no Apple/Stripe API call",
        "next": "Wire StoreKit when apps/apple-store-api WORK order lands",
    }
    RECEIPT_PATH.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="FBE billing webhook stub v1")
    ap.add_argument("--payload", help="JSON string or @file path")
    ap.add_argument("--demo", action="store_true", help="Record demo GOLD purchase")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    if args.demo:
        payload = {
            "event": "purchase",
            "tenant": "demo-tenant",
            "tier": "GOLD",
            "transaction_id": "demo-txn-001",
            "credits_delta": 100,
            "source": "demo",
        }
    elif args.payload:
        raw = args.payload.strip()
        if raw.startswith("@"):
            payload = json.loads(Path(raw[1:]).read_text(encoding="utf-8"))
        else:
            payload = json.loads(raw)
    else:
        print("Usage: --demo or --payload '{...}' or --payload @path.json")
        return 2

    try:
        row = record_purchase(payload)
    except Exception as exc:
        row = {"ok": False, "verdict": "FAIL", "error": str(exc), "at": _now()}
        if args.json:
            print(json.dumps(row, indent=2))
        return 1

    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"OK: tier_gate={row.get('tier_gate')} · unit_usd={row.get('unit_usd')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
