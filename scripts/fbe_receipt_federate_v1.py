#!/usr/bin/env python3
"""FBE receipt federation — motor + refinery + assembly into run receipt."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SINA = Path.home() / ".sina"
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.receipts_v1 import collect_motor_receipts, expand_path, now_utc, sha256_dict, write_json  # noqa: E402

FEDERATED_LOCAL = ROOT / "receipts" / "federated-run-v1.json"
FEDERATED_SINA = SINA / "fbe-federated-receipt-v1.json"


def _collect_refinery_line(*, bay_slug: str = "sample-bay") -> dict:
    bay = ROOT / "receipts" / "bays" / bay_slug
    ledger = bay / "ledger.jsonl"
    run_r = {}
    run_path = SINA / "fbe-refinery-run-receipt-v1.json"
    if run_path.is_file():
        run_r = json.loads(run_path.read_text(encoding="utf-8"))
    verify_r = {}
    verify_path = SINA / "fbe-refinery-verify-receipt-v1.json"
    if verify_path.is_file():
        verify_r = json.loads(verify_path.read_text(encoding="utf-8"))
    receipts = {}
    if bay.is_dir():
        for p in bay.glob("*.json"):
            receipts[p.stem] = {"path": str(p), "exists": True}
    return {
        "mode": "headless_w2",
        "bay_slug": bay_slug,
        "run_ok": run_r.get("ok"),
        "verify_ok": verify_r.get("ok"),
        "proof": verify_r.get("proof"),
        "ledger_lines": len(ledger.read_text(encoding="utf-8").splitlines()) if ledger.is_file() else 0,
        "receipts": receipts,
    }


def _collect_assembly_line(*, bay_slug: str = "sample-bay") -> dict:
    asm = ROOT / "receipts" / "bays" / bay_slug / "assembly"
    ledger = asm / "ledger.jsonl"
    run_r = {}
    run_path = SINA / "fbe-assembly-run-receipt-v1.json"
    if run_path.is_file():
        run_r = json.loads(run_path.read_text(encoding="utf-8"))
    verify_r = {}
    verify_path = SINA / "fbe-assembly-verify-receipt-v1.json"
    if verify_path.is_file():
        verify_r = json.loads(verify_path.read_text(encoding="utf-8"))
    receipts = {}
    if asm.is_dir():
        for p in asm.glob("*.json"):
            receipts[p.stem] = {"path": str(p), "exists": True}
    return {
        "mode": "headless_w3",
        "bay_slug": bay_slug,
        "run_ok": run_r.get("ok"),
        "verify_ok": verify_r.get("ok"),
        "proof": verify_r.get("proof"),
        "ledger_lines": len(ledger.read_text(encoding="utf-8").splitlines()) if ledger.is_file() else 0,
        "receipts": receipts,
    }


def _collect_exchange_line(*, bay_slug: str = "trustfield-bay") -> dict:
    ex_dir = ROOT / "receipts" / "bays" / bay_slug / "refinery"
    ledger = ex_dir / "ledger.jsonl"
    run_r = {}
    run_path = SINA / "fbe-exchange-run-receipt-v1.json"
    if run_path.is_file():
        run_r = json.loads(run_path.read_text(encoding="utf-8"))
    verify_r = {}
    verify_path = SINA / "fbe-exchange-verify-receipt-v1.json"
    if verify_path.is_file():
        verify_r = json.loads(verify_path.read_text(encoding="utf-8"))
    receipts = {}
    if ex_dir.is_dir():
        for p in ex_dir.glob("*.json"):
            receipts[p.stem] = {"path": str(p), "exists": True}
    return {
        "mode": "headless_w4",
        "bay_slug": bay_slug,
        "factory_id": "factory_2",
        "run_ok": run_r.get("ok"),
        "verify_ok": verify_r.get("ok"),
        "proof": verify_r.get("proof"),
        "ledger_lines": len(ledger.read_text(encoding="utf-8").splitlines()) if ledger.is_file() else 0,
        "receipts": receipts,
    }


def _collect_forge_line(*, bay_slug: str = "forge-bay") -> dict:
    ref_dir = ROOT / "receipts" / "bays" / bay_slug / "refinery"
    asm_dir = ROOT / "receipts" / "bays" / bay_slug / "assembly"
    ref_ledger = ref_dir / "ledger.jsonl"
    asm_ledger = asm_dir / "ledger.jsonl"
    run_r = {}
    run_path = SINA / "fbe-forge-run-receipt-v1.json"
    if run_path.is_file():
        run_r = json.loads(run_path.read_text(encoding="utf-8"))
    verify_r = {}
    verify_path = SINA / "fbe-forge-verify-receipt-v1.json"
    if verify_path.is_file():
        verify_r = json.loads(verify_path.read_text(encoding="utf-8"))
    receipts = {}
    for base in (ref_dir, asm_dir):
        if base.is_dir():
            for p in base.glob("*.json"):
                receipts[p.stem] = {"path": str(p), "exists": True}
    return {
        "mode": "headless_w5",
        "bay_slug": bay_slug,
        "factory_id": "factory_3",
        "run_ok": run_r.get("ok"),
        "verify_ok": verify_r.get("ok"),
        "proof": verify_r.get("proof"),
        "proof_class": "G0-G3",
        "refinery_ledger_lines": len(ref_ledger.read_text(encoding="utf-8").splitlines()) if ref_ledger.is_file() else 0,
        "assembly_ledger_lines": len(asm_ledger.read_text(encoding="utf-8").splitlines()) if asm_ledger.is_file() else 0,
        "receipts": receipts,
    }


def _collect_fleet_line() -> dict:
    fleet: dict = {}
    path = SINA / "fbe-fleet-run-receipt-v1.json"
    if path.is_file():
        fleet = json.loads(path.read_text(encoding="utf-8"))
    tiers = {f.get("factory_id"): f.get("tier_achieved") for f in (fleet.get("factories") or [])}
    return {
        "mode": "headless_w6_fleet",
        "fleet_id": "fleet_3",
        "run_ok": fleet.get("ok"),
        "factories": fleet.get("factories"),
        "tier_map": tiers,
        "partner_packs": fleet.get("partner_packs"),
        "proof": "fleet_run PASS" if fleet.get("ok") else "fleet_run FAIL",
    }


def federate(
    *,
    work_order_id: str | None = None,
    bay_slug: str = "sample-bay",
    wave: str = "W2",
    factory_id: str = "factory_1",
) -> dict:
    motor = collect_motor_receipts()
    required_keys = ("session_gate", "motor_delegate", "compile", "cloud_adapter")
    missing = [k for k in required_keys if not motor.get(k, {}).get("exists")]
    refinery = _collect_refinery_line(bay_slug=bay_slug)
    assembly = _collect_assembly_line(bay_slug=bay_slug)
    exchange = _collect_exchange_line(bay_slug=bay_slug) if wave == "W4" else {}
    forge = _collect_forge_line(bay_slug="forge-bay") if wave in ("W5", "W6") else {}
    fleet_line = _collect_fleet_line() if wave == "W6" else {}
    fleet_path = SINA / "fbe-fleet-run-receipt-v1.json"
    fleet_ok = bool(fleet_line.get("run_ok")) if fleet_path.is_file() else True
    refinery_ok = bool(refinery.get("verify_ok") or refinery.get("run_ok"))
    assembly_ok = bool(assembly.get("verify_ok") or assembly.get("run_ok"))
    exchange_ok = bool(exchange.get("verify_ok") or exchange.get("run_ok"))
    forge_ok = bool(forge.get("verify_ok") or forge.get("run_ok"))

    lines = {
        "motor": {k: v for k, v in motor.items() if v.get("exists")},
        "refinery": forge if wave == "W5" else (exchange if wave == "W4" else refinery),
        "assembly": assembly if wave not in ("W4", "W5", "W6") else (forge if wave == "W5" else assembly),
    }
    if wave == "W4":
        lines["exchange"] = exchange
    if wave == "W5":
        lines["forge"] = forge
    if wave == "W6":
        lines["refinery"] = refinery
        lines["assembly"] = assembly
        lines["exchange"] = _collect_exchange_line(bay_slug="trustfield-bay")
        lines["forge"] = forge
        lines["fleet"] = fleet_line

    partial_ok = len(missing) < len(required_keys)
    ok = partial_ok and motor.get("motor_delegate", {}).get("ok", False) and refinery_ok
    if wave == "W3":
        ok = ok and assembly_ok
    if wave == "W4":
        ok = partial_ok and motor.get("motor_delegate", {}).get("ok", False) and exchange_ok and assembly_ok
    if wave == "W5":
        ok = partial_ok and motor.get("motor_delegate", {}).get("ok", False) and forge_ok
    if wave == "W6":
        ok = partial_ok and motor.get("motor_delegate", {}).get("ok", False) and fleet_ok

    market_r = {}
    if wave == "W6":
        market_path = SINA / "fbe-fleet-run-receipt-v1.json"
    elif wave == "W5":
        market_path = SINA / "fbe-forge-verify-receipt-v1.json"
    elif wave == "W4":
        market_path = SINA / "fbe-exchange-verify-receipt-v1.json"
    else:
        market_path = SINA / "fbe-market-ready-verify-receipt-v1.json"
    if market_path.is_file():
        market_r = json.loads(market_path.read_text(encoding="utf-8"))
    if wave == "W6" and market_r:
        tier_achieved = "fleet_3"
        tiers = (market_r.get("factories") or [])
        if tiers:
            tier_achieved = tiers[-1].get("tier_achieved") or tier_achieved
    else:
        tier_achieved = market_r.get("tier_achieved") or ("GOLD" if refinery_ok and partial_ok else "BRONZE")

    orders_path = expand_path("~/.sina/fbe-work-orders-v1.json")
    if orders_path.is_file():
        ledger = json.loads(orders_path.read_text(encoding="utf-8"))
        if work_order_id:
            match = next((o for o in ledger.get("orders") or [] if o.get("id") == work_order_id), None)
            if match:
                lines["work_order"] = match

    row = {
        "schema": "fbe-run-receipt-v1",
        "ok": ok,
        "at": now_utc(),
        "wave": wave,
        "factory_id": factory_id,
        "mode": "federated_headless",
        "deliveryMode": "prove_only",
        "work_order_id": work_order_id,
        "bay_slug": bay_slug,
        "lines": lines,
        "artifact_uri": None,
        "receipt_pack_uri": str(FEDERATED_SINA),
        "tier_achieved": tier_achieved,
        "sha256": "",
        "missing": missing,
    }
    row["sha256"] = sha256_dict({k: v for k, v in row.items() if k != "sha256"})

    write_json(FEDERATED_LOCAL, row)
    SINA.mkdir(parents=True, exist_ok=True)
    write_json(FEDERATED_SINA, row)
    try:
        from fbe.lib.trust_ledger_v1 import append_event as ledger_append  # noqa: WPS433

        jid = str(work_order_id or f"fed-{bay_slug}-{wave}")
        ledger_append(
            event_type="RECEIPT_FEDERATED",
            job_id=jid,
            factory_id=factory_id,
            payload={"wave": wave, "bay_slug": bay_slug, "ok": ok, "tier_achieved": tier_achieved},
        )
    except Exception:
        pass
    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="sample-bay")
    ap.add_argument("--work-order-id")
    ap.add_argument("--wave", default="W2")
    ap.add_argument("--factory-id", default="factory_1")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = federate(
        work_order_id=args.work_order_id,
        bay_slug=args.bay,
        wave=args.wave,
        factory_id=args.factory_id,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
