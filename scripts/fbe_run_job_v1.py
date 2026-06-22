#!/usr/bin/env python3
"""FBE full job orchestrator — W3/W4/W5 multi-factory motor → lines → federate."""
from __future__ import annotations

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
SINA = Path.home() / ".sina"
RECEIPT_PATH = SINA / "fbe-run-job-receipt-v1.json"
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.motor_ensure_v1 import ensure_motor  # noqa: E402
from fbe_refinery_runner_v1 import run_bay as run_refinery  # noqa: E402
from fbe_verify_refinery_v1 import verify as refinery_verify  # noqa: E402
from fbe_assembly_runner_v1 import run_bay as run_assembly  # noqa: E402
from fbe_verify_assembly_v1 import verify as assembly_verify  # noqa: E402
from fbe_exchange_runner_v1 import run_exchange  # noqa: E402
from fbe_verify_exchange_v1 import verify as exchange_verify  # noqa: E402
from fbe_forge_runner_v1 import run_forge  # noqa: E402
from fbe_verify_forge_v1 import verify as forge_verify  # noqa: E402
from fbe_receipt_federate_v1 import federate  # noqa: E402
from fbe_verify_market_ready_v1 import verify as market_ready_verify  # noqa: E402
from fbe_run_receipt_pack_v1 import build_pack  # noqa: E402
from fbe_mono_bridge_v1 import mirror_full_job  # noqa: E402
from fbe_cloud_sync_v1 import pull_assembly_receipts  # noqa: E402
from fbe_spawn_factory_v1 import mark_w3_ready, mark_w4_ready, mark_w5_ready  # noqa: E402
from fbe_billing_meter_v1 import record_run_job  # noqa: E402
from fbe_design_partner_receipt_v1 import build_partner_pack  # noqa: E402


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def _resolve_factory(*, template_id: str, bay_slug: str, tenant: str) -> dict:
    jobs = _read_json(DATA / "fbe_bay_jobs_v1.json")
    factories = jobs.get("factories") or {}
    if template_id in factories:
        f = factories[template_id]
        return {
            "template_id": template_id,
            "bay_slug": bay_slug or f.get("bay_slug", "sample-bay"),
            "tenant": tenant or f.get("tenant", "wil_ai_design_partner"),
            "wave": f.get("wave", "W3"),
            "factory_id": f.get("factory_id", "factory_1"),
        }
    if template_id == "exchange-factory-v1":
        ex = _read_json(DATA / "fbe_exchange_job_v1.json")
        return {
            "template_id": template_id,
            "bay_slug": bay_slug or ex.get("bay_slug", "trustfield-bay"),
            "tenant": tenant or ex.get("tenant", "trustfield"),
            "wave": "W4",
            "factory_id": "factory_2",
        }
    if template_id == "forge-app-factory-v1":
        fg = _read_json(DATA / "fbe_forge_job_v1.json")
        return {
            "template_id": template_id,
            "bay_slug": bay_slug or fg.get("bay_slug", "forge-bay"),
            "tenant": tenant or fg.get("tenant", "forge"),
            "wave": "W5",
            "factory_id": "factory_3",
        }
    return {
        "template_id": template_id,
        "bay_slug": bay_slug,
        "tenant": tenant,
        "wave": "W3",
        "factory_id": "factory_1",
    }


def run_job(
    *,
    bay_slug: str = "sample-bay",
    template_id: str = "web-product-factory-v1",
    tenant: str = "",
    work_order_id: str = "",
    forge_context: dict | None = None,
) -> dict:
    cfg = _resolve_factory(template_id=template_id, bay_slug=bay_slug, tenant=tenant)
    bay_slug = cfg["bay_slug"]
    tenant = cfg["tenant"]
    template_id = cfg["template_id"]
    wave = cfg.get("wave", "W3")
    factory_id = cfg.get("factory_id", "factory_1")
    woid = work_order_id or f"wo-{bay_slug}-{wave.lower()}"

    motor = ensure_motor(wave=wave, bay_slug=bay_slug, factory_id=factory_id)

    if template_id == "exchange-factory-v1":
        exchange_run = run_exchange(bay_slug=bay_slug, tenant=tenant)
        exchange_v = exchange_verify(bay_slug=bay_slug)
        refinery_v = {"ok": True, "proof": "exchange_refinery via exchange_runner"}
        assembly_v = {"ok": True, "proof": "exchange_assembly via exchange_runner"}
        market = exchange_v
        tier_achieved = exchange_v.get("tier_achieved")
        tier_target = exchange_v.get("tier_target", "PLATINUM")
        mode = "full_job_w4"
        plane = "headless_w4"
        refinery_run = exchange_run
        assembly_run = exchange_run
    elif template_id == "forge-app-factory-v1":
        ctx = forge_context or {}
        run_id = str(ctx.get("run_id") or "")
        woid = work_order_id or str(ctx.get("plan_id") or "")
        forge_run = run_forge(
            bay_slug=bay_slug,
            tenant=tenant,
            work_order_id=woid,
            run_id=run_id,
        )
        router_result: dict = {}
        critic_result: dict = {}
        graph_path = str(ctx.get("task_graph_path") or "")
        graph: dict = {}
        if isinstance(ctx.get("task_graph"), dict):
            graph = ctx["task_graph"]
        elif graph_path and Path(graph_path).is_file():
            graph = json.loads(Path(graph_path).read_text(encoding="utf-8"))
        if graph:
            from forge_router_execute_v01 import execute_graph  # noqa: WPS433
            from forge_critic_loop_v01 import run_critic_loop  # noqa: WPS433

            router_result = execute_graph(graph=graph, bay=bay_slug)
            pick_stub = {
                "id": ctx.get("plan_id"),
                "stack": ctx.get("stack"),
                "": ctx.get(""),
                "workstream": ctx.get("workstream"),
            }
            critic_result = run_critic_loop(
                graph=graph,
                router_result=router_result,
                pick=pick_stub,
                bay=bay_slug,
            )
        forge_v = forge_verify(bay_slug=bay_slug)
        refinery_v = {"ok": True, "proof": "forge_refinery via forge_runner"}
        assembly_v = {"ok": True, "proof": "forge_assembly via forge_runner"}
        market = forge_v
        tier_achieved = forge_v.get("tier_achieved")
        tier_target = forge_v.get("tier_target", "GOLD")
        mode = "full_job_w5"
        plane = "headless_w5"
        refinery_run = forge_run
        assembly_run = forge_run
    else:
        refinery_run = run_refinery(bay_slug=bay_slug, tenant=tenant)
        refinery_v = refinery_verify(bay_slug=bay_slug)
        assembly_run = run_assembly(bay_slug=bay_slug, tenant=tenant)
        assembly_v = assembly_verify(bay_slug=bay_slug)
        market = market_ready_verify(bay_slug=bay_slug)
        tier_achieved = market.get("tier_achieved")
        tier_target = market.get("tier_target", "MARKET_READY")
        mode = "full_job_w3"
        plane = "headless_w3"

    from fbe_motor_delegate_v1 import delegate as motor_delegate  # noqa: WPS433

    if os.environ.get("FBE_MODE") == "headless" or os.environ.get("FBE_HOME") == "/app":
        from fbe_cloud_motor_seed_v1 import seed  # noqa: WPS433

        seed(force=True)
    else:
        motor_delegate(fbe_prove=True, skip_federate=True)
    fed = federate(work_order_id=woid, bay_slug=bay_slug, wave=wave, factory_id=factory_id)
    sync = pull_assembly_receipts(bay_slug=bay_slug)
    bridge = mirror_full_job(bay_slug=bay_slug, template_id=template_id, tier_achieved=tier_achieved)
    pack = build_pack(bay_slug=bay_slug)

    row = {
        "schema": "fbe-run-job-receipt-v1",
        "ok": False,
        "at": _now(),
        "wave": wave,
        "factory_id": factory_id,
        "bay_slug": bay_slug,
        "template_id": template_id,
        "tenant": tenant,
        "work_order_id": woid,
        "mode": mode,
        "execution_plane": plane,
        "deliveryMode": "prove_only",
        "tier_target": tier_target,
        "tier_achieved": tier_achieved,
        "lines": {
            "motor": {"ok": motor.get("ok"), "proof": motor.get("proof")},
            "refinery": {"ok": refinery_v.get("ok"), "proof": refinery_v.get("proof")},
            "assembly": {"ok": assembly_v.get("ok"), "proof": assembly_v.get("proof")},
        },
        "federated_ok": fed.get("ok"),
        "market_ready_proof": market.get("proof"),
        "artifact_uri": pack.get("artifact_uri"),
        "receipt_pack_uri": pack.get("receipt_pack_uri"),
        "mono_bridge": bridge.get("farm_status"),
        "cloud_sync": sync.get("action"),
    }

    if template_id == "exchange-factory-v1":
        row["ok"] = (
            bool(motor.get("ok"))
            and bool(exchange_run.get("ok"))
            and bool(exchange_v.get("ok"))
            and bool(fed.get("ok"))
        )
        partner = build_partner_pack(tenant=tenant, bay_slug=bay_slug)
        row["partner_pack_uri"] = partner.get("receipt_pack_uri")
        row["receipt_pack_uri"] = partner.get("receipt_pack_uri") or row["receipt_pack_uri"]
    elif template_id == "forge-app-factory-v1":
        row["ok"] = (
            bool(motor.get("ok"))
            and bool(forge_run.get("ok"))
            and bool(forge_v.get("ok"))
            and bool(fed.get("ok"))
            and (not critic_result or critic_result.get("ok", True))
        )
        row["forge_router"] = router_result or None
        row["forge_critic"] = critic_result or None
        row["forge_context"] = forge_context
        row["proof_class"] = "G0-G3"
    else:
        row["ok"] = (
            bool(motor.get("ok"))
            and bool(refinery_run.get("ok"))
            and bool(refinery_v.get("ok"))
            and bool(assembly_run.get("ok"))
            and bool(assembly_v.get("ok"))
            and bool(fed.get("ok"))
            and bool(market.get("ok"))
        )
        if row.get("ok") and tenant == "wil_ai_design_partner":
            partner = build_partner_pack(tenant=tenant, bay_slug=bay_slug)
            row["partner_pack_uri"] = partner.get("receipt_pack_uri")

    SINA.mkdir(parents=True, exist_ok=True)
    RECEIPT_PATH.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    record_run_job(job_receipt=row)

    if row.get("ok"):
        if template_id == "exchange-factory-v1":
            mark_w4_ready(template_id=template_id)
        elif template_id == "forge-app-factory-v1":
            mark_w5_ready(template_id=template_id)
        else:
            mark_w3_ready(template_id=template_id)

    return row


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--bay", default="")
    ap.add_argument("--template", default="web-product-factory-v1")
    ap.add_argument("--tenant", default="")
    ap.add_argument("--work-order-id", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    default_bay = "sample-bay"
    if args.template == "exchange-factory-v1":
        default_bay = "trustfield-bay"
    elif args.template == "forge-app-factory-v1":
        default_bay = "forge-bay"
    row = run_job(
        bay_slug=args.bay or default_bay,
        template_id=args.template,
        tenant=args.tenant,
        work_order_id=args.work_order_id,
    )
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
