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
    normalize_receipt,
    policy_gate,
    validate_contract,
)


def _json_response(handler: BaseHTTPRequestHandler, code: int, row: dict[str, Any]) -> None:
    body = json.dumps(row, indent=2).encode("utf-8")
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
                    "",
                    "workstream",
                    "prompt_abs",
                    "task_graph_path",
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
        return run_comprehension_bay(
            draft=draft,
            founder_message=founder_message,
            system_snapshot=snap,
        )
    if path == "/api/cloud-worker/dispatch/v1":
        from cloud_worker_dispatch_v1 import dispatch  # noqa: WPS433

        plan_id = str(body.get("plan_id") or "")
        dry_run = bool(body.get("dry_run"))
        if not plan_id:
            return {"ok": False, "error": "plan_id_required"}
        return dispatch(plan_id=plan_id, dry_run=dry_run)
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
                    "hint": "Push plans/ to GitHub or set FORGE_GITHUB_OWNER/REPO/PLANS_PATH",
                }
            raise
        return {
            "ok": True,
            "schema": "forge-v02-run-receipt-v1",
            "architecture": "A",
            "telemetry_line": result.get("telemetry_line"),
            "for_founder": {
                "show_this": result.get("telemetry_line"),
                "data_health_url": result.get("urls", {}).get("data_health"),
                "forge_top_url": result.get("urls", {}).get("forge_top"),
            },
            **result,
        }
    if path == "/api/fbe/loop-specialist/tick/v1":
        from fbe_cloud_loop_specialist_tick_v1 import run_cloud_loop_tick  # noqa: WPS433

        return run_cloud_loop_tick(body)
    return {"ok": False, "error": "unknown_route", "path": path}


class FbeWorkerHandler(BaseHTTPRequestHandler):
    server_version = "FBECloudWorker/1.0"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[FBE KERNEL] " + (fmt % args) + "\n")

    def do_GET(self) -> None:
        parsed = urlparse(self.path)
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
        _json_response(self, 404, {"ok": False, "error": "not_found"})

    def do_POST(self) -> None:
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
            _json_response(self, 500, {"ok": False, "error": "execution_failed", "message": str(exc)})
            return

        if path in (
            "/api/cloud-worker/dispatch/v1",
            "/api/cloud-worker/dispatch-batch/v1",
            "/api/cloud-worker/build-summary/v1",
            "/api/forge/v01/run/v1",
            "/api/forge/v02/run/v1",
        ):
            row["execution_plane"] = row.get("execution_plane") or "headless_cloud"
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
