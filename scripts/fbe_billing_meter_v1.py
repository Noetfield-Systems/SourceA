#!/usr/bin/env python3
"""FBE billing meter — outcome-band metering for run jobs."""
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
DATA = ROOT / "data"
CONTRACT_PATH = DATA / "fbe_billing_contract_v1.json"
RECEIPT_PATH = SINA / "fbe-billing-meter-receipt-v1.json"
EVENTS_PATH = SINA / "fbe-billing-events-v1.jsonl"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def record_run_job(*, job_receipt: dict) -> dict:
    contract = _read_json(CONTRACT_PATH)
    bands = contract.get("bands") or {}
    tier = str(job_receipt.get("tier_achieved") or "BRONZE")
    band = bands.get(tier) or bands.get("BRONZE") or {}
    unit_usd = band.get("unit_usd", 0)

    lines = job_receipt.get("lines") or {}
    event = {
        "schema": "fbe-billing-event-v1",
        "at": _now(),
        "event": "run_job",
        "template_id": job_receipt.get("template_id"),
        "tenant": job_receipt.get("tenant"),
        "bay_slug": job_receipt.get("bay_slug"),
        "wave": job_receipt.get("wave"),
        "tier_achieved": tier,
        "unit_usd": unit_usd,
        "lines_ok": {
            "motor": (lines.get("motor") or {}).get("ok"),
            "refinery": (lines.get("refinery") or {}).get("ok"),
            "assembly": (lines.get("assembly") or {}).get("ok"),
        },
        "factory_id": job_receipt.get("factory_id") or (
            "factory_3" if job_receipt.get("template_id") == "forge-app-factory-v1"
            else "factory_2" if job_receipt.get("template_id") == "exchange-factory-v1"
            else "factory_1"
        ),
    }

    SINA.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, separators=(",", ":")) + "\n")

    events = []
    if EVENTS_PATH.is_file():
        events = [json.loads(ln) for ln in EVENTS_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]

    total_usd = sum(int(e.get("unit_usd") or 0) for e in events)
    row = {
        "schema": "fbe-billing-meter-receipt-v1",
        "ok": True,
        "at": _now(),
        "model": contract.get("model") or "outcome_band",
        "event_count": len(events),
        "last_event": event,
        "total_usd": total_usd,
        "events_tail": events[-5:],
    }
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def record_fleet_run(*, fleet_receipt: dict) -> dict:
    contract = _read_json(CONTRACT_PATH)
    bands = contract.get("bands") or {}
    total_unit = 0
    factory_events = []
    for f in fleet_receipt.get("factories") or []:
        tier = str(f.get("tier_achieved") or "BRONZE")
        band = bands.get(tier) or bands.get("BRONZE") or {}
        unit_usd = int(band.get("unit_usd") or 0)
        total_unit += unit_usd
        factory_events.append({
            "factory_id": f.get("factory_id"),
            "template_id": f.get("template_id"),
            "tier_achieved": tier,
            "unit_usd": unit_usd,
        })

    event = {
        "schema": "fbe-billing-event-v1",
        "at": _now(),
        "event": "fleet_run",
        "wave": "W6",
        "fleet_id": fleet_receipt.get("fleet_id") or "fleet_3",
        "factory_count": len(factory_events),
        "factories": factory_events,
        "unit_usd": total_unit,
        "fleet_ok": fleet_receipt.get("ok"),
    }

    SINA.mkdir(parents=True, exist_ok=True)
    with EVENTS_PATH.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(event, separators=(",", ":")) + "\n")

    events = []
    if EVENTS_PATH.is_file():
        events = [json.loads(ln) for ln in EVENTS_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]

    total_usd = sum(int(e.get("unit_usd") or 0) for e in events)
    row = {
        "schema": "fbe-billing-meter-receipt-v1",
        "ok": True,
        "at": _now(),
        "model": contract.get("model") or "outcome_band",
        "event_count": len(events),
        "last_event": event,
        "total_usd": total_usd,
        "events_tail": events[-5:],
        "fleet_total_usd": total_unit,
    }
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def status_payload() -> dict:
    receipt = _read_json(RECEIPT_PATH)
    events = []
    if EVENTS_PATH.is_file():
        events = [json.loads(ln) for ln in EVENTS_PATH.read_text(encoding="utf-8").splitlines() if ln.strip()]
    return {
        "ok": bool(receipt.get("ok")),
        "schema": "fbe-billing-status-v1",
        "at": _now(),
        "meter": receipt,
        "event_count": len(events),
        "events_tail": events[-10:],
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    job = _read_json(SINA / "fbe-run-job-receipt-v1.json")
    row = record_run_job(job_receipt=job) if job else status_payload()
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
