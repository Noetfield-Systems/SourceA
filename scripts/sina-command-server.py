#!/usr/bin/env python3
"""Hub server — Worker Hub (H1) + Machine Hub (H2) + API on :13020."""
from __future__ import annotations

import json
import mimetypes
import os
import subprocess
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlparse

SOURCE_A = Path(__file__).resolve().parents[1]
PANEL_DIR = SOURCE_A / "agent-control-panel"
PORT = int(os.environ.get("SINA_COMMAND_PORT", "13020"))


def _commitments_context(payload: dict) -> dict:
    """Full context for Track — must match build_payload() in sina_command_lib."""
    bowl = payload.get("bowl") or {}
    cc = payload.get("command_center") or {}
    founder = cc.get("founder") or {}
    return {
        "bowl": bowl,
        "progress": {
            "todos": bowl.get("open_todos") or [],
            "parallel_plans": bowl.get("parallel_plans") or [],
        },
        "ops": payload.get("ops_blockers") or founder.get("ops_cards") or [],
        "founder": founder,
        "repos": cc.get("repos"),
        "founder_notes": payload.get("founder_notes"),
        "prompt_queue": payload.get("prompt_queue"),
        "agent_loop": payload.get("agent_loop"),
        "semej": payload.get("semej"),
        "prompt_direction": payload.get("prompt_direction"),
        "ecosystem": payload.get("ecosystem"),
    }


def _run_loop_chain_tick(body: dict | None = None) -> dict:
    """E2E loop chain: observatory → advisory → investigator → judge → specialist → routing panel."""
    body = body or {}
    steps: list[dict] = []
    ok = True
    py = sys.executable
    scripts = SOURCE_A / "scripts"

    def _step(name: str, mod: str, fn: str = "run", **kwargs) -> dict:
        nonlocal ok
        try:
            import importlib

            m = importlib.import_module(mod)
            row = getattr(m, fn)(**kwargs)
            step_ok = bool(row.get("ok", True))
            ok = ok and step_ok
            steps.append({"step": name, "ok": step_ok, "schema": row.get("schema")})
            return row
        except Exception as exc:
            ok = False
            steps.append({"step": name, "ok": False, "error": str(exc)})
            return {}

    obs = _step("observatory", "loop_observatory_report_v1", "run_report", write=True)
    adv = _step("advisory", "future_loop_prompt_advisory_circle_v1", "run_advisory", write=True)
    inv = _step("investigator", "investigator_circle_run_v1", "run_investigation", write=True)
    jv = _step("judge_loop", "judge_loop_room_v1", "run_judge_loop", write=True)
    dispatch = bool(body.get("dispatch"))
    spec = _step(
        "loop_specialist",
        "loop_specialist_tick_v1",
        "run_tick",
        write=True,
        dispatch=dispatch if dispatch else None,
    )
    panel = _step("routing_panel", "founder_routing_panel_v1", "run_panel", write=True)
    dl = _step("disclosure_ladder", "disclosure_ladder_v1", "run_tick", write=True)
    ms = _step("mcp_stack_free_tier", "mcp_stack_free_tier_v1", "run_tick", write=True)
    tp = _step("tool_pick_two_phase", "tool_pick_two_phase_v1", "run_tick", write=True)
    at = _step("anti_theater_loop", "anti_theater_validator_loop_v1", "run_loop", write=True)
    pu = _step("plans_unified", "plans_unified_upgrade_v1", "run_upgrade", write=True)
    p0 = _step("phase0_reference", "phase0_freemium_sandbox_pulse_v1", "run_pulse", write=True)
    wtm = _step("world_model_plan_check", "world_model_plan_check_v1", "run_check", write=True)
    return {
        "schema": "loop-chain-tick-v1",
        "ok": ok,
        "steps": steps,
        "observatory_ok": obs.get("ok"),
        "advisory_hash": adv.get("deterministic_hash"),
        "investigation_verdict": inv.get("investigation_verdict"),
        "loop_verdict": jv.get("loop_verdict"),
        "tick_decision": spec.get("tick_decision"),
        "founder_routing_panel_line": panel.get("founder_routing_panel_line"),
        "disclosure_line": dl.get("disclosure_line"),
        "investigator_line": inv.get("investigator_line"),
        "judge_loop_line": jv.get("judge_loop_line"),
        "loop_specialist_line": spec.get("loop_specialist_line"),
        "mcp_stack_line": ms.get("mcp_stack_line"),
        "tool_pick_line": tp.get("tool_pick_line"),
        "anti_theater_line": at.get("anti_theater_line"),
        "plans_unified_line": pu.get("plans_unified_line"),
        "phase0_line": p0.get("phase0_line") or (pu.get("phase0_check") or {}).get("line"),
        "world_model_line": wtm.get("world_model_line"),
    }


sys.path.insert(0, str(SOURCE_A / "scripts"))
from founder_notes import add_note as add_founder_note, set_note_status  # noqa: E402
from agent_loop import handle_action as agent_loop_action, loop_payload  # noqa: E402
from semej_loop import handle_semej_action, semej_payload  # noqa: E402
from loop_advisor import handle_advisor_action  # noqa: E402
from prompt_direction import handle_action as prompt_direction_action, direction_payload  # noqa: E402
from prompt_queue import handle_action as prompt_queue_action, queue_payload  # noqa: E402
from sina_command_lib import (  # noqa: E402
    SOURCE_A as SA,
    branches_registry,
    command_data_response,
    command_data_shell_response,
    founder_actions_grouped,
    get_hub_payload,
    hub_after_mutation,
    launch_mini_app,
    mark_todo_done,
    mini_apps_registry,
    open_mini_app,
    read_rule,
    run_branch_action,
    warm_hub_cache_from_disk,
    write_rule,
)
from sina_command_lib import list_notes  # noqa: E402

ALLOWED_OPEN_ROOTS = [
    SA,
    Path.home() / ".sina",
    Path.home() / "Desktop",
    Path.home() / "Desktop/SinaaiMonoRepo",
    Path.home() / "Desktop/mergepack",
    Path.home() / "Desktop/SinaaiDataBase",
    Path.home() / "Desktop/SinaPromptOS",
]


def cors_headers(handler: BaseHTTPRequestHandler) -> None:
    handler.send_header("Access-Control-Allow-Origin", "*")
    handler.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
    handler.send_header("Access-Control-Allow-Headers", "Content-Type")


def dispatch_fbe_route(path: str, body: dict, local_fn) -> dict:
    from fbe.lib.hub_cloud_proxy_v1 import dispatch_fbe  # noqa: WPS433

    return dispatch_fbe(path=path, body=body, local_fn=local_fn)


class SinaCommandHandler(BaseHTTPRequestHandler):
    """Serves static panel + JSON API on the same origin."""

    def log_message(self, fmt, *args):
        pass

    def do_OPTIONS(self):
        self.send_response(204)
        cors_headers(self)
        self.end_headers()

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, {"ok": True, "service": "sina-command", "port": PORT})
            return
        if path == "/status":
            # CLI/API agents probe eval gateway here (not /api/status).
            try:
                from healthy_queue_blocker_lib import live_eval_available  # noqa: WPS433

                eval_ok, eval_reason = live_eval_available()
            except Exception as exc:
                eval_ok, eval_reason = False, str(exc)
            self._json(
                200,
                {
                    "ok": True,
                    "service": "sina-command",
                    "port": PORT,
                    "eval_credits_ok": bool(eval_ok),
                    "eval_mode": eval_reason,
                },
            )
            return
        if path == "/shutdown":
            self._json(200, {"ok": True, "message": "Use POST /shutdown to stop hub"})
            return
        if path == "/api/rule":
            rel = parse_qs(urlparse(self.path).query).get("path", [""])[0]
            if not rel:
                self._json(400, {"error": "path query required"})
                return
            self._json(200, read_rule(rel))
            return
        if path in ("/api/state", "/command-data.json"):
            from founder_directive_ssot_v1 import command_retired_forever  # noqa: WPS433

            if command_retired_forever():
                self._json(200, command_data_shell_response())
                return
            self._json(200, command_data_response())
            return
        if path == "/command-data-shell.json":
            self._json(200, command_data_shell_response())
            return
        if path == "/api/branches":
            self._json(200, {"ok": True, "branches": branches_registry()})
            return
        if path == "/api/founder/actions":
            self._json(200, {"ok": True, "groups": founder_actions_grouped()})
            return
        if path in ("/api/goal1-auto-run-status", "/api/goal1-loop-status"):
            from sina_command_lib import goal1_auto_run_payload, goal1_hub_status_bundle  # noqa: WPS433

            g1 = goal1_auto_run_payload()
            self._json(
                200,
                {
                    "ok": True,
                    **goal1_hub_status_bundle(g1),
                    "turn_progress": g1.get("turn_progress"),
                    "last_turn_proof": g1.get("last_turn_proof"),
                    "remaining_pids": (g1.get("executor") or {}).get("live_pids"),
                },
            )
            return
        if path == "/api/hub-sync":
            from hub_sync_slim_v1 import hub_sync_payload  # noqa: WPS433

            self._json(200, hub_sync_payload())
            return
        if path == "/api/surface/v1":
            from hub_surface_v1 import surface_payload  # noqa: WPS433

            self._json(200, surface_payload())
            return
        if path == "/api/worker-hub/v1":
            from worker_hub_v1 import worker_hub_payload  # noqa: WPS433

            self._json(200, worker_hub_payload())
            return
        if path == "/api/forge/v01/output/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_get_from_cloud  # noqa: WPS433

            row = proxy_get_from_cloud(path="/receipts/forge_v0.1_output.json", timeout_s=30)
            self._json(200 if row.get("ok", True) and row.get("schema") else 502, row)
            return
        if path == "/api/forge/v02/data-health/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_get_from_cloud  # noqa: WPS433

            row = proxy_get_from_cloud(path="/receipts/forge_v0.2/data_health.json", timeout_s=30)
            self._json(200 if row.get("schema") else 502, row)
            return
        if path == "/api/forge/v02/top/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_get_from_cloud  # noqa: WPS433

            row = proxy_get_from_cloud(path="/receipts/forge_v0.2/forge_v0.2_top.json", timeout_s=30)
            self._json(200 if row.get("schema") else 502, row)
            return
        if path == "/api/forge/v02/status/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_get_from_cloud  # noqa: WPS433

            row = proxy_get_from_cloud(path="/api/forge/v02/status/v1", timeout_s=30)
            self._json(200 if row.get("schema") else 502, row)
            return
        if path == "/api/worker-hub/extended/v1":
            from worker_hub_v1 import worker_hub_extended_payload  # noqa: WPS433

            self._json(200, worker_hub_extended_payload())
            return
        if path == "/api/sourcea/plan-registry/v1":
            from sourcea_plan_registry_client_v1 import contains_secret_like, handle_query  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            row = handle_query(qs)
            row["endpoint"] = "/api/sourcea/plan-registry/v1"
            row["contract"] = "sourcea-plan-registry-read-v1"
            if contains_secret_like(row):
                self._json(500, {"ok": False, "error": "secret_like_response_blocked"})
                return
            plan_id = (qs.get("plan_id") or [""])[0].strip()
            if plan_id and row.get("ok") and not row.get("found"):
                self._json(404, row)
                return
            self._json(200 if row.get("ok") else 422, row)
            return
        if path == "/api/worker-hub/outbound-salvage/v1":
            from outbound_telemetry_v1 import hub_slice as outbound_salvage_slice  # noqa: WPS433

            self._json(200, outbound_salvage_slice())
            return
        if path == "/api/fbe/v1":
            from fbe_hub_projection_v1 import payload as fbe_payload  # noqa: WPS433

            self._json(200, fbe_payload())
            return
        if path == "/api/fbe/cloud-proxy/v1":
            from fbe.lib.hub_cloud_proxy_v1 import status_payload as fbe_proxy_status  # noqa: WPS433

            self._json(200, fbe_proxy_status())
            return
        if path == "/api/fbe/catalog/v1":
            from fbe.lib.factory_spec_v1 import catalog_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            tier = (qs.get("tier") or [""])[0]
            self._json(200, catalog_payload(tier=tier))
            return
        if path == "/api/fbe/ledger/v1":
            from fbe.lib.trust_ledger_v1 import ledger_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            job_id = (qs.get("job_id") or [""])[0]
            self._json(200, ledger_payload(job_id=job_id))
            return
        if path == "/api/fbe/registry/v1":
            from fbe_hub_projection_v1 import registry_payload  # noqa: WPS433

            self._json(200, registry_payload())
            return
        if path == "/api/fbe/work-orders/v1":
            from fbe_hub_projection_v1 import work_orders_payload  # noqa: WPS433

            self._json(200, work_orders_payload())
            return
        if path == "/api/fbe/receipts/v1":
            from fbe_hub_projection_v1 import receipts_payload  # noqa: WPS433

            self._json(200, receipts_payload())
            return
        if path == "/api/fbe/bay/v1":
            from fbe_hub_projection_v1 import bay_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            bay = (qs.get("bay_slug") or ["sample-bay"])[0]
            self._json(200, bay_payload(bay_slug=bay))
            return
        if path == "/api/fbe/refinery/v1":
            from fbe_hub_projection_v1 import refinery_payload  # noqa: WPS433

            self._json(200, refinery_payload())
            return
        if path == "/api/fbe/assembly/v1":
            from fbe_hub_projection_v1 import assembly_payload  # noqa: WPS433

            bay = (qs.get("bay_slug") or ["sample-bay"])[0]
            self._json(200, assembly_payload(bay_slug=bay))
            return
        if path == "/api/fbe/job/v1":
            from fbe_hub_projection_v1 import job_payload  # noqa: WPS433

            self._json(200, job_payload())
            return
        if path == "/api/fbe/exchange/v1":
            from fbe_hub_projection_v1 import exchange_payload  # noqa: WPS433

            bay = (qs.get("bay_slug") or ["trustfield-bay"])[0]
            self._json(200, exchange_payload(bay_slug=bay))
            return
        if path == "/api/fbe/forge/v1":
            from fbe_hub_projection_v1 import forge_payload  # noqa: WPS433

            bay = (qs.get("bay_slug") or ["forge-bay"])[0]
            self._json(200, forge_payload(bay_slug=bay))
            return
        if path == "/api/fbe/fleet/v1":
            from fbe_hub_projection_v1 import fleet_payload  # noqa: WPS433

            self._json(200, fleet_payload())
            return
        if path == "/api/fbe/billing/v1":
            from fbe_hub_projection_v1 import billing_payload  # noqa: WPS433

            self._json(200, billing_payload())
            return
        if path == "/api/fbe/partner-receipt/v1":
            from fbe_hub_projection_v1 import partner_receipt_payload  # noqa: WPS433

            tenant = (qs.get("tenant") or ["trustfield"])[0]
            self._json(200, partner_receipt_payload(tenant=tenant))
            return
        if path == "/api/runtime-wrapper/v1":
            from sourcea_runtime_wrapper_v1 import status_payload  # noqa: WPS433

            self._json(200, status_payload())
            return
        if path == "/api/machine-hub/v1":
            from machine_hub_v1 import machine_hub_payload  # noqa: WPS433

            self._json(200, machine_hub_payload())
            return
        if path.startswith("/api/slice/"):
            from hub_slice_v1 import slice_payload  # noqa: WPS433

            domain = path[len("/api/slice/") :].strip("/")
            row = slice_payload(domain)
            self._json(200 if row.get("ok") else 404, row)
            return
        if path == "/api/form-founder-draft-v1":
            draft_path = Path.home() / ".sina/canvas-form-picks-draft-v1.json"
            if draft_path.is_file():
                try:
                    draft = json.loads(draft_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    draft = {"picks": {}}
            else:
                draft = {"picks": {}}
            self._json(200, {"ok": True, "picks": draft.get("picks") or {}, "path": str(draft_path)})
            return
        if path == "/api/form-official-canvas-route-v1":
            from form_official_canvas_route_v1 import hub_canvas_target  # noqa: WPS433

            row = hub_canvas_target()
            self._json(200, {"ok": True, **row})
            return
        if path == "/api/live-founder-decision-form-v1":
            from live_founder_decision_form_v1 import founder_readable_cards, payload as live_form_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            if "index" in qs:
                try:
                    idx = int(qs["index"][0])
                except (TypeError, ValueError):
                    self._json(400, {"ok": False, "error": "index must be integer"})
                    return
                cards = founder_readable_cards()
                if idx < 0 or idx >= len(cards):
                    self._json(404, {"ok": False, "error": "index out of range", "total": len(cards)})
                    return
                self._json(
                    200,
                    {
                        "ok": True,
                        "index": idx,
                        "total": len(cards),
                        "card": cards[idx],
                    },
                )
                return

            self._json(200, live_form_payload())
            return
        if path == "/api/live/v1":
            self._handle_live_sse()
            return
        if path == "/api/live/queue":
            from hub_sync_slim_v1 import live_queue_payload  # noqa: WPS433

            self._json(200, live_queue_payload())
            return
        if path == "/api/live/factory":
            from hub_sync_slim_v1 import live_factory_payload  # noqa: WPS433

            self._json(200, live_factory_payload())
            return
        if path == "/api/apps":
            self._json(200, {"ok": True, "apps": mini_apps_registry()})
            return
        if path == "/api/notes":
            self._json(200, {"ok": True, "notes": list_notes()})
            return
        if path == "/api/ai/advisory":
            from sina_ai_advisory import load_cached_advisory  # noqa: WPS433

            self._json(200, load_cached_advisory())
            return
        if path == "/api/prompt-queue":
            self._json(200, queue_payload())
            return
        if path == "/api/prompt-direction":
            self._json(200, direction_payload())
            return
        if path == "/api/agent-loop":
            warm_hub_cache_from_disk()
            payload = get_hub_payload()
            self._json(200, loop_payload(hub_payload=payload))
            return
        if path == "/api/advisor/chat":
            from loop_advisor import advisor_payload  # noqa: WPS433

            self._json(200, {"ok": True, **advisor_payload()})
            return
        if path == "/api/brain/chat/v1":
            from sourcea_brain_chat_v1 import status_payload  # noqa: WPS433

            self._json(200, status_payload())
            return
        if path == "/api/intelligence-circle":
            from intelligence_circle import circle_payload  # noqa: WPS433

            warm_hub_cache_from_disk()
            payload = get_hub_payload()
            self._json(200, circle_payload(hub_payload=payload))
            return
        if path == "/api/semej":
            self._json(200, semej_payload())
            return
        if path == "/api/site-guide":
            from site_guide import build_site_index, search_site  # noqa: WPS433

            payload = get_hub_payload()
            q = parse_qs(urlparse(self.path).query).get("q", [""])[0]
            self._json(
                200,
                {"ok": True, "hits": search_site(q, payload) if q else [], "index_size": len(build_site_index(payload))},
            )
            return
        if path == "/api/commitments":
            from founder_commitments import commitments_payload  # noqa: WPS433

            payload = get_hub_payload()
            self._json(200, commitments_payload(**_commitments_context(payload)))
            return
        if path == "/api/audit-backlog":
            from command_audit_backlog import audit_backlog_payload  # noqa: WPS433

            self._json(200, audit_backlog_payload())
            return
        if path == "/api/agent-review":
            from agent_command_reviews import reviews_payload  # noqa: WPS433

            self._json(200, reviews_payload())
            return
        if path == "/api/agent-workspaces":
            from agent_private_workspaces import workspaces_payload  # noqa: WPS433

            self._json(200, workspaces_payload())
            return
        if path == "/api/workspace-vault":
            from agent_workspace_vault import handle_vault_action  # noqa: WPS433

            q = parse_qs(urlparse(self.path).query)
            agent_id = (q.get("agent_id") or [""])[0]
            self._json(200, handle_vault_action({"action": "list", "agent_id": agent_id}))
            return
        if path == "/api/workspace-mirror":
            from agent_workspace_mirror import handle_mirror_action  # noqa: WPS433

            q = parse_qs(urlparse(self.path).query)
            agent_id = (q.get("agent_id") or [""])[0]
            self._json(200, handle_mirror_action({"action": "get", "agent_id": agent_id}))
            return
        if path == "/api/agent-scoreboard":
            from agent_scoreboard import handle_scoreboard_action  # noqa: WPS433

            q = parse_qs(urlparse(self.path).query)
            agent_id = (q.get("agent_id") or [""])[0]
            self._json(200, handle_scoreboard_action({"action": "list", "agent_id": agent_id}))
            return
        if path == "/api/essay-discourse":
            from agent_essay_discourse import handle_essay_action  # noqa: WPS433

            q = parse_qs(urlparse(self.path).query)
            subject = (q.get("subject") or [""])[0]
            self._json(200, handle_essay_action({"action": "list", "subject": subject}))
            return
        if path == "/api/incident-room":
            from agent_incident_system import incident_room_payload  # noqa: WPS433

            q = parse_qs(urlparse(self.path).query)
            agent_id = (q.get("agent_id") or [""])[0]
            self._json(200, incident_room_payload(agent_id or None))
            return
        if path == "/api/conflict-room":
            from agent_conflict_room import conflict_room_payload  # noqa: WPS433

            q = parse_qs(urlparse(self.path).query)
            agent_id = (q.get("agent_id") or [""])[0]
            self._json(200, conflict_room_payload(agent_id or None))
            return
        if path == "/api/founder-requests":
            from founder_request_tracker import handle_action  # noqa: WPS433

            self._json(200, handle_action({"action": "list"}))
            return
        if path == "/api/founder-advisor-discussion":
            from founder_advisor_discussion_v1 import handle_action  # noqa: WPS433

            self._json(200, handle_action({"action": "list"}))
            return
        if path == "/api/agent-truth-bundle-v1":
            from agent_truth_bundle_v1 import build_agent_truth_bundle  # noqa: WPS433

            self._json(200, build_agent_truth_bundle())
            return
        if path == "/api/order-guardian":
            from task_orders_guardian import handle_action  # noqa: WPS433

            hub = get_hub_payload()
            self._json(200, handle_action({"action": "list"}, hub))
            return
        if path == "/api/founder-agent-guide":
            from founder_agent_use_guide import handle_action  # noqa: WPS433

            hub = get_hub_payload()
            self._json(200, handle_action({"action": "list"}, hub))
            return
        if path == "/api/governance-drift":
            from governance_drift_engine import handle_drift_action  # noqa: WPS433

            self._json(200, handle_drift_action({"action": "get"}))
            return
        if path == "/api/governance-unify":
            from agent_governance_unification import handle_unification_action  # noqa: WPS433

            self._json(200, handle_unification_action({"action": "list"}))
            return
        if path == "/api/council-room":
            from agent_council_room import council_room_payload  # noqa: WPS433
            from agent_system_unified import system_unified_payload  # noqa: WPS433

            room = council_room_payload()
            room["system_unified"] = system_unified_payload()
            self._json(200, room)
            return
        if path == "/api/important-docs":
            from important_docs_index import important_docs_payload  # noqa: WPS433

            self._json(200, important_docs_payload())
            return
        if path == "/api/roadmaps-goals":
            from roadmaps_goals import roadmaps_goals_payload  # noqa: WPS433

            self._json(200, roadmaps_goals_payload())
            return
        if path == "/api/system-roadmap":
            from system_roadmap import system_roadmap_payload  # noqa: WPS433

            self._json(200, system_roadmap_payload())
            return
        if path == "/api/stranger-agent-safety-v1":
            from stranger_agent_safety_live_wire_v1 import live_wire_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            refresh = (qs.get("refresh") or ["0"])[0] in ("1", "true", "yes")
            role = (qs.get("role") or ["any"])[0]
            self._json(200, live_wire_payload(refresh=refresh, role=role))
            return
        if path == "/api/pre-write-guard-v1":
            from pre_write_guard_v1 import check_pre_write  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            agent = (qs.get("agent") or ["cursor"])[0]
            target = (qs.get("path") or [""])[0]
            explicit = (qs.get("explicit_order") or [""])[0]
            if not target:
                self._json(400, {"ok": False, "error": "path query required"})
                return
            self._json(200, check_pre_write(agent=agent, path=target, explicit_order=explicit))
            return
        if path == "/api/meta-reasoning-policy":
            from meta_reasoning_policy import handle_action  # noqa: WPS433

            hub = get_hub_payload()
            self._json(200, handle_action({"action": "get"}, hub))
            return
        if path == "/api/agent-research":
            from agent_research_pipeline import handle_action as research_action  # noqa: WPS433

            self._json(200, research_action({"action": "list"}))
            return
        if path == "/api/execution-spine":
            from execution_spine.spine import spine_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            if task_id:
                from execution_spine.writer import read_memory  # noqa: WPS433

                rows = read_memory(task_id=task_id)
                self._json(200, {"ok": True, "task_id": task_id, "records": rows})
                return
            self._json(200, spine_payload())
            return
        if path == "/api/execution-intelligence":
            from execution_intelligence.api import intelligence_payload  # noqa: WPS433

            self._json(200, intelligence_payload())
            return
        if path == "/api/execution-intelligence-v2":
            from execution_intelligence_v2.api import intelligence_v2_payload  # noqa: WPS433

            self._json(200, intelligence_v2_payload())
            return
        if path == "/api/execution-patterns-v1":
            from execution_intelligence.pattern_engine.api import patterns_v1_payload  # noqa: WPS433

            self._json(200, patterns_v1_payload())
            return
        if path == "/api/context-intelligence-v1":
            from execution_intelligence.context_intelligence.api import context_intelligence_v1_payload  # noqa: WPS433

            self._json(200, context_intelligence_v1_payload())
            return
        if path == "/api/execution-context":
            from execution_intelligence.context_intelligence.api import execution_context_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            action_id = (qs.get("action_id") or [""])[0] or None
            self._json(200, execution_context_payload(task_id=task_id, action_id=action_id))
            return
        if path in ("/api/execution-decisions-v1", "/api/execution-decisions"):
            from execution_intelligence.decision_memory.api import decisions_v1_payload  # noqa: WPS433

            self._json(200, decisions_v1_payload())
            return
        if path == "/api/execution-feedback-v1":
            from execution_intelligence.feedback_loop.api import feedback_v1_payload  # noqa: WPS433

            self._json(200, feedback_v1_payload())
            return
        if path == "/api/planner-upgrade-v1":
            from execution_intelligence.planner_upgrade.api import planner_upgrade_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            raw_candidates = (qs.get("actions") or [""])[0]
            candidates = [a.strip() for a in raw_candidates.split(",") if a.strip()] or None
            self._json(200, planner_upgrade_v1_payload(candidate_actions=candidates))
            return
        if path == "/api/self-optimization-v1":
            from execution_intelligence.self_optimization.api import self_optimization_v1_payload  # noqa: WPS433

            self._json(200, self_optimization_v1_payload())
            return
        if path == "/api/tool-graph-v1":
            from runtime.tool_graph.api import tool_graph_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            goal = (qs.get("goal") or qs.get("goal_tool") or ["pos-run"])[0]
            task_id = (qs.get("task_id") or [""])[0]
            self._json(200, tool_graph_v1_payload(goal_tool_id=goal, task_id=task_id))
            return
        if path == "/api/tool-graph-verify-v1":
            from runtime.tool_graph_verification.api import tool_graph_verify_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            goal = (qs.get("goal") or qs.get("goal_tool") or ["pos-run"])[0]
            task_id = (qs.get("task_id") or [""])[0]
            self._json(200, tool_graph_verify_v1_payload(goal_tool_id=goal, task_id=task_id))
            return
        if path == "/api/execution-router-v1":
            from runtime.execution_router.api import execution_router_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            goal = (qs.get("goal") or qs.get("goal_tool") or ["pos-run"])[0]
            task_id = (qs.get("task_id") or [""])[0]
            self._json(200, execution_router_v1_payload(goal_tool_id=goal, task_id=task_id))
            return
        if path == "/api/prompt-router-v1":
            from autonomy_stack_api import prompt_router_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            keyword = (qs.get("keyword") or ["implement"])[0]
            lane = (qs.get("lane") or ["sourcea"])[0]
            dry = (qs.get("dry_run") or ["1"])[0].lower() not in ("0", "false", "no")
            invoke = (qs.get("invoke_loop") or ["0"])[0].lower() in ("1", "true", "yes")
            self._json(200, prompt_router_v1_payload(keyword=keyword, lane=lane, dry_run=dry, invoke_loop=invoke))
            return
        if path == "/api/execution-kernel-v1":
            from autonomy_stack_api import execution_kernel_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            lane = (qs.get("lane") or ["sourcea"])[0]
            keyword = (qs.get("keyword") or ["PLAN WITH NO ASF"])[0]
            invoke = (qs.get("invoke_loop") or ["0"])[0].lower() in ("1", "true", "yes")
            spine = (qs.get("use_spine_router") or ["0"])[0].lower() in ("1", "true", "yes")
            self._json(
                200,
                execution_kernel_v1_payload(
                    lane=lane, keyword=keyword, invoke_loop=invoke, use_spine_router=spine
                ),
            )
            return
        if path == "/api/execution-state-v1":
            from autonomy_stack_api import execution_state_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            lane = (qs.get("lane") or ["sourcea"])[0]
            self._json(200, execution_state_v1_payload(lane=lane))
            return
        if path == "/api/execution-scheduler-v1":
            from autonomy_stack_api import execution_scheduler_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            lane = (qs.get("lane") or ["sourcea"])[0]
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            self._json(200, execution_scheduler_v1_payload(lane=lane, force=force))
            return
        if path == "/api/execution-state-machine-v1":
            from autonomy_stack_api import execution_state_machine_v1_payload  # noqa: WPS433

            self._json(200, execution_state_machine_v1_payload())
            return
        if path == "/api/repair-loop-v1":
            from runtime.repair_loop.api import repair_loop_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            goal = (qs.get("goal") or qs.get("goal_tool") or ["pos-run"])[0]
            task_id = (qs.get("task_id") or [""])[0]
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            self._json(200, repair_loop_v1_payload(goal_tool_id=goal, task_id=task_id, force_refresh=force))
            return
        if path == "/api/code-intelligence-v1":
            from pre_llm.code_intelligence.api import code_intelligence_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            query_type = (qs.get("query") or qs.get("query_type") or [""])[0]
            query_arg = (qs.get("arg") or qs.get("query_arg") or [""])[0]
            self._json(
                200,
                code_intelligence_v1_payload(
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                    query_type=query_type,
                    query_arg=query_arg,
                ),
            )
            return
        if path == "/api/graph-fusion-v1":
            from pre_llm.graph_fusion.api import graph_fusion_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            query_type = (qs.get("query") or qs.get("query_type") or [""])[0]
            query_arg = (qs.get("arg") or qs.get("query_arg") or [""])[0]
            self._json(
                200,
                graph_fusion_v1_payload(
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                    query_type=query_type,
                    query_arg=query_arg,
                ),
            )
            return
        if path == "/api/llm-context-packet-schema-v1":
            from pre_llm.context_packet.schema import schema_contract_payload  # noqa: WPS433

            self._json(200, schema_contract_payload())
            return
        if path == "/api/vector-retrieval-v1":
            from pre_llm.vector_retrieval.api import vector_retrieval_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            top_k = int((qs.get("top_k") or ["8"])[0] or "8")
            self._json(
                200,
                vector_retrieval_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                    top_k=top_k,
                ),
            )
            return
        if path == "/api/memory-git-bridge-v1":
            from pre_llm.memory_git_bridge.api import memory_git_bridge_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            top_k = int((qs.get("top_k") or ["12"])[0] or "12")
            self._json(
                200,
                memory_git_bridge_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                    top_k=top_k,
                ),
            )
            return
        if path == "/api/query-expansion-v1":
            from pre_llm.query_expansion.api import query_expansion_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            self._json(
                200,
                query_expansion_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                ),
            )
            return
        if path == "/api/graph-reasoning-v1":
            from pre_llm.graph_reasoning.api import graph_reasoning_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            target = (qs.get("target") or qs.get("arg") or [""])[0]
            target_type = (qs.get("target_type") or qs.get("type") or ["file"])[0]
            self._json(
                200,
                graph_reasoning_v1_payload(
                    text=text,
                    target=target,
                    target_type=target_type,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                ),
            )
            return
        if path == "/api/context-ranking-v1":
            from pre_llm.context_ranking.api import context_ranking_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            top_k = int((qs.get("top_k") or ["16"])[0] or "16")
            self._json(
                200,
                context_ranking_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                    top_k=top_k,
                ),
            )
            return
        if path == "/api/planning-engine-v1":
            from pre_llm.planning_engine.api import planning_engine_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            self._json(
                200,
                planning_engine_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                ),
            )
            return
        if path == "/api/tool-router-v1":
            from pre_llm.tool_router.api import tool_router_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            gate_mode = (qs.get("gate_mode") or ["shadow"])[0]
            self._json(
                200,
                tool_router_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                    gate_mode=gate_mode,
                ),
            )
            return
        if path == "/api/validation-layer-v1":
            from pre_llm.validation_layer.api import validation_layer_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            self._json(
                200,
                validation_layer_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                ),
            )
            return
        if path == "/api/diff-intelligence-v1":
            from pre_llm.diff_intelligence.api import diff_intelligence_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            commits_back = int((qs.get("commits_back") or ["3"])[0] or "3")
            self._json(
                200,
                diff_intelligence_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                    commits_back=commits_back,
                ),
            )
            return
        if path == "/api/context-compression-v1":
            from pre_llm.context_compression.api import context_compression_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            tl_raw = (qs.get("token_limit") or [""])[0]
            token_limit = int(tl_raw) if tl_raw.isdigit() and int(tl_raw) > 0 else None
            self._json(
                200,
                context_compression_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                    token_limit=token_limit,
                ),
            )
            return
        if path == "/api/context-assembly-v1":
            from pre_llm.context_assembly.api import context_assembly_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            self._json(
                200,
                context_assembly_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                ),
            )
            return
        if path == "/api/model-dispatch-gate-v1":
            import model_dispatch  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or ""
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            self._json(
                200,
                model_dispatch.gate_status_payload(
                    task_id=task_id,
                    repo_root=repo_root,
                    query_text=text,
                ),
            )
            return
        if path == "/api/eval-packet-v1":
            from eval_packet_v1.runner import hub_payload as eval_packet_payload  # noqa: WPS433

            self._json(200, eval_packet_payload())
            return
        if path == "/api/eval-packet-v1b":
            from eval_packet_v1b.runner import hub_payload as eval_1b_payload  # noqa: WPS433
            from eval_packet_v1b.runner import run_eval as eval_1b_run  # noqa: WPS433

            if self.command == "POST":
                body = self._read_json_body()
                force = bool(body.get("live") or body.get("force_live"))
                self._json(200, eval_1b_run(write_report=True, live=force))
                return
            qs = parse_qs(urlparse(self.path).query)
            force_live = (qs.get("live") or qs.get("force_live") or [""])[0] in ("1", "true", "yes")
            self._json(200, eval_1b_payload(force_live=force_live))
            return
        if path == "/api/dispatch-policy-v1":
            from runtime.dispatch_policy.api import dispatch_policy_v1_get  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_class = (qs.get("task_class") or [""])[0]
            eval_tier = (qs.get("eval_tier") or [""])[0]
            dry_run = (qs.get("dry_run") or ["1"])[0] not in ("0", "false", "no")
            founder_override = (qs.get("founder_override") or [""])[0] in ("1", "true", "yes")
            self._json(
                200,
                dispatch_policy_v1_get(
                    task_class=task_class,
                    eval_tier=eval_tier,
                    dry_run=dry_run,
                    founder_override=founder_override,
                ),
            )
            return
        if path == "/api/graph-executor-v1":
            from runtime.graph_executor.api import graph_executor_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            goal = (qs.get("goal_tool_id") or ["pos-run"])[0]
            tid = (qs.get("task_id") or [""])[0]
            self._json(200, graph_executor_v1_payload(goal_tool_id=goal, task_id=tid))
            return
        if path == "/api/user-workspace-signals-v1":
            from pre_llm.user_signals.api import user_workspace_signals_v1_payload  # noqa: WPS433

            if self.command == "GET":
                self._json(200, user_workspace_signals_v1_payload())
                return
            body = self._read_json_body()
            self._json(200, user_workspace_signals_v1_payload(body))
            return
        if path == "/api/gate-receipts-v1":
            from gate_receipts_hub import gate_receipts_hub_payload  # noqa: WPS433

            self._json(200, gate_receipts_hub_payload())
            return
        if path == "/api/event-bus-v1":
            from runtime.event_bus.bus_v1 import event_bus_payload, publish, tail  # noqa: WPS433

            if self.command == "POST":
                body = self._read_json_body()
                topic = str(body.get("topic") or "hub.touch")
                payload = dict(body.get("payload") or body)
                payload.pop("topic", None)
                self._json(200, publish(topic=topic, payload=payload, source=str(body.get("source") or "hub")))
                return
            qs = parse_qs(urlparse(self.path).query)
            topic = (qs.get("topic") or [None])[0]
            n = int((qs.get("n") or ["20"])[0] or 20)
            out = event_bus_payload()
            if topic:
                out["tail"] = tail(topic=topic, n=n)
            self._json(200, out)
            return
        if path == "/api/strategic-synthesis-v1":
            from strategic_synthesis_hub import strategic_synthesis_payload  # noqa: WPS433

            self._json(200, strategic_synthesis_payload())
            return
        if path == "/api/agent-rules-in-charge-v1":
            from agent_rules_loop_orchestrator import handle_api as rules_loop_api  # noqa: WPS433
            from agent_rules_in_charge import rules_in_charge_payload  # noqa: WPS433

            if self.command == "GET":
                self._json(200, rules_in_charge_payload())
                return
            body = self._read_json_body()
            self._json(200, rules_loop_api(body))
            return
        if path == "/api/packet-readiness-v1":
            from pre_llm.packet_readiness.hub_surface import packet_readiness_hub_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or ""
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            self._json(
                200,
                packet_readiness_hub_payload(
                    task_id=task_id or "hub-readiness",
                    repo_root=repo_root,
                    query_text=text,
                ),
            )
            return
        if path == "/api/packet-memory-merge-v1":
            from pre_llm.packet_memory_merge.api import packet_memory_merge_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            self._json(
                200,
                packet_memory_merge_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                ),
            )
            return
        if path == "/api/intent-engine-v1":
            from pre_llm.intent_engine.api import intent_engine_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            text = (qs.get("text") or qs.get("prompt") or qs.get("input") or [""])[0]
            query_type = (qs.get("query") or qs.get("query_type") or [""])[0]
            query_arg = (qs.get("arg") or qs.get("query_arg") or [""])[0]
            self._json(
                200,
                intent_engine_v1_payload(
                    text=text,
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                    query_type=query_type,
                    query_arg=query_arg,
                ),
            )
            return
        if path == "/api/dependency-graph-v1":
            from pre_llm.dependency_graph.api import dependency_graph_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            repo_root = (qs.get("repo_root") or [""])[0] or None
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            query_type = (qs.get("query") or qs.get("query_type") or [""])[0]
            query_arg = (qs.get("arg") or qs.get("query_arg") or [""])[0]
            target_type = (qs.get("target_type") or qs.get("type") or [""])[0]
            self._json(
                200,
                dependency_graph_v1_payload(
                    repo_root=repo_root,
                    task_id=task_id,
                    force_refresh=force,
                    query_type=query_type,
                    query_arg=query_arg,
                    target_type=target_type,
                ),
            )
            return
        if path == "/api/semantic-context-fabric-v1":
            from runtime.context_fabric.api import semantic_context_fabric_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            task_id = (qs.get("task_id") or [""])[0]
            self._json(200, semantic_context_fabric_v1_payload(task_id=task_id))
            return
        if path == "/api/multi-step-planner-v1":
            from runtime.multi_step_planner.api import multi_step_planner_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            goal = (qs.get("goal") or qs.get("goal_tool") or ["pos-run"])[0]
            task_id = (qs.get("task_id") or [""])[0]
            force = (qs.get("force") or ["0"])[0].lower() in ("1", "true", "yes")
            self._json(200, multi_step_planner_v1_payload(goal_tool_id=goal, task_id=task_id, force_refresh=force))
            return
        if path == "/api/runtime-orchestrator-v1":
            from runtime.orchestrator.api import runtime_orchestrator_v1_payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            goal = (qs.get("goal") or qs.get("goal_tool") or ["pos-run"])[0]
            task_id = (qs.get("task_id") or [""])[0]
            self._json(200, runtime_orchestrator_v1_payload(goal_tool_id=goal, task_id=task_id))
            return
        if path == "/api/apple-health":
            from apple_health_mini import apple_health_payload  # noqa: WPS433

            self._json(200, apple_health_payload())
            return
        if path == "/api/mac-health":
            from mac_health_guard import build_report  # noqa: WPS433

            self._json(200, build_report(rescan=False))
            return
        if path == "/api/n8n":
            from n8n_automation import automation_payload  # noqa: WPS433

            self._json(200, automation_payload())
            return
        if path == "/api/n8n/intelligence":
            from n8n_intelligence import handle_intelligence_action  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            self._json(200, handle_intelligence_action({}, query={k: v[0] for k, v in qs.items()}))
            return
        if path == "/api/hub-essentials":
            from hub_essentials_index import hub_essentials_payload  # noqa: WPS433

            self._json(200, hub_essentials_payload(hub_port=PORT))
            return
        if path == "/api/personal-db":
            from personal_db_ops import personal_db_payload  # noqa: WPS433

            self._json(200, personal_db_payload())
            return
        if path in ("/form", "/form/", "/form/index.html"):
            self._serve_static("/form/index.html")
            return
        if path in ("/mail", "/mail/", "/mail-hub", "/mail-hub/"):
            self._serve_static("/mail-hub/index.html")
            return
        if path == "/api/portfolio-mail/v1/integration":
            from portfolio_mail_hub_v1 import integration_status  # noqa: WPS433

            self._json(200, integration_status())
            return
        if path == "/api/portfolio-mail/v1":
            from portfolio_mail_hub_v1 import handle_get  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            self._json(200, handle_get(qs))
            return
        if path == "/api/api-station/terminal/v1":
            from api_station_v1 import handle_terminal_get  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            lines = int((qs.get("lines") or ["120"])[0])
            self._json(200, handle_terminal_get(lines=lines))
            return
        if path == "/api/api-station/v1":
            from api_station_v1 import handle_get  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            app_id = (qs.get("app") or ["worker-hub"])[0]
            flat = {k: v[0] for k, v in qs.items() if v}
            self._json(200, handle_get(app_id=app_id, query=flat))
            return
        if path == "/api/hub-pro-skills/v1":
            from hub_pro_skills_v1 import append_entry, payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            app_id = (qs.get("app") or ["worker_hub"])[0]
            self._json(200, payload(app_id=app_id))
            return
        if path == "/api/founder-ops/v1":
            from founder_ops_v1 import manifest  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            hub = (qs.get("hub") or [None])[0]
            self._json(200, manifest(hub=hub))
            return
        if path == "/api/cloud-workers/v1":
            from cloud_workers_hub_v1 import handle_action, payload  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            if qs.get("probe"):
                self._json(200, handle_action({"action": "probe"}))
                return
            self._json(200, payload())
            return
        if path == "/api/living-system-chain/v1":
            from living_system_chain_validate_v1 import hub_slice, validate_chains  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            if qs.get("full"):
                self._json(200, validate_chains())
                return
            self._json(200, hub_slice())
            return
        if path == "/api/validator-machine/v1":
            from validator_machine_v1 import hub_slice, run_all, run_app  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            if qs.get("run"):
                tier = (qs.get("tier") or ["light"])[0]
                app_id = (qs.get("app") or [None])[0]
                if app_id:
                    self._json(200, run_app(str(app_id), tier=tier))
                else:
                    self._json(200, run_all(tier=tier))
                return
            app_id = (qs.get("app") or [None])[0]
            self._json(200, hub_slice(app_id=app_id))
            return
        if path.startswith("/shared/"):
            self._serve_static(path)
            return
        self._serve_static(path)

    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", 0))
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            body = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            body = {}

        if path in ("/shutdown", "/api/emergency-stop"):
            from emergency_stop import run_emergency_stop  # noqa: WPS433

            result = run_emergency_stop(from_hub=True)
            self._json(200, result)
            import os
            import signal
            import threading
            import time

            def _exit_hub() -> None:
                time.sleep(0.35)
                os.kill(os.getpid(), signal.SIGTERM)

            threading.Thread(target=_exit_hub, daemon=True).start()
            return
        if path == "/api/portfolio-mail/v1/integration":
            from portfolio_mail_hub_v1 import integration_wire  # noqa: WPS433

            row = integration_wire(import_cursor=bool(body.get("import_cursor")))
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/portfolio-mail/v1/send":
            import asyncio

            from portfolio_mail_hub_v1 import handle_post  # noqa: WPS433

            row = asyncio.run(handle_post(body))
            self._json(200 if row.get("ok") else 400, row)
            return
        if path == "/api/api-station/v1":
            from api_station_v1 import handle_post  # noqa: WPS433

            qs = parse_qs(urlparse(self.path).query)
            app_id = (qs.get("app") or ["worker-hub"])[0]
            row = handle_post(app_id=app_id, body=body)
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/hub-pro-skills/v1":
            from hub_pro_skills_v1 import append_entry  # noqa: WPS433

            if str((body or {}).get("action") or "").strip().lower() != "append":
                self._json(400, {"ok": False, "error": "action_required", "hint": "POST { action: append, app_id, agent, summary }"})
                return
            app_id = str((body or {}).get("app_id") or "").strip()
            summary = str((body or {}).get("summary") or "").strip()
            if not app_id or not summary:
                self._json(400, {"ok": False, "error": "app_id_and_summary_required"})
                return
            row = append_entry(
                app_id=app_id,
                agent=str((body or {}).get("agent") or "hub_ui"),
                summary=summary,
                obstacles=(body or {}).get("obstacles") if isinstance((body or {}).get("obstacles"), list) else None,
                fixes=(body or {}).get("fixes") if isinstance((body or {}).get("fixes"), list) else None,
                golden_tips=(body or {}).get("golden_tips") if isinstance((body or {}).get("golden_tips"), list) else None,
                paths=(body or {}).get("paths") if isinstance((body or {}).get("paths"), list) else None,
            )
            self._json(200 if row.get("ok") else 500, row)
            return
        if path == "/api/founder-ops/v1":
            from founder_ops_v1 import run_op  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            op = str((body or {}).get("op") or "").strip()
            payload = (body or {}).get("payload") if isinstance((body or {}).get("payload"), dict) else {}
            if not op:
                self._json(400, {"ok": False, "error": "op_required", "hint": "POST { op: '<id>', payload: {} }"})
                return
            row = run_op(op, payload)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/worker-hub/heal":
            from worker_anti_staleness_heal_v1 import worker_anti_staleness_heal  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            reason = str(body.get("reason") or "founder")
            deep = bool(body.get("full") or body.get("deep"))
            force = bool(body.get("force") or reason in ("founder", "founder-tap", "auto"))
            row = worker_anti_staleness_heal(reason=reason, force=force, deep=deep)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/worker-hub/outbound-coherence-heal/v1":
            from outbound_disk_coherence_heal_v1 import heal as outbound_coherence_heal  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = outbound_coherence_heal(redeliver=not bool(body.get("no_redeliver")))
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/pipeline-node-graph/run/v1":
            from pipeline_node_graph_runner_v1 import run_graph, run_session_tiers  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            tier = str(body.get("tier") or "T3_proof_parallel")
            if tier == "session":
                row = run_session_tiers(dry_run=False)
            else:
                row = run_graph(tier_filter=tier, dry_run=False)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") or row.get("degraded") else 207, row)
            return
        if path == "/api/worker-hub/rooms/run":
            from worker_hub_daily_rooms_v1 import run_rooms  # noqa: WPS433

            room = str(body.get("room") or "both").strip().lower()
            chats = body.get("chats")
            row = run_rooms(room=room, chats=str(chats) if chats else None)
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/worker-hub/commercial/run":
            from commercial_agents_wire_v1 import run_commercial_action  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            action = str(body.get("action") or "").strip()
            row_id = str(body.get("row_id") or "")
            reply_text = str(body.get("reply_text") or "")
            row = run_commercial_action(action, row_id=row_id, reply_text=reply_text)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok", True) and not row.get("error") else 400, row)
            return
        if path == "/api/loop-specialist/tick/v1":
            from loop_specialist_tick_v1 import handle_hub_post  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = handle_hub_post(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/investigator-circle/tick/v1":
            from investigator_circle_run_v1 import handle_hub_post as inv_post  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = inv_post(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/judge-loop/tick/v1":
            from judge_loop_room_v1 import handle_hub_post as judge_post  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = judge_post(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/routing-panel/tick/v1":
            from founder_routing_panel_v1 import run_panel  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = run_panel(write=True)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/w3-founder-review/score/v1":
            from w3_founder_review_v1 import hub_slice, set_sina_read_score  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            account_id = str(body.get("account_id") or "").strip()
            try:
                pct = int(body.get("pct") or 0)
            except (TypeError, ValueError):
                pct = 0
            note = str(body.get("note") or "").strip()
            if not account_id or pct < 0 or pct > 100:
                self._json(400, {"ok": False, "error": "account_id and pct 0–100 required"})
                return
            if pct < 90 and not note:
                self._json(400, {"ok": False, "error": "sina_read score <90 requires note", "upgrade": "U064"})
                return
            try:
                set_sina_read_score(account_id, pct, note=note)
            except SystemExit as exc:
                self._json(400, {"ok": False, "error": str(exc)})
                return
            invalidate_worker_hub_cache()
            self._json(200, {"ok": True, "review": hub_slice(), "account_id": account_id, "pct": pct})
            return
        if path == "/api/w3-founder-review/pack-to/v1":
            from w3_founder_review_v1 import hub_slice, update_pack_to  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            account_id = str(body.get("account_id") or "").strip()
            to_email = str(body.get("to") or body.get("to_email") or "").strip()
            if not account_id or not to_email:
                self._json(400, {"ok": False, "error": "account_id and to required"})
                return
            row = update_pack_to(account_id, to_email)
            if not row.get("ok"):
                code = 409 if row.get("blocked") else 400
                self._json(code, row)
                return
            invalidate_worker_hub_cache()
            self._json(200, {"ok": True, "row": row, "review": hub_slice()})
            return
        if path == "/api/w3-founder-review/export/v1":
            from w3_founder_review_v1 import build_review, export_markdown  # noqa: WPS433

            row = build_review(write=True)
            dest = export_markdown(row)
            self._json(200, {"ok": True, "path": str(dest), "review": row.get("red_summary")})
            return
        if path == "/api/w3-founder-review/reply-log/v1":
            from outbound_reply_log_v1 import log_reply  # noqa: WPS433
            from w3_founder_review_v1 import hub_slice  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            account_id = str(body.get("account_id") or "").strip()
            reply_yn = str(body.get("reply_yn") or body.get("reply") or "").strip()
            note = str(body.get("note") or "")
            if not account_id or not reply_yn:
                self._json(400, {"ok": False, "error": "account_id and reply_yn (Y|N) required"})
                return
            try:
                row = log_reply(account_id, reply_yn, note=note)
            except SystemExit as exc:
                self._json(400, {"ok": False, "error": str(exc)})
                return
            invalidate_worker_hub_cache()
            self._json(200, {"ok": True, "row": row, "review": hub_slice()})
            return
        if path == "/api/disclosure-ladder/tick/v1":
            from disclosure_ladder_v1 import handle_hub_post  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = handle_hub_post(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/mcp-stack/tick/v1":
            from mcp_stack_free_tier_v1 import handle_hub_post  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = handle_hub_post(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/tool-pick/tick/v1":
            from tool_pick_two_phase_v1 import handle_hub_post  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = handle_hub_post(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/plans-unified/tick/v1":
            from plans_unified_upgrade_v1 import handle_hub_post  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = handle_hub_post(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/world-model-plan-check/tick/v1":
            from world_model_plan_check_v1 import handle_hub_post  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = handle_hub_post(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/full-stack-fix-plan/pulse/v1":
            from full_stack_fix_plan_pulse_v1 import handle_hub_post as fix_plan_post  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = fix_plan_post(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/brain/outbound-work-order/v1":
            from brain_outbound_work_order_v1 import handle_hub_post as brain_wo_post  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = brain_wo_post(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/loop-chain/tick/v1":
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = _run_loop_chain_tick(body)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 207, row)
            return
        if path == "/api/fbe/spawn/v1":
            from fbe_spawn_factory_v1 import spawn as fbe_spawn  # noqa: WPS433

            template_id = str(body.get("template_id") or "web-product-factory-v1")
            tenant = str(body.get("tenant") or "wil_ai_design_partner")

            def _local() -> dict:
                return fbe_spawn(template_id=template_id, tenant=tenant)

            row = dispatch_fbe_route(path, body, _local)
            self._json(200 if row.get("ok") else 400, row)
            return
        if path == "/api/fbe/run-bay/v1":
            from fbe_run_bay_v1 import run_bay_job  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            bay_slug = str(body.get("bay_slug") or "sample-bay")
            template_id = str(body.get("template_id") or "web-product-factory-v1")
            tenant = str(body.get("tenant") or "wil_ai_design_partner")
            work_order_id = str(body.get("work_order_id") or "")

            def _local() -> dict:
                return run_bay_job(
                    bay_slug=bay_slug,
                    template_id=template_id,
                    tenant=tenant,
                    work_order_id=work_order_id,
                )

            row = dispatch_fbe_route(path, body, _local)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 400, row)
            return
        if path == "/api/fbe/run-job/v1":
            from fbe_run_job_v1 import run_job  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            bay_slug = str(body.get("bay_slug") or "sample-bay")
            template_id = str(body.get("template_id") or "web-product-factory-v1")
            tenant = str(body.get("tenant") or "wil_ai_design_partner")
            work_order_id = str(body.get("work_order_id") or "")

            def _local() -> dict:
                return run_job(
                    bay_slug=bay_slug,
                    template_id=template_id,
                    tenant=tenant,
                    work_order_id=work_order_id,
                )

            row = dispatch_fbe_route(path, body, _local)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 400, row)
            return
        if path == "/api/fbe/run-exchange/v1":
            from fbe_run_job_v1 import run_job  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            bay_slug = str(body.get("bay_slug") or "trustfield-bay")
            template_id = str(body.get("template_id") or "exchange-factory-v1")
            tenant = str(body.get("tenant") or "trustfield")
            work_order_id = str(body.get("work_order_id") or "")

            def _local() -> dict:
                return run_job(
                    bay_slug=bay_slug,
                    template_id=template_id,
                    tenant=tenant,
                    work_order_id=work_order_id,
                )

            row = dispatch_fbe_route(path, body, _local)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 400, row)
            return
        if path == "/api/fbe/run-forge/v1":
            from fbe_run_job_v1 import run_job  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            bay_slug = str(body.get("bay_slug") or "forge-bay")
            template_id = str(body.get("template_id") or "forge-app-factory-v1")
            tenant = str(body.get("tenant") or "forge")
            work_order_id = str(body.get("work_order_id") or "")
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

            def _local() -> dict:
                return run_job(
                    bay_slug=bay_slug,
                    template_id=template_id,
                    tenant=tenant,
                    work_order_id=work_order_id,
                    forge_context=forge_ctx or None,
                )

            row = dispatch_fbe_route(path, body, _local)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 400, row)
            return
        if path == "/api/cloud-worker/dispatch/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

            plan_id = str(body.get("plan_id") or "")
            dry_run = bool(body.get("dry_run"))
            if not plan_id:
                self._json(400, {"ok": False, "error": "plan_id_required"})
                return
            row = proxy_to_cloud(
                path="/api/cloud-worker/dispatch/v1",
                body={"plan_id": plan_id, "dry_run": dry_run},
                timeout_s=120,
            )
            self._json(200 if row.get("ok") else 502, row)
            return
        if path == "/api/cloud-workers/v1":
            from cloud_workers_hub_v1 import handle_action  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = handle_action(body if isinstance(body, dict) else {})
            if str((body or {}).get("action") or "") in ("proceed", "dispatch"):
                invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 502, row)
            return
        if path == "/api/cloud-forge-run/proceed/v1":
            from hub_cloud_forge_run_proceed_v1 import proceed_from_hub  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            row = proceed_from_hub(body if isinstance(body, dict) else {})
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 502, row)
            return
        if path == "/api/forge/v01/run/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

            row = proxy_to_cloud(path="/api/forge/v01/run/v1", body={}, timeout_s=120)
            self._json(200 if row.get("ok") else 502, row)
            return
        if path == "/api/forge/v02/run/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

            row = proxy_to_cloud(path="/api/forge/v02/run/v1", body=body if isinstance(body, dict) else {}, timeout_s=180)
            self._json(200 if row.get("ok") else 502, row)
            return
        if path == "/api/forge/v02/run-and-implement/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

            row = proxy_to_cloud(
                path="/api/forge/v02/run-and-implement/v1",
                body=body if isinstance(body, dict) else {},
                timeout_s=240,
            )
            self._json(200 if row.get("ok") else 502, row)
            return
        if path == "/api/forge/v02/implement/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

            row = proxy_to_cloud(
                path="/api/forge/v02/implement/v1",
                body=body if isinstance(body, dict) else {},
                timeout_s=180,
            )
            self._json(200 if row.get("ok") else 502, row)
            return
        if path == "/api/forge/v02/drain/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

            row = proxy_to_cloud(
                path="/api/forge/v02/drain/v1",
                body=body if isinstance(body, dict) else {},
                timeout_s=600,
            )
            self._json(200 if row.get("ok") else 502, row)
            return
        if path == "/api/fbe/forge--run/v1":
            from forge__run_v1 import run__forge  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            stack = str(body.get("stack") or "sourcea")
            dry_run = bool(body.get("dry_run") or body.get("dry-run"))
            plan_id = str(body.get("plan_id") or "")
            row = run__forge(stack=stack, dry_run=dry_run, plan_id=plan_id)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 400, row)
            return
        if path == "/api/fbe/run-fleet/v1":
            from fbe_run_fleet_v1 import run_fleet  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            def _local() -> dict:
                return run_fleet()

            row = dispatch_fbe_route(path, body, _local)
            invalidate_worker_hub_cache()
            self._json(200 if row.get("ok") else 400, row)
            return
        if path == "/api/comprehension-loop/v1":
            from fbe_comprehension_bay_v1 import run_comprehension_bay  # noqa: WPS433

            draft = str(body.get("draft") or body.get("text") or "")
            founder_message = str(body.get("founder_message") or "")
            snap = body.get("system_snapshot")
            if snap is None:
                try:
                    from cloud_comprehension_bay_client_v1 import light_system_snapshot  # noqa: WPS433

                    snap = light_system_snapshot()
                except Exception:
                    snap = {}

            fbe_body = {
                **body,
                "job_id": str(body.get("job_id") or __import__("uuid").uuid4()),
                "factory_id": "comprehension-loop-factory-v1",
                "bay_slug": "comprehension-loop-bay",
                "tenant": str(body.get("tenant") or "sourcea"),
                "execution_mode": "CLOUD_ONLY",
                "draft": draft,
                "founder_message": founder_message,
                "system_snapshot": snap,
            }

            variation_key = str(body.get("variation_key") or "").strip() or None

            def _local() -> dict:
                return run_comprehension_bay(
                    draft=draft,
                    founder_message=founder_message,
                    system_snapshot=snap if isinstance(snap, dict) else None,
                    variation_key=variation_key,
                    context_id=str(body.get("context_id") or body.get("job_id") or ""),
                )

            row = dispatch_fbe_route("/api/fbe/comprehension-loop/v1", fbe_body, _local)
            raw = row
            er = row.get("execution_receipt") or {}
            if isinstance(er.get("raw_receipt"), dict):
                raw = er["raw_receipt"]
            slim = {
                "ok": bool(raw.get("ok")),
                "verdict": raw.get("verdict"),
                "config_version": raw.get("config_version"),
                "variation_key": raw.get("variation_key"),
                "meaning_score": raw.get("meaning_score"),
                "escalated": bool(raw.get("escalated")),
                "attempts": raw.get("attempts") or [],
                "for_founder": raw.get("for_founder") or {},
                "for_agent": raw.get("for_agent") or {},
                "one_line": raw.get("one_line") or "",
                "execution_plane": raw.get("execution_plane") or row.get("execution_plane") or "headless_cloud",
                "proxied": row.get("proxied", True),
                "bay_slug": "comprehension-loop-bay",
            }
            code = 200 if slim.get("verdict") else (200 if slim.get("ok") else 422)
            self._json(code, slim)
            return
        if path == "/api/comprehension-eval-batch/v1":
            from fbe.lib.hub_cloud_proxy_v1 import proxy_to_cloud  # noqa: WPS433

            vk = str(body.get("variation_key") or "").strip() or None
            proxy_body = {"variation_key": vk} if vk else {}
            row = proxy_to_cloud(
                path="/api/fbe/comprehension-eval-batch/v1",
                body=proxy_body,
                timeout_s=180,
            )
            self._json(200 if row.get("ok") else 422, row)
            return
        if path == "/api/fbe/actions/v1":
            from fbe_actions_v1 import run_action  # noqa: WPS433

            action = str(body.get("action") or "").strip()
            template_id = str(body.get("template_id") or "web-product-factory-v1")
            row = run_action(action, template_id=template_id)
            self._json(200 if row.get("ok") else 400, row)
            return
        if path == "/refresh":
            mode = str(body.get("mode") or "light").strip().lower()
            if mode == "full":
                try:
                    import urllib.request

                    with urllib.request.urlopen("http://127.0.0.1:13030/health", timeout=2) as resp:
                        worker_ok = resp.status == 200
                except Exception:
                    worker_ok = False
                if worker_ok:
                    from hub_queue_lib_v1 import enqueue_rebuild  # noqa: WPS433

                    enqueue_rebuild(source="refresh", run_refresh=True)
                    self._json(
                        202,
                        {
                            "ok": True,
                            "queued": True,
                            "mode": "full",
                            "message": "Full rebuild queued — UI updates via SSE when worker finishes",
                        },
                    )
                    return
                payload = hub_after_mutation(run_refresh_scripts=True, write_html=True)
                self._json(
                    200,
                    {
                        "ok": True,
                        "mode": "full",
                        "built_at": payload.get("built_at"),
                        "refresh_steps": payload.get("refresh_log") or [],
                        "data": payload,
                    },
                )
                return
            from sina_command_lib import hub_light_refresh  # noqa: WPS433
            from worker_hub_v1 import invalidate_worker_hub_cache  # noqa: WPS433

            shell = hub_light_refresh()
            invalidate_worker_hub_cache()
            self._json(
                200,
                {
                    "ok": True,
                    "mode": "light",
                    "built_at": shell.get("built_at"),
                    "generation_id": shell.get("generation_id"),
                    "refresh_steps": [{"ok": True, "label": "light-align"}],
                },
            )
            return
            return
        if path == "/open":
            rel = body.get("path") or parse_qs(urlparse(self.path).query).get("path", [""])[0]
            if not rel:
                self._json(400, {"error": "path required"})
                return
            target = Path(rel).expanduser()
            if not target.is_absolute():
                target = (SA / rel).resolve()
            else:
                target = target.resolve()
            allowed = any(
                target == root.resolve() or root.resolve() in target.parents
                for root in ALLOWED_OPEN_ROOTS
            )
            if not allowed:
                self._json(403, {"error": "path not allowed"})
                return
            if not target.exists():
                self._json(404, {"error": "not found"})
                return
            subprocess.run(["open", str(target)], check=False)
            self._json(200, {"ok": True, "opened": str(target)})
            return
        if path == "/api/live-founder-decision-form-v1":
            action = (body.get("action") or "").strip().lower()
            if action == "submit":
                if not body.get("founder_submit"):
                    self._json(
                        403,
                        {
                            "ok": False,
                            "error": "FOUNDER_SUBMIT_REQUIRED",
                            "law": "INCIDENT-037 — only founder Hub Submit with founder_submit:true",
                        },
                    )
                    return
                from hub_form_submit_v1 import submit_founder_picks  # noqa: WPS433

                overrides = body.get("picks") if isinstance(body.get("picks"), dict) else None
                comments = body.get("founder_comments") or body.get("comments")
                if not isinstance(comments, dict):
                    comments = None
                partial = bool(body.get("partial_batch") or body.get("batch_submit"))
                try:
                    result = submit_founder_picks(
                        overrides=overrides,
                        comments=comments,
                        cascade_hub=False,
                        partial_batch=partial,
                        actor="founder",
                        channel="hub_browser",
                        background_wire=False,
                    )
                except Exception as exc:
                    self._json(
                        500,
                        {
                            "ok": False,
                            "error": "FORM_SUBMIT_EXCEPTION",
                            "detail": str(exc)[:240],
                        },
                    )
                    return
                code = 200 if result.get("ok") else 500
                result["cascade"] = result.get("cascade") or "disk_now·wire_background"
                self._json(code, result)

                def _form_post_response_wire() -> None:
                    try:
                        from hub_form_submit_v1 import _background_form_wire  # noqa: WPS433

                        _background_form_wire(reason="hub-form-submit")
                        warm_hub_cache_from_disk()
                    except Exception:
                        pass

                threading.Thread(target=_form_post_response_wire, daemon=True, name="form-post-wire").start()
                return
            self._json(400, {"ok": False, "error": "action required: submit"})
            return
        if path == "/api/rule":
            rel = body.get("path")
            content = body.get("content")
            if not rel or content is None:
                self._json(400, {"error": "path and content required"})
                return
            result = write_rule(rel, content)
            if result.get("ok"):
                payload = hub_after_mutation(run_refresh_scripts=True)
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/apps/launch":
            app_id = body.get("id")
            if not app_id:
                self._json(400, {"error": "id required"})
                return
            self._json(200, launch_mini_app(app_id))
            return
        if path == "/api/apps/open":
            app_id = body.get("id")
            if not app_id:
                self._json(400, {"error": "id required"})
                return
            self._json(200, open_mini_app(app_id))
            return
        if path == "/api/dispatch-policy-v1":
            from runtime.dispatch_policy.api import dispatch_policy_v1_post  # noqa: WPS433

            self._json(200, dispatch_policy_v1_post(body))
            return
        if path == "/api/runtime-wrapper/v1/dispatch":
            from sourcea_runtime_wrapper_v1 import governed_dispatch  # noqa: WPS433

            action = str(body.get("action") or "")
            if not action:
                self._json(400, {"ok": False, "error": "action required"})
                return
            row = governed_dispatch(
                action=action,
                context=body.get("context") if isinstance(body.get("context"), dict) else {},
                profile_name=str(body.get("profile") or "") or None,
                execute=not bool(body.get("dry_run")),
                dry_run=bool(body.get("dry_run")),
            )
            self._json(200 if row.get("ok") else 403, row)
            return
        if path == "/api/user-workspace-signals-v1":
            from pre_llm.user_signals.api import user_workspace_signals_v1_payload  # noqa: WPS433

            self._json(200, user_workspace_signals_v1_payload(body))
            return
        if path == "/api/execution-state-v1":
            from autonomy_stack_api import execution_state_v1_post  # noqa: WPS433

            self._json(200, execution_state_v1_post(body))
            return
        if path in ("/api/stop-goal1-auto-run", "/api/stop-goal1-loop"):
            self._json(200, run_branch_action("founder-goal1-autorun-stop"))
            return
        if path == "/api/goal1-autorun-start":
            self._json(200, run_branch_action("founder-goal1-autorun-start"))
            return
        if path == "/api/goal1-autorun-stop":
            self._json(200, run_branch_action("founder-goal1-autorun-stop"))
            return
        if path in ("/api/run-goal1-auto-run", "/api/run-goal1-auto-loop"):
            import subprocess
            import sys as _sys

            from sina_command_lib import SOURCE_A, build_payload  # noqa: WPS433

            turns = int(body.get("turns") or 10)
            proc = subprocess.run(
                [
                    _sys.executable,
                    str(SOURCE_A / "scripts" / "brain_run_loop_v1.py"),
                    "--turns",
                    str(turns),
                ],
                cwd=str(SOURCE_A),
                capture_output=True,
                text=True,
                timeout=120,
            )
            try:
                trace = json.loads(proc.stdout) if proc.stdout.strip() else {}
            except json.JSONDecodeError:
                trace = {"ok": False, "raw": proc.stdout, "stderr": proc.stderr}
            from sina_command_lib import goal1_auto_run_payload, goal1_hub_status_bundle  # noqa: WPS433

            payload = build_payload(run_refresh_scripts=False)
            g1 = goal1_auto_run_payload()
            inject = next((s for s in (trace.get("steps") or []) if s.get("id") == "inject"), {})
            self._json(
                200 if trace.get("ok") else 400,
                {
                    "ok": trace.get("ok", False),
                    "message": trace.get("status") or inject.get("error"),
                    "pid": trace.get("pid"),
                    "log_path": trace.get("log_path"),
                    "background": True,
                    "turns": turns,
                    "brain_loop_trace": trace,
                    "output": (proc.stdout or proc.stderr or "")[:8000],
                    **goal1_hub_status_bundle(g1),
                    "turn_progress": g1.get("turn_progress"),
                    "last_turn_proof": g1.get("last_turn_proof"),
                    "data": payload,
                },
            )
            return
        if path == "/api/run-goal1-batch":
            import subprocess
            import sys as _sys

            from sina_command_lib import SOURCE_A, build_payload  # noqa: WPS433

            batch_size = int(body.get("batch_size") or 5)
            max_batches = int(body.get("max_batches") or 6)
            subprocess.run(
                [_sys.executable, str(SOURCE_A / "scripts" / "stop_goal1_auto_run_v1.py")],
                cwd=str(SOURCE_A),
                capture_output=True,
                timeout=30,
            )
            log_path = Path.home() / ".sina" / "goal1-worker-batch-latest.log"
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("w", encoding="utf-8") as logfh:
                logfh.write(f"[hub] starting batch size={batch_size} max_batches={max_batches}\n")
                proc = subprocess.Popen(
                    [
                        _sys.executable,
                        str(SOURCE_A / "scripts" / "goal1_worker_batch_loop_v1.py"),
                        "--batch-size",
                        str(batch_size),
                        "--max-batches",
                        str(max_batches),
                    ],
                    cwd=str(SOURCE_A),
                    stdout=logfh,
                    stderr=subprocess.STDOUT,
                    start_new_session=True,
                )
            import time

            time.sleep(10)
            verify = subprocess.run(
                ["pgrep", "-f", "goal1_worker_batch_loop_v1.py"],
                capture_output=True,
                text=True,
                timeout=5,
            )
            child_alive = bool((verify.stdout or "").strip())
            payload = build_payload(run_refresh_scripts=False)
            if not child_alive:
                self._json(
                    400,
                    {
                        "ok": False,
                        "message": f"Batch child died within 10s (pid {proc.pid}) — see Batch log",
                        "pid": proc.pid,
                        "log_path": str(log_path),
                        "data": payload,
                    },
                )
                return
            self._json(
                200,
                {
                    "ok": True,
                    "message": f"Worker batch STARTED pid {proc.pid} — verified alive @10s",
                    "pid": proc.pid,
                    "log_path": str(log_path),
                    "background": True,
                    "child_verified": True,
                    "data": payload,
                },
            )
            return
        if path == "/api/action":
            action_id = body.get("id")
            if not action_id:
                self._json(400, {"error": "id required"})
                return
            try:
                result = run_branch_action(action_id)
                if result.get("ok") and not result.get("data"):
                    canvas_surface = result.get("surface") if isinstance(result.get("surface"), str) else None
                    if action_id not in ("founder-open-integrity-form", "founder-open-m1-canvas"):
                        from sina_command_lib import hub_light_refresh  # noqa: WPS433

                        result["hub_projection"] = hub_light_refresh()
                    if canvas_surface:
                        result["canvas_surface"] = canvas_surface
                    elif result.get("hub_projection"):
                        result["surface"] = result["hub_projection"]
                self._json(200 if result.get("ok") else 400, result)
            except Exception as exc:
                import traceback

                traceback.print_exc()
                self._json(500, {"ok": False, "error": str(exc), "action_id": action_id})
            return
        if path == "/todo/done":
            todo_id = body.get("id")
            if not todo_id:
                self._json(400, {"error": "id required"})
                return
            result = mark_todo_done(todo_id)
            if result.get("ok"):
                payload = hub_after_mutation(run_refresh_scripts=True)
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/notes":
            text = body.get("text", "")
            category = body.get("category", "update")
            result = add_founder_note(text, category=category)
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/notes/done":
            note_id = body.get("id")
            if not note_id:
                self._json(400, {"error": "id required"})
                return
            result = set_note_status(note_id, "done")
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/ai/advisory":
            from sina_ai_advisory import run_advisory  # noqa: WPS433

            payload = get_hub_payload()
            result = run_advisory(payload=payload)
            if result.get("ok"):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/prompt-queue":
            result = prompt_queue_action(body)
            if result.get("ok"):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/prompt-direction":
            payload = get_hub_payload()
            result = prompt_direction_action(body, payload=payload)
            if result.get("ok"):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/agent-loop":
            payload = get_hub_payload()
            result = agent_loop_action(body, payload=payload)
            if result.get("ok") and body.get("action") in (
                "start",
                "response",
                "activate_pack",
                "activate_devbridge_pack",
                "select_workspace",
                "set_seeds",
            ):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/founder-cursor-send":
            from founder_cursor_send import handle_founder_cursor_send  # noqa: WPS433

            result = handle_founder_cursor_send(body)
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/site-guide":
            from site_guide import answer_site_question  # noqa: WPS433

            payload = get_hub_payload()
            result = answer_site_question(body.get("question") or "", payload)
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/advisor/chat":
            payload = get_hub_payload()
            result = handle_advisor_action(body, payload=payload)
            if result.get("ok") and body.get("action") == "chat":
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/semej":
            result = handle_semej_action(body)
            if result.get("ok") and body.get("action") in ("start", "response", "capture_now", "skip_provider"):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/commitments":
            from founder_commitments import commitments_payload, handle_commitments_action  # noqa: WPS433

            payload = get_hub_payload()
            ctx = _commitments_context(payload)
            result = handle_commitments_action(body, hub_context=ctx)
            if result.get("ok") and body.get("action") in (
                "add",
                "done",
                "pin",
                "dismiss_workstream",
            ):
                payload = hub_after_mutation()
                result["data"] = payload
            elif body.get("action") in ("list", "status"):
                result = {**result, **commitments_payload(**ctx)}
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/audit-backlog":
            from command_audit_backlog import audit_backlog_payload, handle_audit_action  # noqa: WPS433

            result = handle_audit_action(body)
            if result.get("ok") and body.get("action") == "set_status":
                payload = hub_after_mutation()
                result["data"] = payload
            elif body.get("action") in ("list", ""):
                result = {**result, **audit_backlog_payload()}
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/agent-review":
            from agent_command_reviews import handle_review_action, reviews_payload  # noqa: WPS433

            result = handle_review_action(body)
            if result.get("ok") and body.get("action") in ("set_status", "submit"):
                payload = hub_after_mutation()
                result["data"] = payload
            elif body.get("action") in ("list", ""):
                result = {**result, **reviews_payload()}
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/agent-workspaces":
            from agent_private_workspaces import handle_workspace_action, workspaces_payload  # noqa: WPS433

            result = handle_workspace_action(body)
            if result.get("ok") and body.get("action") == "ensure":
                payload = hub_after_mutation()
                result["data"] = payload
            elif body.get("action") in ("list", ""):
                result = {**result, **workspaces_payload()}
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/workspace-vault":
            from agent_workspace_vault import handle_vault_action  # noqa: WPS433

            result = handle_vault_action(body)
            if result.get("ok") and body.get("action") in ("deposit", "register_ref", "log_activity", "ensure"):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/workspace-mirror":
            from agent_workspace_mirror import handle_mirror_action  # noqa: WPS433

            result = handle_mirror_action(body)
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/agent-scoreboard":
            from agent_scoreboard import handle_scoreboard_action  # noqa: WPS433

            result = handle_scoreboard_action(body)
            if result.get("ok") and body.get("action") in ("submit_report", "verify", "unverify"):
                payload = hub_after_mutation()
                result["scoreboard"] = payload.get("agent_scoreboard")
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/essay-discourse":
            from agent_essay_discourse import handle_essay_action  # noqa: WPS433

            result = handle_essay_action(body)
            if result.get("ok") and body.get("action") in ("submit_essay", "mark_best"):
                payload = hub_after_mutation()
                result["essay_discourse"] = payload.get("essay_discourse")
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/agent-research":
            from agent_research_pipeline import handle_action as research_action  # noqa: WPS433

            result = research_action(body)
            if result.get("ok") and body.get("action") in (
                "submit",
                "brainstorm",
                "evaluate",
                "promote",
                "archive",
            ):
                payload = hub_after_mutation()
                result["agent_research_pipeline"] = payload.get("agent_research_pipeline")
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/incident-room":
            from agent_incident_system import handle_incident_room_action, incident_room_payload  # noqa: WPS433

            result = handle_incident_room_action(body)
            if result.get("ok") and body.get("action") not in ("list", ""):
                payload = hub_after_mutation()
                result["data"] = payload
            elif body.get("action") in ("list", ""):
                aid = body.get("agent_id") or body.get("id")
                result = {**result, **incident_room_payload(aid or None)}
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/conflict-room":
            from agent_conflict_room import conflict_room_payload, handle_conflict_room_action  # noqa: WPS433

            result = handle_conflict_room_action(body)
            if result.get("ok") and body.get("action") not in ("list", ""):
                payload = hub_after_mutation()
                result["data"] = payload
            elif body.get("action") in ("list", ""):
                aid = body.get("agent_id") or body.get("id")
                result = {**result, **conflict_room_payload(aid or None)}
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/founder-requests":
            from founder_request_tracker import handle_action  # noqa: WPS433

            result = handle_action(body)
            if result.get("ok") and body.get("action") in ("register", "update"):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/founder-advisor-discussion":
            from founder_advisor_discussion_v1 import handle_action  # noqa: WPS433

            result = handle_action(body)
            if result.get("ok") and body.get("action") in ("update_decision", "set_notes", "reopen"):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/order-guardian":
            from task_orders_guardian import handle_action  # noqa: WPS433

            hub = get_hub_payload()
            result = handle_action(body, hub)
            if result.get("ok") and body.get("action") in ("register", "update", "refresh_advisory"):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/founder-agent-guide":
            from founder_agent_use_guide import handle_action  # noqa: WPS433

            hub = get_hub_payload()
            result = handle_action(body, hub)
            if result.get("ok") and body.get("action") in ("want", "unwant", "done", "reset_priorities"):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/governance-drift":
            from governance_drift_engine import handle_drift_action  # noqa: WPS433

            result = handle_drift_action(body)
            if result.get("ok") and body.get("action") in ("run", "refresh", "report"):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        if path == "/api/governance-unify":
            from agent_governance_unification import handle_unification_action  # noqa: WPS433

            unify_result = handle_unification_action(body)
            self._json(200 if unify_result.get("ok", True) else 400, unify_result)
            return
        if path == "/api/council-room":
            from agent_council_room import council_room_payload, handle_post  # noqa: WPS433
            from agent_system_unified import handle_unified_action, system_unified_payload  # noqa: WPS433

            action = (body.get("action") or "list").strip().lower()
            if action == "add_directive":
                result = handle_unified_action(body)
                if result.get("ok"):
                    payload = hub_after_mutation()
                    result["system_unified"] = payload.get("system_unified") or system_unified_payload(hub_payload=payload)
                    result["room"] = payload.get("council_room") or council_room_payload()
            elif action in ("list", ""):
                result = council_room_payload()
                result["system_unified"] = system_unified_payload()
            else:
                result = handle_post(body)
                if result.get("ok"):
                    result["system_unified"] = system_unified_payload()
            self._json(200 if result.get("ok", True) else 400, result)
            return
        if path == "/api/apple-health":
            from apple_health_mini import handle_action  # noqa: WPS433

            self._json(200, handle_action(body))
            return
        if path == "/api/mac-health":
            from mac_health_guard import handle_action  # noqa: WPS433

            self._json(200, handle_action(body))
            return
        if path == "/api/personal-db":
            from personal_db_ops import handle_action  # noqa: WPS433

            self._json(200, handle_action(body))
            return
        if path == "/api/n8n/intelligence":
            from n8n_intelligence import handle_intelligence_action  # noqa: WPS433

            self._json(200, handle_intelligence_action(body))
            return
        if path == "/api/brain/chat/v1":
            from sourcea_brain_chat_v1 import handle_chat  # noqa: WPS433

            row = handle_chat(body)
            self._json(200 if row.get("ok") else 503, row)
            return
        if path == "/api/intelligence-circle":
            from intelligence_circle import handle_circle_action  # noqa: WPS433

            action = (body.get("action") or "status").strip().lower()
            if action in ("clear_session", "clear_advisor", "clear_maintainer"):
                result = handle_circle_action(body, hub_payload=None)
                self._json(200 if result.get("ok") else 400, result)
                return
            warm_hub_cache_from_disk()
            payload = get_hub_payload()
            result = handle_circle_action(body, hub_payload=payload)
            if result.get("ok") and action in (
                "chat",
                "talk",
                "brief",
                "set_provider",
                "set_agent_enabled",
                "toggle_agent",
                "agent_reply",
                "select_agent",
            ):
                payload = hub_after_mutation()
                result["data"] = payload
            self._json(200 if result.get("ok") else 400, result)
            return
        self._json(404, {"error": "not found"})

    def _retired_redirect(self) -> None:
        """ASF_RETIRE_SINA_COMMAND_FOREVER — monolith paths must not serve."""
        self.send_response(301)
        self.send_header("Location", "/")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _serve_static(self, path: str) -> None:
        if (
            path.startswith("/legacy")
            or path.startswith("/oldhub")
            or path == "/index.html"
            or path.startswith("/assets/")
        ):
            self._retired_redirect()
            return
        if path in ("", "/"):
            path = "/worker-hub/index.html"
        elif path in ("/machines", "/machines/"):
            path = "/machines/index.html"
        elif path in ("/cloud-workers", "/cloud-workers/"):
            path = "/cloud-workers/index.html"
        rel = unquote(path.lstrip("/"))
        file_path = (PANEL_DIR / rel).resolve()
        root = PANEL_DIR.resolve()
        if root != file_path and root not in file_path.parents:
            self.send_error(403)
            return
        if file_path.is_dir():
            file_path = file_path / "index.html"
        if not file_path.is_file():
            self.send_error(404)
            return
        ctype, _ = mimetypes.guess_type(str(file_path))
        if not ctype:
            ctype = "application/octet-stream"
        data = file_path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        if str(file_path).endswith(".html"):
            self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            self.wfile.write(data)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def _handle_live_sse(self) -> None:
        import time

        from hub_live_events_lib_v1 import append_live_event, tail_events  # noqa: WPS433

        self.protocol_version = "HTTP/1.1"
        self.send_response(200)
        cors_headers(self)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Connection", "keep-alive")
        self.send_header("X-Accel-Buffering", "no")
        self.end_headers()
        offset = 0
        try:
            now = time.time()
            connect = json.dumps({"type": "live.connect", "ts": now}, ensure_ascii=False)
            hb = json.dumps({"type": "live.heartbeat", "ts": now}, ensure_ascii=False)
            self.wfile.write(f"data: {connect}\n\n".encode("utf-8"))
            self.wfile.write(f"data: {hb}\n\n".encode("utf-8"))
            self.wfile.flush()
            append_live_event("live.connect", {"client": "hub"})
            last_hb = now
            while True:
                events, offset = tail_events(since_offset=offset, max_lines=20)
                for evt in events:
                    payload = json.dumps(evt, ensure_ascii=False)
                    self.wfile.write(f"data: {payload}\n\n".encode("utf-8"))
                if events:
                    self.wfile.flush()
                now = time.time()
                if now - last_hb >= 15:
                    hb = json.dumps({"type": "live.heartbeat", "ts": now}, ensure_ascii=False)
                    self.wfile.write(f"data: {hb}\n\n".encode("utf-8"))
                    self.wfile.flush()
                    last_hb = now
                time.sleep(0.5)
        except (BrokenPipeError, ConnectionResetError, OSError):
            pass

    def _json(self, code: int, obj: dict) -> None:
        body = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        cors_headers(self)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        try:
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError):
            pass


def _bootstrap_vault_env() -> None:
    """Load ~/.sina/secrets.env into os.environ so OpenRouter model/key match vault."""
    vault = Path.home() / ".sina" / "secrets.env"
    if not vault.is_file():
        return
    for line in vault.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, _, v = line.partition("=")
        k = k.strip()
        if k.startswith("OPENROUTER_") and k not in os.environ:
            os.environ[k] = v.strip().strip('"').strip("'")


def main() -> None:
    _bootstrap_vault_env()
    if not PANEL_DIR.is_dir():
        print(f"Missing panel dir: {PANEL_DIR}", file=sys.stderr)
        sys.exit(1)
    # Bind immediately — warm cache from disk; never block launch on full rebuild.
    warm_hub_cache_from_disk()
    data_file = PANEL_DIR / "command-data.json"
    if not data_file.is_file():
        hub_after_mutation(write_html=True)
    server = ThreadingHTTPServer(("127.0.0.1", PORT), SinaCommandHandler)
    print(f"Hub → http://127.0.0.1:{PORT}/", flush=True)
    print("  UI + API unified — use Refresh for live rebuild", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
