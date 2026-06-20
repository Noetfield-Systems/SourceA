#!/usr/bin/env python3
"""FBE Hub projection — graph + registry + charter + W1 APIs."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
GRAPH_PATH = DATA / "fbe_node_graph_v1.json"
REGISTRY_PATH = SINA / "fbe-factory-registry-v1.json"
ORDERS_PATH = SINA / "fbe-work-orders-v1.json"
FEDERATED_PATH = SINA / "fbe-federated-receipt-v1.json"
CHARTER = "docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md"
sys.path.insert(0, str(ROOT / "scripts"))


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def registry_payload() -> dict:
    reg = _read_json(REGISTRY_PATH)
    return {"ok": True, "schema": "fbe-registry-v1", "at": _now(), "registry": reg}


def work_orders_payload() -> dict:
    ledger = _read_json(ORDERS_PATH)
    orders = ledger.get("orders") or []
    return {"ok": True, "schema": "fbe-work-orders-v1", "at": _now(), "count": len(orders), "orders": orders}


def bay_payload(*, bay_slug: str = "sample-bay") -> dict:
    ledger = ROOT / "receipts" / "bays" / bay_slug / "ledger.jsonl"
    lines = []
    if ledger.is_file():
        lines = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    run_r = _read_json(SINA / "fbe-refinery-run-receipt-v1.json")
    verify_r = _read_json(SINA / "fbe-refinery-verify-receipt-v1.json")
    return {
        "ok": True,
        "schema": "fbe-bay-status-v1",
        "at": _now(),
        "bay_slug": bay_slug,
        "first_bay": bay_slug,
        "template_id": "web-product-factory-v1",
        "ledger_lines": len(lines),
        "ledger": lines[-7:],
        "refinery_run_ok": run_r.get("ok"),
        "refinery_verify_ok": verify_r.get("ok"),
        "proof": verify_r.get("proof"),
        "deliveryMode": "prove_only",
    }


def refinery_payload() -> dict:
    verify_r = _read_json(SINA / "fbe-refinery-verify-receipt-v1.json")
    run_r = _read_json(SINA / "fbe-refinery-run-receipt-v1.json")
    try:
        from fbe.lib.cloud_adapter_v1 import status_payload as adapter_status  # noqa: WPS433
        adapter = adapter_status()
    except Exception as exc:
        adapter = {"ok": False, "error": str(exc)}
    bridge = _read_json(SINA / "fbe-mono-bridge-receipt-v1.json")
    return {
        "ok": bool(verify_r.get("ok")),
        "schema": "fbe-refinery-status-v1",
        "at": _now(),
        "wave": "W2",
        "refinery_verify": verify_r,
        "refinery_run": run_r,
        "cloud_adapter": adapter,
        "mono_bridge": bridge,
        "execution_plane": "headless_w2",
    }


def receipts_payload() -> dict:
    fed = _read_json(FEDERATED_PATH)
    motor = _read_json(SINA / "fbe-motor-delegate-receipt-v1.json")
    verify = _read_json(ROOT / "receipts" / "motor-verify-v1.json")
    refinery = _read_json(SINA / "fbe-refinery-verify-receipt-v1.json")
    return {
        "ok": True,
        "schema": "fbe-receipts-v1",
        "at": _now(),
        "federated": fed,
        "motor_delegate": motor,
        "motor_verify": verify,
        "refinery_verify": refinery,
    }


def assembly_payload(*, bay_slug: str = "sample-bay") -> dict:
    ledger = ROOT / "receipts" / "bays" / bay_slug / "assembly" / "ledger.jsonl"
    lines = []
    if ledger.is_file():
        lines = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    run_r = _read_json(SINA / "fbe-assembly-run-receipt-v1.json")
    verify_r = _read_json(SINA / "fbe-assembly-verify-receipt-v1.json")
    return {
        "ok": bool(verify_r.get("ok")),
        "schema": "fbe-assembly-status-v1",
        "at": _now(),
        "wave": "W3",
        "bay_slug": bay_slug,
        "ledger_lines": len(lines),
        "ledger": lines[-12:],
        "assembly_run_ok": run_r.get("ok"),
        "assembly_verify_ok": verify_r.get("ok"),
        "proof": verify_r.get("proof"),
        "deliveryMode": "prove_only",
        "execution_plane": "headless_w3",
    }


def job_payload() -> dict:
    job = _read_json(SINA / "fbe-run-job-receipt-v1.json")
    market = _read_json(SINA / "fbe-market-ready-verify-receipt-v1.json")
    return {
        "ok": bool(job.get("ok")),
        "schema": "fbe-job-status-v1",
        "at": _now(),
        "wave": job.get("wave") or "W3",
        "job": job,
        "market_ready": market,
        "tier_achieved": job.get("tier_achieved") or market.get("tier_achieved"),
        "tier_target": market.get("tier_target") or "MARKET_READY",
        "execution_plane": job.get("execution_plane") or "headless_w3",
    }


def exchange_payload(*, bay_slug: str = "trustfield-bay") -> dict:
    ledger = ROOT / "receipts" / "bays" / bay_slug / "refinery" / "ledger.jsonl"
    lines = []
    if ledger.is_file():
        lines = [json.loads(ln) for ln in ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    run_r = _read_json(SINA / "fbe-exchange-run-receipt-v1.json")
    verify_r = _read_json(SINA / "fbe-exchange-verify-receipt-v1.json")
    return {
        "ok": bool(verify_r.get("ok")),
        "schema": "fbe-exchange-status-v1",
        "at": _now(),
        "wave": "W4",
        "bay_slug": bay_slug,
        "template_id": "exchange-factory-v1",
        "factory_id": "factory_2",
        "ledger_lines": len(lines),
        "exchange_run_ok": run_r.get("ok"),
        "exchange_verify_ok": verify_r.get("ok"),
        "proof": verify_r.get("proof"),
        "tier_achieved": verify_r.get("tier_achieved"),
        "deliveryMode": "prove_only",
        "execution_plane": "headless_w4",
    }


def forge_payload(*, bay_slug: str = "forge-bay") -> dict:
    ref_ledger = ROOT / "receipts" / "bays" / bay_slug / "refinery" / "ledger.jsonl"
    lines = []
    if ref_ledger.is_file():
        lines = [json.loads(ln) for ln in ref_ledger.read_text(encoding="utf-8").splitlines() if ln.strip()]
    run_r = _read_json(SINA / "fbe-forge-run-receipt-v1.json")
    verify_r = _read_json(SINA / "fbe-forge-verify-receipt-v1.json")
    job_r = _read_json(SINA / "fbe-run-job-receipt-v1.json")
    wo = _read_json(SINA / "forge-active-work-order-v1.json")
    deploy_r = _read_json(ROOT / "receipts" / "bays" / bay_slug / "assembly" / "forge-deploy-pack-v1-v1.json")
    trace_base = ROOT / "receipts" / "bays" / bay_slug / "trace"
    preview_url = (deploy_r.get("manifest") or {}).get("preview_url") or wo.get("preview_url")
    mock_only = (deploy_r.get("manifest") or {}).get("mock_only", True)
    return {
        "ok": bool(verify_r.get("ok")),
        "schema": "fbe-forge-status-v1",
        "at": _now(),
        "wave": "W5",
        "bay_slug": bay_slug,
        "template_id": "forge-app-factory-v1",
        "factory_id": "factory_3",
        "ledger_lines": len(lines),
        "forge_run_ok": run_r.get("ok"),
        "forge_verify_ok": verify_r.get("ok"),
        "proof": verify_r.get("proof"),
        "tier_achieved": verify_r.get("tier_achieved"),
        "proof_class": verify_r.get("proof_class", "G0-G3"),
        "deliveryMode": "prove_only",
        "execution_plane": "headless_w5",
        "work_order_id": wo.get("plan_id") or job_r.get("work_order_id"),
        "stack": wo.get("stack"),
        "competitor": wo.get("competitor"),
        "run_id": wo.get("run_id"),
        "preview_url": preview_url,
        "mock_only": mock_only,
        "trace_paths": {
            "cost": str(trace_base / "cost.jsonl") if (trace_base / "cost.jsonl").is_file() else None,
            "eval": str(trace_base / "eval.jsonl") if (trace_base / "eval.jsonl").is_file() else None,
        },
    }


def fleet_payload() -> dict:
    fleet = _read_json(SINA / "fbe-fleet-run-receipt-v1.json")
    wil_pack = ROOT / "receipts" / "partners" / "wil_ai_design_partner" / "design-partner-receipt-v1.zip"
    tf_pack = ROOT / "receipts" / "partners" / "trustfield" / "design-partner-receipt-v1.zip"
    factories = [
        {"id": "factory_1", "template": "web-product-factory-v1", "bay": "sample-bay", "tenant": "wil_ai_design_partner"},
        {"id": "factory_2", "template": "exchange-factory-v1", "bay": "trustfield-bay", "tenant": "trustfield"},
        {"id": "factory_3", "template": "forge-app-factory-v1", "bay": "forge-bay", "tenant": "forge"},
    ]
    tier_map = {f.get("factory_id"): f.get("tier_achieved") for f in (fleet.get("factories") or [])}
    for row in factories:
        row["tier_achieved"] = tier_map.get(row["id"])
    return {
        "ok": bool(fleet.get("ok")),
        "schema": "fbe-fleet-status-v1",
        "at": _now(),
        "wave": "W6",
        "fleet_id": "fleet_3",
        "fleet_ready": bool(fleet.get("ok")),
        "factories": factories,
        "fleet_factories": fleet.get("factories"),
        "partner_packs": {
            "wil_ai_design_partner": str(wil_pack.relative_to(ROOT)) if wil_pack.is_file() else None,
            "trustfield": str(tf_pack.relative_to(ROOT)) if tf_pack.is_file() else None,
        },
        "wil_partner_ship_status": "ready" if wil_pack.is_file() else "pending",
        "execution_plane": "headless_w6_fleet",
    }


def billing_payload() -> dict:
    try:
        from fbe_billing_meter_v1 import status_payload  # noqa: WPS433
        return status_payload()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def partner_receipt_payload(*, tenant: str = "trustfield") -> dict:
    pack = ROOT / "receipts" / "partners" / tenant / "design-partner-receipt-v1.zip"
    receipt = ROOT / "receipts" / "partners" / tenant / "pack-receipt-v1.json"
    data = _read_json(receipt)
    return {
        "ok": pack.is_file(),
        "schema": "fbe-partner-receipt-status-v1",
        "at": _now(),
        "tenant": tenant,
        "pack_path": str(pack.relative_to(ROOT)) if pack.is_file() else None,
        "receipt": data,
    }


def payload() -> dict:
    graph = _read_json(GRAPH_PATH)
    registry = _read_json(REGISTRY_PATH)
    counts = graph.get("counts") or {}
    instances = registry.get("instances") or []
    motor_verify = _read_json(ROOT / "receipts" / "motor-verify-v1.json")
    refinery_verify = _read_json(SINA / "fbe-refinery-verify-receipt-v1.json")
    assembly_verify = _read_json(SINA / "fbe-assembly-verify-receipt-v1.json")
    job_receipt = _read_json(SINA / "fbe-run-job-receipt-v1.json")
    spawn_ready = graph.get("schema") == "fbe-node-graph-v1" and graph.get("line_node_count") == 76
    w1_ready = bool(motor_verify.get("ok"))
    w2_ready = bool(refinery_verify.get("ok"))
    exchange_verify = _read_json(SINA / "fbe-exchange-verify-receipt-v1.json")
    forge_verify = _read_json(SINA / "fbe-forge-verify-receipt-v1.json")
    billing = _read_json(SINA / "fbe-billing-meter-receipt-v1.json")
    wil_pack = ROOT / "receipts" / "partners" / "wil_ai_design_partner" / "design-partner-receipt-v1.zip"
    w3_ready = bool(assembly_verify.get("ok")) and bool(job_receipt.get("ok")) and job_receipt.get("template_id") == "web-product-factory-v1"
    w4_ready = bool(exchange_verify.get("ok")) and bool(job_receipt.get("ok")) and job_receipt.get("template_id") == "exchange-factory-v1"
    w5_ready = bool(forge_verify.get("ok")) and bool(job_receipt.get("ok")) and job_receipt.get("template_id") == "forge-app-factory-v1"
    fleet_receipt = _read_json(SINA / "fbe-fleet-run-receipt-v1.json")
    w6_ready = bool(fleet_receipt.get("ok"))
    wil_partner_ship = wil_pack.is_file()
    map_data = _read_json(DATA / "fbe_cloud_workspace_map_v1.json")
    mono_url = (map_data.get("mono_mirror") or {}).get("farm_url")
    try:
        from fbe.lib.cloud_adapter_v1 import status_payload as adapter_status  # noqa: WPS433

        adapter = adapter_status()
    except Exception as exc:
        adapter = {"ok": False, "error": str(exc)}

    return {
        "ok": True,
        "schema": "fbe-hub-projection-v1",
        "at": _now(),
        "wave": "W6" if w6_ready else ("W5" if w5_ready else ("W4" if w4_ready else "W3")),
        "charter_path": CHARTER,
        "first_bay": "sample-bay",
        "exchange_bay": "trustfield-bay",
        "forge_bay": "forge-bay",
        "graph_path": "data/fbe_node_graph_v1.json",
        "bundle_path": "data/fbe_factory_builder_bundle_v1.json",
        "graph_nodes": graph.get("line_node_count") or 76,
        "graph_total": graph.get("graph_total_nodes") or 80,
        "counts": counts,
        "factory_1_template": "web-product-factory-v1",
        "factory_2_template": "exchange-factory-v1",
        "factory_3_template": "forge-app-factory-v1",
        "factory_3_label": "Controlled App Factory",
        "factory_3_product": "Forge",
        "spawn_ready": spawn_ready and w1_ready,
        "motor_verify_ok": w1_ready,
        "refinery_verify_ok": w2_ready,
        "assembly_verify_ok": bool(assembly_verify.get("ok")),
        "exchange_verify_ok": bool(exchange_verify.get("ok")),
        "forge_verify_ok": bool(forge_verify.get("ok")),
        "wil_partner_ship": wil_partner_ship,
        "wil_partner_ship_status": "ready" if wil_partner_ship else "pending",
        "fleet_ready": w6_ready,
        "run_job_ok": bool(job_receipt.get("ok")),
        "billing_ok": bool(billing.get("ok")),
        "tier_target": job_receipt.get("tier_target") or ("GOLD" if w5_ready else ("PLATINUM" if w4_ready else "MARKET_READY")),
        "tier_achieved": job_receipt.get("tier_achieved"),
        "spawn_action": {
            "path": "/api/fbe/spawn/v1",
            "method": "POST",
            "body": {"template_id": "web-product-factory-v1"},
        },
        "run_bay_action": {
            "path": "/api/fbe/run-bay/v1",
            "method": "POST",
            "body": {"bay_slug": "sample-bay", "template_id": "web-product-factory-v1"},
        },
        "run_job_action": {
            "path": "/api/fbe/run-job/v1",
            "method": "POST",
            "body": {"bay_slug": "sample-bay", "template_id": "web-product-factory-v1"},
        },
        "exchange_action": {
            "path": "/api/fbe/run-exchange/v1",
            "method": "POST",
            "body": {"bay_slug": "trustfield-bay", "template_id": "exchange-factory-v1"},
        },
        "forge_action": {
            "path": "/api/fbe/run-forge/v1",
            "method": "POST",
            "body": {"bay_slug": "forge-bay", "template_id": "forge-app-factory-v1"},
        },
        "wil_partner_action": {
            "path": "/api/fbe/partner-receipt/v1",
            "method": "GET",
            "query": {"tenant": "wil_ai_design_partner"},
        },
        "fleet_action": {
            "path": "/api/fbe/run-fleet/v1",
            "method": "POST",
            "body": {},
        },
        "billing_glance": {
            "path": "/api/fbe/billing/v1",
            "method": "GET",
            "total_usd": billing.get("total_usd"),
        },
        "apis": {
            "registry": "/api/fbe/registry/v1",
            "work_orders": "/api/fbe/work-orders/v1",
            "receipts": "/api/fbe/receipts/v1",
            "spawn": "/api/fbe/spawn/v1",
            "actions": "/api/fbe/actions/v1",
            "bay": "/api/fbe/bay/v1",
            "run_bay": "/api/fbe/run-bay/v1",
            "refinery": "/api/fbe/refinery/v1",
            "assembly": "/api/fbe/assembly/v1",
            "job": "/api/fbe/job/v1",
            "run_job": "/api/fbe/run-job/v1",
            "exchange": "/api/fbe/exchange/v1",
            "run_exchange": "/api/fbe/run-exchange/v1",
            "forge": "/api/fbe/forge/v1",
            "run_forge": "/api/fbe/run-forge/v1",
            "fleet": "/api/fbe/fleet/v1",
            "run_fleet": "/api/fbe/run-fleet/v1",
            "billing": "/api/fbe/billing/v1",
            "partner_receipt": "/api/fbe/partner-receipt/v1",
        },
        "registry_instances": len(instances),
        "execution_plane": (
            "headless_w6_fleet" if w6_ready else
            ("headless_w5" if w5_ready else ("headless_w4" if w4_ready else ("headless_w3" if w3_ready else ("headless_w2" if w2_ready else "cloud_skeleton"))))
        ),
        "factories": fleet_payload().get("factories") if w6_ready else [
            {"id": "factory_1", "template": "web-product-factory-v1", "bay": "sample-bay"},
            {"id": "factory_2", "template": "exchange-factory-v1", "bay": "trustfield-bay"},
            {"id": "factory_3", "template": "forge-app-factory-v1", "bay": "forge-bay"},
        ],
        "mono_mirror_url": mono_url,
        "fbe_bay_result_path": "receipts/bays/sample-bay/",
        "fbe_exchange_result_path": "receipts/bays/trustfield-bay/",
        "fbe_forge_result_path": "receipts/bays/forge-bay/",
        "cloud_adapter": adapter,
        "w6_note": "Factory fleet W6 — three factories + dual design-partner packs",
        "w5_note": "Factory 3 Controlled App Factory (Forge product SKU) — GOLD G0-G3 prove_only · production deploy deferred",
        "w4_note": "Factory 2 exchange — PLATINUM deferred until CREED dealer PASS",
        "w3_note": "Line B wired assembly — full MARKET_READY deferred until 10 planned CHURCH npm wired",
        "w2_note": "Headless refinery prove subset — PLATINUM deferred until CREED dealer PASS",
        "deliveryMode": "prove_only",
        "epic": "E12",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = payload()
    if args.json:
        print(json.dumps(row, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
