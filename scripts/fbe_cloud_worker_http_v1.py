#!/usr/bin/env python3
"""FBE cloud HTTP worker — headless API on Railway/Fly (port 8080)."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from fbe.lib.execution_contract_v1 import (  # noqa: E402
    contract_from_hub_body,
    json_safe_dict,
    normalize_receipt,
    policy_gate,
    validate_contract,
)


def _normalize_motor_path(path: str) -> str:
    """Legacy alias: /api/cloud-drain/* → /api/cloud-forge-run/* (physical rename v3)."""
    if path.startswith("/api/cloud-drain/"):
        return "/api/cloud-forge-run/" + path[len("/api/cloud-drain/") :]
    return path


def _json_response(handler: BaseHTTPRequestHandler, code: int, row: dict[str, Any]) -> None:
    body = json.dumps(json_safe_dict(row), indent=2).encode("utf-8")
    handler.send_response(code)
    handler.send_header("Content-Type", "application/json")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _auth_ok(handler: BaseHTTPRequestHandler) -> bool:
    secret = os.environ.get("FBE_INTERNAL_SECRET", "").strip()
    if not secret:
        return True
    auth = handler.headers.get("Authorization", "")
    return auth == f"Bearer {secret}"


def _single_cycle_gate(path: str, body: dict[str, Any] | None = None) -> dict[str, Any] | None:
    from cloud_auto_runtime_single_cycle_gate_v1 import claim_or_halt, is_gated_path  # noqa: WPS433

    if not is_gated_path(path):
        return None
    trigger = str((body or {}).get("trigger_source") or "http")
    return claim_or_halt(path=path, trigger_source=trigger)


def _run_local(path: str, body: dict[str, Any]) -> dict[str, Any]:
    bay = str(body.get("bay_slug") or "sample-bay")
    template = str(body.get("template_id") or body.get("factory_id") or "web-product-factory-v1")
    tenant = str(body.get("tenant") or body.get("tenant_id") or "")
    work_order_id = str(body.get("work_order_id") or "")

    if path == "/api/fbe/run-fleet/v1":
        from fbe_run_fleet_v1 import run_fleet  # noqa: WPS433

        return run_fleet()
    if path == "/api/fbe/spawn/v1":
        from fbe_spawn_factory_v1 import spawn  # noqa: WPS433

        return spawn(template_id=template, tenant=tenant or "wil_ai_design_partner")
    if path == "/api/fbe/run-bay/v1":
        from fbe_run_bay_v1 import run_bay_job  # noqa: WPS433

        return run_bay_job(
            bay_slug=bay,
            template_id=template,
            tenant=tenant or "wil_ai_design_partner",
            work_order_id=work_order_id,
        )
    if path in ("/api/fbe/run-job/v1", "/api/fbe/run-exchange/v1", "/api/fbe/run-forge/v1"):
        from fbe_run_job_v1 import run_job  # noqa: WPS433

        if path == "/api/fbe/run-exchange/v1":
            template = "exchange-factory-v1"
            bay = bay or "trustfield-bay"
            tenant = tenant or "trustfield"
        elif path == "/api/fbe/run-forge/v1":
            template = "forge-app-factory-v1"
            bay = bay or "forge-bay"
            tenant = tenant or "forge"
        forge_ctx = body.get("forge_context") if isinstance(body.get("forge_context"), dict) else None
        if not forge_ctx:
            forge_ctx = {
                k: body.get(k)
                for k in (
                    "stack",
                    "competitor",
                    "workstream",
                    "prompt_abs",
                    "task_graph_path",
                    "task_graph",
                    "run_id",
                    "plan_id",
                )
                if body.get(k) is not None
            }
        return run_job(
            bay_slug=bay,
            template_id=template,
            tenant=tenant,
            work_order_id=work_order_id,
            forge_context=forge_ctx or None,
        )
    if path == "/api/fbe/comprehension-loop/v1":
        from fbe_comprehension_bay_v1 import run_comprehension_bay  # noqa: WPS433

        draft = str(body.get("draft") or body.get("text") or "")
        founder_message = str(body.get("founder_message") or "")
        snap = body.get("system_snapshot")
        if not isinstance(snap, dict):
            snap = None
        variation_key = str(body.get("variation_key") or "").strip() or None
        config_override = body.get("config_override")
        if config_override is not None and not isinstance(config_override, dict):
            config_override = None
        return run_comprehension_bay(
            draft=draft,
            founder_message=founder_message,
            system_snapshot=snap,
            variation_key=variation_key,
            config_override=config_override,
            context_id=str(body.get("context_id") or body.get("job_id") or ""),
        )
    if path == "/api/fbe/comprehension-eval-batch/v1":
        from fbe_comprehension_eval_batch_v1 import run_eval_batch  # noqa: WPS433

        vk = str(body.get("variation_key") or "").strip() or None
        return run_eval_batch(variation_key=vk, write_receipt=bool(body.get("write_receipt", True)))
    if path == "/api/cloud-worker/dispatch/v1":
        from cloud_worker_dispatch_v1 import dispatch  # noqa: WPS433

        plan_id = str(body.get("plan_id") or "")
        dry_run = bool(body.get("dry_run"))
        if not plan_id:
            return {"ok": False, "error": "plan_id_required"}
        return dispatch(plan_id=plan_id, dry_run=dry_run)
    if path == "/api/cloud-forge-run/proceed/v1":
        from hub_cloud_forge_run_proceed_v1 import proceed_on_cloud  # noqa: WPS433

        return proceed_on_cloud(body if isinstance(body, dict) else {})
    if path == "/api/cloud-forge-run/queue/v1":
        from fbe.lib.cloud_forge_run_queue_v1 import handle_queue_action  # noqa: WPS433

        return handle_queue_action(body if isinstance(body, dict) else {})
    if path == "/api/cloud-forge-run/auto-tick/v1":
        from cloud_auto_runtime_v1 import run_cloud_auto_tick  # noqa: WPS433

        return run_cloud_auto_tick(body=body if isinstance(body, dict) else {})
    if path == "/api/cloud-forge-run/supabase/ensure/v1":
        from cloud_forge_run_supabase_v1 import count_rows, ensure_schema  # noqa: WPS433

        mig = ensure_schema()
        return {
            "ok": bool(mig.get("ok")),
            "schema": "cloud-forge-run-supabase-ensure-v1",
            "migration": mig,
            "count": count_rows(),
        }
    if path == "/api/cloud-forge-run/supabase/backfill/v1":
        from cloud_forge_run_supabase_v1 import backfill_from_artifacts, count_rows  # noqa: WPS433

        limit = int(body.get("limit") or 0)
        bf = backfill_from_artifacts(limit=limit)
        return {
            "ok": bool(bf.get("ok")),
            "schema": "cloud-forge-run-supabase-backfill-v1",
            "backfill": bf,
            "count": count_rows(),
        }
    if path == "/api/cloud-worker/dispatch-batch/v1":
        from cloud_worker_dispatch_v1 import dispatch_batch  # noqa: WPS433

        start = int(body.get("start") or 1)
        end = int(body.get("end") or 90)
        return dispatch_batch(start=start, end=end)
    if path == "/api/cloud-worker/build-summary/v1":
        from cloud_worker_dispatch_v1 import build_summary  # noqa: WPS433

        return build_summary()
    if path == "/api/forge/v01/run/v1":
        from forge_v01_engine_v1 import run_forge_from_disk, run_win_test  # noqa: WPS433

        result = run_forge_from_disk(write_output=True, root=ROOT)
        win = run_win_test(result)
        return {
            "ok": bool(win.get("ok")),
            "schema": "forge-v01-run-receipt-v1",
            "architecture": "A",
            "for_founder": {
                "show_this": result.get("summary_line"),
                "win_test_question": result.get("win_test_question"),
                "win_test_card": result.get("win_test_card"),
            },
            "summary_line": result.get("summary_line"),
            "win_test": win,
            "output_url": "/receipts/forge_v0.1_output.json",
            "blueprints_url": "/forge/blueprints/v01.json",
            **result,
        }
    if path == "/api/forge/v02/run/v1":
        from forge_v02_github_v1 import run_forge_v02_from_github  # noqa: WPS433

        gh = body.get("github") if isinstance(body.get("github"), dict) else {}
        try:
            result = run_forge_v02_from_github(
                write_output=True,
                root=ROOT,
                owner=str(gh.get("owner") or body.get("owner") or ""),
                repo=str(gh.get("repo") or body.get("repo") or ""),
                plans_path=str(gh.get("plans_path") or body.get("plans_path") or ""),
                ref=str(gh.get("ref") or body.get("ref") or ""),
            )
        except RuntimeError as exc:
            msg = str(exc)
            if msg.startswith("github_api_"):
                return {
                    "ok": False,
                    "schema": "forge-v02-run-receipt-v1",
                    "error": "github_fetch_failed",
                    "message": msg,
                    "hint": "Push plans/ to GitHub; set GITHUB_TOKEN on Railway for private repos",
                }
            raise
        return {
            "ok": True,
            "schema": "forge-v02-run-receipt-v1",
            "architecture": "A",
            "telemetry_line": result.get("telemetry_line"),
            "fetch_source": (result.get("data_health") or {}).get("fetch_source"),
            "for_founder": {
                "show_this": result.get("telemetry_line"),
                "win_test_question": result.get("win_test_question"),
                "win_test_card": (result.get("win_test_card") or [])[:10],
                "data_health_url": result.get("urls", {}).get("data_health"),
                "forge_top_url": result.get("urls", {}).get("forge_top"),
            },
            **result,
        }
    if path == "/api/forge/v02/implement/v1":
        from forge_v02_implement_v1 import run_forge_v02_implement  # noqa: WPS433

        plan_id = str(body.get("plan_id") or "")
        if not plan_id:
            return {"ok": False, "error": "plan_id_required"}
        try:
            receipt = run_forge_v02_implement(plan_id, write_output=True, root=ROOT)
        except ValueError as exc:
            return {"ok": False, "error": str(exc)}
        return {
            "ok": receipt.get("status") == "PASS",
            "schema": "forge-v02-implement-receipt-v1",
            "architecture": "A",
            "for_founder": {
                "show_this": receipt.get("telemetry_line") or f"{plan_id} {receipt.get('implement_mode')} {receipt.get('status')}",
            },
            **receipt,
        }
    if path == "/api/forge/v02/run-and-implement/v1":
        from forge_v02_implement_v1 import run_forge_v02_run_and_implement  # noqa: WPS433

        gh = body.get("github") if isinstance(body.get("github"), dict) else {}
        try:
            result = run_forge_v02_run_and_implement(
                write_output=True,
                root=ROOT,
                implement_top_n=int(body.get("implement_top_n") or 1),
                owner=str(gh.get("owner") or body.get("owner") or ""),
                repo=str(gh.get("repo") or body.get("repo") or ""),
                plans_path=str(gh.get("plans_path") or body.get("plans_path") or ""),
                ref=str(gh.get("ref") or body.get("ref") or ""),
            )
        except RuntimeError as exc:
            msg = str(exc)
            if msg.startswith("github_api_"):
                return {
                    "ok": False,
                    "schema": "forge-v02-run-and-implement",
                    "error": "github_fetch_failed",
                    "message": msg,
                    "hint": "Set GITHUB_TOKEN on Railway for private repos",
                }
            raise
        impl_ok = all(r.get("status") == "PASS" for r in (result.get("implement_results") or []))
        return {
            "ok": bool(result.get("forge", {}).get("telemetry_line")) and impl_ok,
            "schema": "forge-v02-run-and-implement-receipt-v1",
            "architecture": "A",
            "telemetry_line": result.get("telemetry_line"),
            "implement_telemetry": result.get("implement_telemetry"),
            "for_founder": {
                "show_this": "; ".join(
                    [str(result.get("telemetry_line") or "")] + list(result.get("implement_telemetry") or [])
                ).strip("; "),
            },
            **result,
        }
    if path == "/api/forge/v02/drain/v1":
        from forge_v02_drain_v1 import run_forge_v02_drain  # noqa: WPS433

        gh = body.get("github") if isinstance(body.get("github"), dict) else {}
        try:
            result = run_forge_v02_drain(
                max_cycles=int(body.get("max_cycles") if body.get("max_cycles") is not None else 20),
                target=str(body.get("target") or "top_20"),
                write_output=True,
                root=ROOT,
            )
        except RuntimeError as exc:
            msg = str(exc)
            if msg.startswith("github_api_"):
                return {
                    "ok": False,
                    "schema": "forge-v02-drain-v1",
                    "error": "github_fetch_failed",
                    "message": msg,
                }
            raise
        return {
            "ok": bool(result.get("ok")),
            "schema": "forge-v02-drain-receipt-v1",
            "architecture": "A",
            "for_founder": {"show_this": result.get("telemetry_line")},
            **result,
        }
    if path == "/api/fbe/loop-specialist/tick/v1":
        from fbe_cloud_loop_specialist_tick_v1 import run_cloud_loop_tick  # noqa: WPS433

        return run_cloud_loop_tick(body)
    if path == "/api/fbe/signal-factory/tick/v1":
        from fbe_cloud_signal_factory_tick_v1 import run_cloud_signal_factory_tick  # noqa: WPS433

        return run_cloud_signal_factory_tick(body)
    if path == "/api/fbe/gmail-sweep/v1":
        from fbe_cloud_ops_motors_v1 import run_cloud_gmail_sweep  # noqa: WPS433

        return run_cloud_gmail_sweep(body)
    if path == "/api/fbe/signal-factory/triage/v1":
        from fbe_cloud_ops_motors_v1 import run_cloud_signal_factory_triage  # noqa: WPS433

        return run_cloud_signal_factory_triage(body)
    if path == "/api/fbe/kaizen/nightly/v1":
        from fbe_cloud_ops_motors_v1 import run_cloud_kaizen_nightly  # noqa: WPS433

        return run_cloud_kaizen_nightly(body)
    if path == "/api/fbe/ops/heartbeat/v1":
        from fbe_cloud_ops_motors_v1 import run_cloud_ops_heartbeat  # noqa: WPS433

        return run_cloud_ops_heartbeat(body)
    return {"ok": False, "error": "unknown_route", "path": path}


class FbeWorkerHandler(BaseHTTPRequestHandler):
    server_version = "FBECloudWorker/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[FBE KERNEL] " + (fmt % args) + "\n")

    def do_GET(self) -> None:
        parsed = urlparse(_normalize_motor_path(self.path))
        if parsed.path in ("/health", "/api/fbe/health/v1"):
            _json_response(
                self,
                200,
                {
                    "ok": True,
                    "service": "fbe-cloud-worker",
                    "kernel": "fbe-v1",
                    "mode": "headless_http",
                },
            )
            return
        if parsed.path.startswith("/receipts/"):
            rel = parsed.path[len("/receipts/") :].lstrip("/")
            if not rel or ".." in rel.split("/"):
                _json_response(self, 400, {"ok": False, "error": "invalid_path"})
                return
            receipt_path = (ROOT / "receipts" / rel).resolve()
            receipts_root = (ROOT / "receipts").resolve()
            if not str(receipt_path).startswith(str(receipts_root)) or not receipt_path.is_file():
                _json_response(self, 404, {"ok": False, "error": "not_found"})
                return
            try:
                row = json.loads(receipt_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                _json_response(self, 500, {"ok": False, "error": "receipt_read_failed", "message": str(exc)})
                return
            _json_response(self, 200, row)
            return
        if parsed.path == "/api/cloud-forge-run/queue/v1":
            from fbe.lib.cloud_forge_run_queue_v1 import read_head  # noqa: WPS433

            _json_response(self, 200, read_head())
            return
        if parsed.path == "/api/cloud-forge-run/evidence-audit/v1":
            from autonomous_drain_receipt_cloud_v1 import (  # noqa: WPS433
                evidence_audit_html,
                evidence_audit_payload,
                evidence_audit_row,
            )
            from urllib.parse import parse_qs

            qs = parse_qs(parsed.query or "")
            plan = (qs.get("plan_id") or [""])[0].strip()
            accept = self.headers.get("Accept", "")
            if "text/html" in accept and not accept.strip().startswith("application/json"):
                try:
                    limit = min(int((qs.get("limit") or ["50"])[0]), 200)
                    offset = max(int((qs.get("offset") or ["0"])[0]), 0)
                except ValueError:
                    limit, offset = 50, 0
                html_doc = evidence_audit_html(limit=limit, offset=offset, plan_id=plan)
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.end_headers()
                self.wfile.write(html_doc.encode("utf-8"))
                return
            if plan:
                _json_response(self, 200, evidence_audit_row(plan_id=plan))
                return
            try:
                limit = min(int((qs.get("limit") or ["50"])[0]), 200)
                offset = max(int((qs.get("offset") or ["0"])[0]), 0)
            except ValueError:
                limit, offset = 50, 0
            _json_response(self, 200, evidence_audit_payload(limit=limit, offset=offset))
            return
        if parsed.path == "/api/cloud-forge-run/supabase/rows/v1":
            from cloud_forge_run_supabase_v1 import count_rows, query_rows  # noqa: WPS433
            from urllib.parse import parse_qs

            qs = parse_qs(parsed.query or "")
            try:
                limit = min(int((qs.get("limit") or ["20"])[0]), 200)
            except ValueError:
                limit = 20
            row = query_rows(limit=limit)
            row["total"] = count_rows().get("total")
            _json_response(self, 200, row)
            return
        if parsed.path == "/api/sourcea/plan-registry/v1":
            from sourcea_plan_registry_client_v1 import contains_secret_like, handle_query  # noqa: WPS433
            from urllib.parse import parse_qs

            qs = parse_qs(parsed.query or "")
            row = handle_query(qs)
            plan_id = (qs.get("plan_id") or [""])[0].strip()
            row["endpoint"] = "/api/sourcea/plan-registry/v1"
            row["contract"] = "sourcea-plan-registry-read-v1"
            if contains_secret_like(row):
                _json_response(self, 500, {"ok": False, "error": "secret_like_response_blocked"})
                return
            if plan_id and row.get("ok") and not row.get("found"):
                _json_response(self, 404, row)
                return
            _json_response(self, 200 if row.get("ok") else 422, row)
            return
        if parsed.path == "/api/sourcea/plan-registry/status/v1":
            from sourcea_plan_registry_client_v1 import contains_secret_like, handle_status  # noqa: WPS433
            from urllib.parse import parse_qs

            row = handle_status(parse_qs(parsed.query or ""))
            row["endpoint"] = "/api/sourcea/plan-registry/status/v1"
            if contains_secret_like(row):
                _json_response(self, 500, {"ok": False, "error": "secret_like_response_blocked"})
                return
            _json_response(self, 200 if row.get("ok") else 207, row)
            return
        if parsed.path == "/truth/status":
            from truth_layer_verifier_v1 import build_truth_status  # noqa: WPS433

            _json_response(self, 200, build_truth_status())
            return
        if parsed.path in ("/truth", "/truth/"):
            from truth_log_v1 import build_truth  # noqa: WPS433

            _json_response(self, 200, build_truth())
            return
        if parsed.path in ("/truth/live", "/truth/live/"):
            from truth_log_v1 import build_truth_live  # noqa: WPS433

            _json_response(self, 200, build_truth_live())
            return
        if parsed.path in ("/api/cloud-forge-run/observer/v1", "/observer", "/observer/"):
            try:
                from autonomous_drain_receipt_cloud_v1 import observer_html, observer_payload  # noqa: WPS433

                accept = self.headers.get("Accept", "")
                if "text/html" in accept or parsed.path.startswith("/observer"):
                    html = observer_html(limit=10)
                    self.send_response(200)
                    self.send_header("Content-Type", "text/html; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(html.encode("utf-8"))
                    return
                _json_response(self, 200, observer_payload(limit=10))
            except Exception as exc:
                _json_response(self, 500, {"ok": False, "error": "observer_failed", "message": str(exc)[:200]})
            return
        if parsed.path == "/forge/blueprints/v01.json":
            bp_path = ROOT / "data" / "forge-real-blueprints-v01.json"
            if not bp_path.is_file():
                _json_response(self, 404, {"ok": False, "error": "blueprints_not_found"})
                return
            try:
                row = json.loads(bp_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                _json_response(self, 500, {"ok": False, "error": "blueprints_read_failed", "message": str(exc)})
                return
            _json_response(self, 200, row)
            return
        if parsed.path == "/forge/contract/v02.json":
            contract_path = ROOT / "data" / "forge-v02-cloud-contract-v1.json"
            if not contract_path.is_file():
                _json_response(self, 404, {"ok": False, "error": "contract_not_found"})
                return
            try:
                row = json.loads(contract_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                _json_response(self, 500, {"ok": False, "error": "contract_read_failed", "message": str(exc)})
                return
            _json_response(self, 200, row)
            return
        if parsed.path.startswith("/api/worker-run-detail/v1"):
            from implement_run_detail_slice_v1 import handle_get_request  # noqa: WPS433

            code, row = handle_get_request(self.path, root=ROOT)
            _json_response(self, code, row)
            return
        if parsed.path.startswith("/api/competitor-evidence/v1"):
            from implement_competitor_evidence_slice_v1 import handle_get_request  # noqa: WPS433

            code, row = handle_get_request(self.path, root=ROOT)
            _json_response(self, code, row)
            return
        if parsed.path in ("/api/forge/v02/status/v1", "/api/forge/v02/status/v1/"):
            from forge_v02_status_v1 import build_forge_v02_status  # noqa: WPS433

            row = build_forge_v02_status(root=ROOT)
            _json_response(self, 200, row)
            return
        _json_response(self, 404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
        parsed = urlparse(_normalize_motor_path(self.path))
        path = parsed.path
        if path == "/api/cloud-forge-run/auto-tick/v1":
            if not _auth_ok(self):
                _json_response(self, 401, {"ok": False, "error": "unauthorized"})
                return
            length = int(self.headers.get("Content-Length") or 0)
            raw = self.rfile.read(length).decode("utf-8") if length else "{}"
            try:
                body = json.loads(raw) if raw.strip() else {}
            except json.JSONDecodeError:
                _json_response(self, 400, {"ok": False, "error": "invalid_json"})
                return
            body = body if isinstance(body, dict) else {}
            trigger = str(body.get("trigger_source") or "http")
            if trigger in ("cloudflare_cron", "cloudflare_scheduled", "hub_proceed_pack") or body.get("force_reset_gate"):
                from cloud_auto_runtime_single_cycle_gate_v1 import reset_gate_for_pack  # noqa: WPS433

                reset_gate_for_pack()
            halt = _single_cycle_gate(path, body)
            if halt:
                _json_response(self, 422, halt)
                return
            body["_cycle_claimed"] = True
            from cloud_auto_runtime_v1 import run_cloud_auto_tick  # noqa: WPS433

            row = run_cloud_auto_tick(body=body)
            _json_response(self, 200 if row.get("ok") else 422, row)
            return
        if not _auth_ok(self):
            _json_response(self, 401, {"ok": False, "error": "unauthorized"})
            return
        parsed = urlparse(self.path)
        path = parsed.path
        length = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            body = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            _json_response(self, 400, {"ok": False, "error": "invalid_json"})
            return

        if path == "/api/sourcea/plan-registry/receipt-link/v1":
            from sourcea_plan_registry_client_v1 import attach_execution_receipt, contains_secret_like  # noqa: WPS433

            body = body if isinstance(body, dict) else {}
            row = attach_execution_receipt(
                plan_id=str(body.get("plan_id") or ""),
                run_id=str(body.get("run_id") or body.get("job_id") or ""),
                receipt_path=str(body.get("receipt_path") or body.get("path") or ""),
                status=str(body.get("status") or "attached"),
                completed_at=str(body.get("completed_at") or ""),
                metadata=body.get("metadata") if isinstance(body.get("metadata"), dict) else None,
                dry_run=bool(body.get("dry_run")),
            )
            row["endpoint"] = "/api/sourcea/plan-registry/receipt-link/v1"
            if contains_secret_like(row):
                _json_response(self, 500, {"ok": False, "error": "secret_like_response_blocked"})
                return
            _json_response(self, 200 if row.get("ok") else 422, row)
            return

        if path == "/api/cloud-forge-run/proceed/v1":
            halt = _single_cycle_gate(path, body if isinstance(body, dict) else {})
            if halt:
                _json_response(self, 422, halt)
                return
            if isinstance(body, dict):
                body["_cycle_claimed"] = True

        contract = contract_from_hub_body(path, body)
        validation = validate_contract(contract)
        if not validation.get("ok"):
            _json_response(
                self,
                400,
                {"ok": False, "error": "invalid_execution_contract", "errors": validation.get("errors")},
            )
            return

        gate = policy_gate(contract, freeze_active=False, cloud_url_configured=True)
        if not gate.get("ok"):
            _json_response(
                self,
                403,
                {"ok": False, "error": "policy_gate_deny", "reasons": gate.get("reasons")},
            )
            return

        _ledger_hook("JOB_QUEUED", contract, {"path": path})
        _ledger_hook("POLICY_CHECKED", contract, {"decision": gate.get("decision")})
        _ledger_hook("KERNEL_STARTED", contract, {})

        started = time.time()
        try:
            row = _run_local(path, {**body, **contract})
        except Exception as exc:
            if path.startswith("/api/forge/v02"):
                _json_response(
                    self,
                    422,
                    {"ok": False, "error": "execution_failed", "message": str(exc), "path": path},
                )
                return
            _json_response(self, 500, {"ok": False, "error": "execution_failed", "message": str(exc)})
            return

        if path in (
            "/api/cloud-worker/dispatch/v1",
            "/api/cloud-worker/dispatch-batch/v1",
            "/api/cloud-worker/build-summary/v1",
            "/api/cloud-forge-run/proceed/v1",
            "/api/cloud-forge-run/queue/v1",
            "/api/cloud-forge-run/auto-tick/v1",
            "/api/cloud-drain/proceed/v1",
            "/api/cloud-drain/queue/v1",
            "/api/cloud-drain/auto-tick/v1",
            "/api/fbe/comprehension-loop/v1",
            "/api/fbe/comprehension-eval-batch/v1",
            "/api/forge/v01/run/v1",
            "/api/forge/v02/run/v1",
            "/api/forge/v02/implement/v1",
            "/api/forge/v02/run-and-implement/v1",
            "/api/forge/v02/drain/v1",
        ):
            row["execution_plane"] = row.get("execution_plane") or "headless_cloud"
            # Comprehension bay ran successfully even when verdict is BLOCKED — HTTP 200.
            if path == "/api/fbe/comprehension-loop/v1" and row.get("verdict"):
                code = 200
            else:
                code = 200 if row.get("ok") else 422
            _json_response(self, code, row)
            return

        row["execution_plane"] = row.get("execution_plane") or "headless_cloud"
        row["execution_mode"] = contract.get("execution_mode")
        row["execution_receipt"] = normalize_receipt(
            row,
            contract=contract,
            started_at=started,
            policy_passed=bool(gate.get("policy_passed")),
        )
        _ledger_hook("JOB_COMPLETED", contract, {"ok": row.get("ok")})
        _ledger_hook("LEDGER_SIGNED", contract, {"ok": row.get("ok")}, bridge=True)
        code = 200 if row.get("ok") else 422
        _json_response(self, code, row)


def _ledger_hook(
    event_type: str,
    contract: dict[str, Any],
    payload: dict[str, Any],
    *,
    bridge: bool = False,
) -> None:
    try:
        from fbe.lib.trust_ledger_v1 import append_event  # noqa: WPS433

        append_event(
            event_type=event_type,
            job_id=str(contract.get("job_id") or ""),
            factory_id=str(contract.get("factory_id") or ""),
            policy_pack=str(contract.get("policy_pack") or ""),
            kernel_hash=str(contract.get("kernel_hash") or ""),
            payload=payload,
            bridge_spine=bridge,
        )
    except Exception:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8080")))
    ap.add_argument("--host", default="0.0.0.0")
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), FbeWorkerHandler)
    print(f"[FBE KERNEL] HTTP listener on {args.host}:{args.port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
