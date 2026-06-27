#!/usr/bin/env python3
"""GET /api/worker-hub/v1 — single slim payload for Worker Hub (no monolith)."""
from __future__ import annotations

import json
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCHEMA = "worker-hub-v1"
API_PATH = "/api/worker-hub/v1"
EXTENDED_SCHEMA = "worker-hub-extended-v1"
EXTENDED_API_PATH = "/api/worker-hub/extended/v1"

POLICY_LINKS = (
    {"id": "super-fast", "label": "Super Fast Hub law", "path": "SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md"},
    {"id": "layer-stack", "label": "Agentic layer stack", "path": "SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md"},
    {"id": "no-fake", "label": "No fake progress", "path": "SOURCEA_NO_FAKE_PROGRESS_ENTERPRISE_SHIP_LOCKED_v1.md"},
    {"id": "asf-100", "label": "ASF 100 next plans", "path": "brain-os/system/ASF_100_NEXT_PLANS_ENTERPRISE_SHIP_LOCKED_v1.md"},
    {"id": "no-rebuild", "label": "No hub rebuild stuck", "path": "AGENT_NO_HUB_REBUILD_STUCK_LOCKED_v1.md"},
    {"id": "anti-stale", "label": "Anti-staleness plan", "path": "SOURCEA_ANTI_STALENESS_MACHINE_ENFORCEMENT_PLAN_LOCKED_v1.md"},
    {"id": "no-terminal", "label": "No Terminal (founder law)", "path": "SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md"},
)

_CACHE: dict = {"at": 0.0, "payload": None}
_CACHE_TTL = 15.0
_BUILD_LOCK = threading.Lock()
_DEBUG_LOG = ROOT / ".cursor" / "debug-baabac.log"


def _dbg_e2e(*, hypothesis_id: str, location: str, message: str, data: dict | None = None) -> None:
    # #region agent log
    try:
        payload = {
            "sessionId": "baabac",
            "runId": "post-fix",
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data or {},
            "timestamp": int(time.time() * 1000),
        }
        _DEBUG_LOG.parent.mkdir(parents=True, exist_ok=True)
        with _DEBUG_LOG.open("a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except OSError:
        pass
    # #endregion


def _cache_hit(*, skip_cache: bool) -> dict | None:
    if skip_cache:
        return None
    now = time.monotonic()
    cached = _CACHE.get("payload")
    cache_at = float(_CACHE.get("at") or 0)
    if cached and cache_at and (now - cache_at) < _CACHE_TTL:
        return cached
    return None


def invalidate_worker_hub_cache() -> None:
    _CACHE["at"] = 0.0
    _CACHE["payload"] = None


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _live_form_slice() -> dict:
    try:
        from form_official_canvas_route_v1 import hub_canvas_target  # noqa: WPS433
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        form = live_form_payload()
        route = hub_canvas_target()
        oq = int(form.get("open_questions_count") or 0)
        open_ids = list(route.get("open_pick_ids_head") or [])
        if not open_ids:
            open_ids = [q.get("id") for q in (form.get("open_questions") or [])[:5] if q.get("id")]
        if not open_ids:
            open_ids = list(form.get("open_remaining_ids") or [])[:5]
        return {
            "open_questions_count": oq,
            "open_pick_ids": open_ids,
            "awaiting_founder_picks": bool(form.get("awaiting_founder_picks")),
            "form_clear": oq == 0,
            "form_url": route.get("form_api") or "/api/live-founder-decision-form-v1",
            "form_page_url": route.get("form_page_url") or "http://127.0.0.1:13020/form/",
            "canvas_action": route.get("form_action_id") or "founder-open-integrity-form",
            "canvas_surface": route.get("surface"),
            "canvas_path": route.get("path"),
            "form_line": route.get("form_line"),
            "form_headline": route.get("form_headline") or form.get("form_headline"),
            "founder_head_card": route.get("founder_head_card") or form.get("founder_head_card"),
            "canvas_button_label": route.get("button_label"),
            "hub_url": route.get("hub_url") or "http://127.0.0.1:13020/",
            "h2_machines_url": route.get("h2_machines_url") or "http://127.0.0.1:13020/machines/",
            "form_hub_line": route.get("form_hub_line") or "",
            "open_canvas_hint": route.get("open_canvas_hint") or "",
        }
    except Exception:
        return {
            "open_questions_count": 0,
            "open_pick_ids": [],
            "awaiting_founder_picks": False,
            "form_clear": True,
            "form_url": "/api/live-founder-decision-form-v1",
            "canvas_action": "founder-open-integrity-form",
            "canvas_button_label": "Open Form (M1 Canvas)",
        }


def _ecosystem_mac_health_slice(*, hub_boot: dict | None = None) -> dict:
    try:
        from hub_ecosystem_slice_v1 import hub_slice  # noqa: WPS433

        return hub_slice(write_receipt=True, hub_boot=hub_boot)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "hub-ecosystem-slice-v1"}


def _mac_health_live_slice() -> dict[str, Any]:
    bridge_path = Path.home() / ".sina" / "mac-health-h1-bridge-v1.json"
    if bridge_path.is_file():
        try:
            return json.loads(bridge_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            pass
    try:
        from mac_health_live_v1 import build_live_snapshot  # noqa: WPS433

        return build_live_snapshot(sync_h1=False, side_effects=False)
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _upgrade_slice() -> dict:
    """H1 upgrade block — disk receipts only (no 9MB hero)."""
    sina = Path.home() / ".sina"
    n8n = {}
    n8n_path = sina / "governance-n8n-openrouter-wire-v1.json"
    if n8n_path.is_file():
        try:
            n8n = json.loads(n8n_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            n8n = {}
    h2 = {}
    h2_path = sina / "h2-pending-registry-v1.json"
    if h2_path.is_file():
        try:
            h2 = json.loads(h2_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            h2 = {}
    return {
        "hub_edition": "super-fast-v1.2",
        "daily_url": "/",
        "h2_machines_url": "/machines/",
        "layer_stack": "Brain(1) · Gov(2) · Commercial(3) · Brief(4) → Worker · R2 · M2 · M3",
        "n8n_wired": bool(n8n.get("ok")),
        "n8n_running": bool(n8n.get("n8n_running")),
        "openrouter_gate": (n8n.get("openrouter") or {}).get("gate_mode", "shadow"),
        "h2_pending_count": len((h2.get("next_phase") or [])) + len((h2.get("ops_blocker") or [])),
    }


def _outbound_factory_upgrade_slice() -> dict:
    try:
        from outbound_factory_upgrade_pulse_v1 import hub_slice  # noqa: WPS433

        return hub_slice(refresh=False)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-outbound-factory-upgrade-v1"}


def _loop_specialist_slice() -> dict:
    try:
        from loop_specialist_tick_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-loop-specialist-v1"}


def _investigator_room_slice() -> dict:
    try:
        from investigator_circle_run_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-investigator-room-v1"}


def _judge_room_slice() -> dict:
    try:
        from judge_loop_room_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-judge-room-v1"}


def _routing_panel_slice() -> dict:
    try:
        from founder_routing_panel_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-routing-panel-v1"}


def _disclosure_ladder_slice() -> dict:
    try:
        from disclosure_ladder_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-disclosure-ladder-v1"}


def _mcp_stack_slice() -> dict:
    try:
        from mcp_stack_free_tier_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-mcp-stack-v1"}


def _tool_pick_slice() -> dict:
    try:
        from tool_pick_two_phase_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-tool-pick-v1"}


def _behavior_settings_slice() -> dict:
    try:
        from agent_behavior_settings_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-agent-behavior-v1"}


def _factory_cost_intelligence_slice() -> dict:
    try:
        from factory_cost_intelligence_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-factory-cost-intelligence-v1"}


def _anti_theater_slice() -> dict:
    try:
        from anti_theater_validator_loop_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-anti-theater-loop-v1"}


def _plans_unified_slice() -> dict:
    try:
        from plans_unified_upgrade_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-plans-unified-v1"}


def _cloud_forge_run_proceed_slice() -> dict:
    try:
        from hub_cloud_forge_run_proceed_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc)[:120], "ssot": "data/hub-cloud-forge-run-proceed-v1.json"}


def _world_model_slice() -> dict:
    try:
        from world_model_plan_check_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-world-model-v1"}


def _phase0_slice() -> dict:
    try:
        from phase0_freemium_sandbox_pulse_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-phase0-reference-v1"}


def _rrl_slice() -> dict:
    try:
        from response_reality_layer_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-rrl-v1"}


def _full_stack_fix_plan_slice() -> dict:
    try:
        from full_stack_fix_plan_pulse_v1 import hub_slice  # noqa: WPS433

        return hub_slice(refresh=False)
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-full-stack-fix-plan-v1"}


def _commercial_command_slice() -> dict:
    try:
        from commercial_command_pulse_v1 import hub_slice  # noqa: WPS433

        return hub_slice()
    except Exception as exc:
        return {"ok": False, "error": str(exc), "schema": "worker-hub-commercial-command-v1"}


def _fast_worker_slices() -> dict:
    """Disk-fast path — never subprocess program-1000 --write on poll."""
    from hub_sync_slim_v1 import ensure_shell_generation_id, read_shell_disk  # noqa: WPS433
    from factory_control_v1 import load_factory_now  # noqa: WPS433
    from worker_drain_lib import healthy_queue_status  # noqa: WPS433
    from worker_inject_lib import inbox_status  # noqa: WPS433

    shell = read_shell_disk()
    fn = load_factory_now()
    queue = healthy_queue_status()
    inbox = inbox_status()
    kill = bool(fn.get("kill_flag"))
    mode = str(fn.get("mode") or "RUN")
    freeze_status = "FREEZE" if kill or mode == "FREEZE" else mode
    p0 = ((shell.get("command_center") or {}).get("founder") or {}).get("p0") or {}
    form_live = _live_form_slice()
    form_pending = int(form_live.get("open_questions_count") or 0)
    sa = str(queue.get("sa_id") or inbox.get("sa_id") or "—")
    role = str(queue.get("queue_role") or "—")
    # H1: slim line only — no monolith ops_cards / W3-APPROVE bleed (FORM_OFFICIAL for picks)
    if form_pending > 0:
        btn = (form_live.get("canvas_button_label") or "Open Form").replace("Open ", "")
        if form_pending >= 100:
            p0_next = f"URGENT · Form {form_pending}/100 FULL — fill M1 Canvas NOW"
        elif form_pending >= 90:
            p0_next = f"Form {form_pending}/100 — fill soon · tap {btn}"
        else:
            p0_next = f"Form · {form_pending} open PICK(s) — tap {btn}"
    elif freeze_status == "FREEZE":
        p0_next = f"Auto Runtime specialist · ASF resume Cloud Forge Run · queue {sa} · {role}"
    else:
        p0_next = f"Auto Runtime · Worker chat · {sa} · {role}"

    executor_busy = bool((inbox.get("meta") or {}).get("busy"))
    unified_state = str(fn.get("autorun_state") or fn.get("state") or "ready")

    return {
        "shell": shell,
        "generation_id": ensure_shell_generation_id(),
        "built_at": shell.get("built_at") or _now(),
        "freeze_status": freeze_status,
        "queue_sa_id": queue.get("sa_id"),
        "queue_pos": queue.get("queue_pos"),
        "queue_total": queue.get("queue_total"),
        "queue_role": queue.get("queue_role"),
        "valid_yes": fn.get("valid_yes"),
        "brain_vy": fn.get("brain_vy"),
        "p0_next_action": p0_next,
        "p0_title": p0.get("title") or "Source A worker",
        "form_pending": form_pending,
        "form_live": form_live,
        "inbox_pending": bool(inbox.get("pending")),
        "task_id": str(inbox.get("sa_id") or queue.get("sa_id") or "—"),
        "task_title": str(inbox.get("title") or inbox.get("subject") or queue.get("title") or "—"),
        "worker_busy": executor_busy or bool(fn.get("executor_busy")),
        "worker_mode": unified_state,
        "autorun_paused": bool(fn.get("kill_flag")),
    }


def _read_sina_json(name: str) -> dict:
    path = Path.home() / ".sina" / name
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _current_turn_slice(*, inbox: dict, queue_sa: str | None) -> dict:
    meta = inbox.get("meta") or {}
    sa = str(inbox.get("sa_id") or meta.get("sa_id") or queue_sa or "")
    return {
        "is_current": True,
        "execution_surface": "inbox_only",
        "execution_bind": "bound",
        "sa_id": sa,
        "upgrade_id": meta.get("upgrade_id"),
        "queue_role": meta.get("queue_role"),
        "pending": bool(inbox.get("pending")),
        "cta": "RUN INBOX",
        "bind_law": "Never execute queue_pos != 1 unless broker advanced",
    }


def _next_steps_preview_slice() -> dict:
    live = _read_sina_json("live-ongoing-prompts-next-10-v1.json")
    turns: list[dict] = []
    for t in live.get("turns") or []:
        if t.get("is_current"):
            row = {
                "sa_id": t.get("sa_id"),
                "title": t.get("title"),
                "role": t.get("role"),
                "is_current": True,
                "execution_bind": t.get("execution_bind"),
                "execution_surface": t.get("execution_surface"),
            }
        else:
            row = {
                "sa_id": t.get("sa_id"),
                "title": (str(t.get("title") or ""))[:96],
                "role": t.get("role"),
                "is_current": False,
                "execution_bind": "preview_not_bound",
                "execution_surface": "not_bound",
                "label": "not bound — preview only",
            }
        turns.append(row)
    current = next((x for x in turns if x.get("is_current")), turns[0] if turns else {})
    return {
        "execution_surface": "inbox_only",
        "cursor_pos": live.get("cursor_pos"),
        "current_turn": current,
        "turns": turns,
        "note": "Row 1 = RUN INBOX only · rows 2–10 are preview — not bound",
    }


def _ecosystem_connected_slice() -> dict:
    """Disk receipt only — never run validator marathon on Hub poll (INCIDENT-039)."""
    row = _read_sina_json("sourcea-ecosystem-connected-receipt-v1.json")
    if not row:
        return {
            "ecosystem_connected": None,
            "ok": None,
            "line": "ecosystem-connected · run heal or cloud CI validator",
            "checks": {},
            "receipt_stale": True,
        }
    return {
        "ecosystem_connected": bool(row.get("ecosystem_connected")),
        "ok": bool(row.get("ok")),
        "line": row.get("line"),
        "checks": row.get("checks"),
        "receipt_at": row.get("at"),
        "outbound_progress_line": row.get("outbound_progress_line"),
        "execution_honesty_line": row.get("execution_honesty_line"),
    }


def _worker_connected_slice() -> dict:
    """Disk receipt only — hub_check=False path; no recursive GET /api/worker-hub/v1."""
    row = _read_sina_json("sourcea-worker-connected-receipt-v1.json")
    if not row:
        return {
            "connected": None,
            "ok": None,
            "line": "worker-connected · run heal or cloud CI validator",
            "checks": {},
            "receipt_stale": True,
        }
    return {
        "connected": bool(row.get("connected")),
        "ok": bool(row.get("ok")),
        "line": row.get("line"),
        "outbound_progress_line": row.get("outbound_progress_line"),
        "execution_honesty_line": row.get("execution_honesty_line"),
        "checks": row.get("checks"),
        "receipt_at": row.get("at"),
    }


def _build_extended_slices() -> dict:
    """Heavy H1 slices — lazy-loaded via /api/worker-hub/extended/v1."""
    outbound_factory_upgrade = _outbound_factory_upgrade_slice()
    loop_specialist = _loop_specialist_slice()
    investigator_room = _investigator_room_slice()
    judge_room = _judge_room_slice()
    routing_panel = _routing_panel_slice()
    disclosure_ladder = _disclosure_ladder_slice()
    mcp_stack = _mcp_stack_slice()
    tool_pick = _tool_pick_slice()
    full_stack_fix_plan = _full_stack_fix_plan_slice()
    commercial_command = _commercial_command_slice()

    commercial_pipeline: dict = {}
    commercial_agents: dict = {}
    try:
        from commercial_pipeline_v1 import pipeline_glance_payload  # noqa: WPS433
        from commercial_agents_wire_v1 import commercial_agent_payload  # noqa: WPS433

        commercial_pipeline = pipeline_glance_payload(refresh=False)
        commercial_agents = commercial_agent_payload(commercial_pipeline)
    except Exception as exc:
        commercial_pipeline = {"ok": False, "error": str(exc)}
        commercial_agents = {"ok": False, "error": str(exc)}

    better_loop: dict = {}
    try:
        from better_loop_pulse_v1 import hub_slice  # noqa: WPS433

        better_loop = hub_slice(refresh=False)
    except Exception as exc:
        better_loop = {"ok": False, "error": str(exc), "schema": "worker-hub-better-loop-v1"}

    best_loop_oqg: dict = {}
    try:
        from best_loop_oqg_score_v1 import hub_slice as oqg_hub_slice  # noqa: WPS433

        best_loop_oqg = oqg_hub_slice()
    except Exception as exc:
        best_loop_oqg = {"ok": False, "error": str(exc), "schema": "worker-hub-best-loop-oqg-v1"}

    nerve_system: dict = {}
    try:
        from agent_nerve_system_v1 import hub_slice as nerve_hub_slice  # noqa: WPS433

        nerve_system = nerve_hub_slice()
    except Exception as exc:
        nerve_system = {"ok": False, "error": str(exc), "schema": "worker-hub-nerve-system-v1"}

    w3_founder_review: dict = {}
    try:
        from w3_founder_review_v1 import hub_slice as w3_review_hub_slice  # noqa: WPS433

        w3_founder_review = w3_review_hub_slice()
    except Exception as exc:
        w3_founder_review = {"ok": False, "error": str(exc), "schema": "worker-hub-w3-founder-review-v1"}

    factory_output_critic: dict = {}
    try:
        from factory_output_critic_circle_v1 import hub_slice as critic_hub_slice  # noqa: WPS433

        factory_output_critic = critic_hub_slice()
    except Exception as exc:
        factory_output_critic = {"ok": False, "error": str(exc), "schema": "worker-hub-factory-output-critic-v1"}

    receiver_interest: dict = {}
    try:
        from receiver_interest_loop_v1 import hub_slice as ril_hub_slice  # noqa: WPS433

        receiver_interest = ril_hub_slice()
    except Exception as exc:
        receiver_interest = {"ok": False, "error": str(exc), "schema": "worker-hub-receiver-interest-v1"}

    conversation_interest: dict = {}
    try:
        from conversation_interest_loop_v1 import hub_slice as cil_hub_slice  # noqa: WPS433

        conversation_interest = cil_hub_slice()
    except Exception as exc:
        conversation_interest = {"ok": False, "error": str(exc), "schema": "worker-hub-conversation-interest-v1"}

    fbe_glance: dict = {}
    try:
        from fbe_hub_projection_v1 import payload as fbe_payload  # noqa: WPS433

        fp = fbe_payload()
        fbe_glance = {
            "schema": "worker-hub-fbe-glance-v1",
            "charter_path": fp.get("charter_path", "docs/SOURCEA_FACTORY_BUILDER_ENGINE_LOCKED_v1.md"),
            "api": "/api/fbe/v1",
            "wave": fp.get("wave", "W4"),
            "graph_nodes": fp.get("graph_nodes", 76),
            "spawn_ready": fp.get("spawn_ready", False),
            "fleet_ready": fp.get("fleet_ready", False),
            "factory_3_label": fp.get("factory_3_label", "Governed App Factory"),
            "factory_3_product": fp.get("factory_3_product", "Forge"),
            "tier_achieved": fp.get("tier_achieved"),
            "w6_note": fp.get("w6_note"),
        }
    except Exception as exc:
        fbe_glance = {"ok": False, "error": str(exc)}

    return {
        "outbound_factory_upgrade": outbound_factory_upgrade,
        "loop_specialist": loop_specialist,
        "investigator_room": investigator_room,
        "judge_room": judge_room,
        "routing_panel": routing_panel,
        "disclosure_ladder": disclosure_ladder,
        "mcp_stack": mcp_stack,
        "tool_pick": tool_pick,
        "full_stack_fix_plan": full_stack_fix_plan,
        "commercial_command": commercial_command,
        "commercial_pipeline": commercial_pipeline,
        "commercial_agents": commercial_agents,
        "better_loop": better_loop,
        "best_loop_oqg": best_loop_oqg,
        "nerve_system": nerve_system,
        "w3_founder_review": w3_founder_review,
        "factory_output_critic": factory_output_critic,
        "receiver_interest": receiver_interest,
        "conversation_interest": conversation_interest,
        "fbe": fbe_glance,
        "rrl": _rrl_slice(),
        "phase0_reference": _phase0_slice(),
        "policy_links": list(POLICY_LINKS),
    }


def worker_hub_extended_payload() -> dict:
    return {
        "ok": True,
        "schema": EXTENDED_SCHEMA,
        "api": EXTENDED_API_PATH,
        "built_at": _now(),
        **_build_extended_slices(),
    }


def worker_hub_payload(*, skip_cache: bool = False) -> dict:
    cached = _cache_hit(skip_cache=skip_cache)
    if cached is not None:
        _dbg_e2e(
            hypothesis_id="H1",
            location="worker_hub_v1:worker_hub_payload",
            message="cache_hit",
            data={"age_ms": int((time.monotonic() - float(_CACHE.get("at") or 0)) * 1000)},
        )
        return cached

    with _BUILD_LOCK:
        cached = _cache_hit(skip_cache=skip_cache)
        if cached is not None:
            _dbg_e2e(
                hypothesis_id="H2",
                location="worker_hub_v1:worker_hub_payload",
                message="cache_hit_after_lock",
                data={"age_ms": int((time.monotonic() - float(_CACHE.get("at") or 0)) * 1000)},
            )
            return cached

        build_start = time.monotonic()
        _dbg_e2e(
            hypothesis_id="H1",
            location="worker_hub_v1:worker_hub_payload",
            message="cache_miss_build_start",
            data={},
        )
        row = _build_worker_hub_payload_row()
        _CACHE["at"] = time.monotonic()
        _CACHE["payload"] = row
        _dbg_e2e(
            hypothesis_id="H1",
            location="worker_hub_v1:worker_hub_payload",
            message="cache_miss_build_done",
            data={"build_ms": int((time.monotonic() - build_start) * 1000)},
        )
        return row


def _build_worker_hub_payload_row() -> dict:
    from worker_hub_staleness_v1 import staleness_probe  # noqa: WPS433

    slices = _fast_worker_slices()
    health = staleness_probe(queue_sa_id=slices.get("queue_sa_id"))

    from worker_inject_lib import inbox_status  # noqa: WPS433

    inbox = inbox_status()
    current_turn = _current_turn_slice(inbox=inbox, queue_sa=slices.get("queue_sa_id"))
    next_steps = _next_steps_preview_slice()
    connected = _worker_connected_slice()
    ecosystem = _ecosystem_connected_slice()

    from worker_hub_daily_rooms_v1 import daily_rooms_payload  # noqa: WPS433

    daily_rooms = daily_rooms_payload()

    kernel_k1: dict = {}
    try:
        from sina_command_lib import kernel_k1_payload  # noqa: WPS433

        kernel_k1 = kernel_k1_payload()
    except Exception as e:
        kernel_k1 = {"ok": False, "verdict": "BLOCK", "error": str(e)}

    upgrade = _upgrade_slice()
    ecosystem_mac_health = _ecosystem_mac_health_slice(
        hub_boot={
            "p0_next_action": slices.get("p0_next_action"),
            "p0_title": slices.get("p0_title"),
        }
    )
    plans_unified = _plans_unified_slice()
    cloud_forge_run_proceed = _cloud_forge_run_proceed_slice()
    anti_theater = _anti_theater_slice()
    agent_behavior = _behavior_settings_slice()
    factory_cost_intelligence = _factory_cost_intelligence_slice()
    world_model = _world_model_slice()

    row = {
        "ok": True,
        "schema": SCHEMA,
        "api": API_PATH,
        "hub_mode": "worker-only",
        "command_retired_forever": True,
        "law": "ASF_RETIRE_SINA_COMMAND_FOREVER_LOCKED_v1.md",
        "built_at": slices.get("built_at"),
        "generation_id": slices.get("generation_id"),
        "freeze_status": slices.get("freeze_status"),
        "queue_sa_id": slices.get("queue_sa_id"),
        "queue_pos": slices.get("queue_pos"),
        "queue_total": slices.get("queue_total"),
        "queue_role": slices.get("queue_role"),
        "valid_yes": slices.get("valid_yes"),
        "brain_vy": slices.get("brain_vy"),
        "p0_title": slices.get("p0_title"),
        "p0_next_action": slices.get("p0_next_action"),
        "form_pending": slices.get("form_pending"),
        "form_live": slices.get("form_live"),
        "upgrade": upgrade,
        "ecosystem_mac_health": ecosystem_mac_health,
        "health_grade": ecosystem_mac_health.get("health_grade"),
        "pressure_badge": ecosystem_mac_health.get("pressure_badge"),
        "m111_line": ecosystem_mac_health.get("m111_line"),
        "mandatory_next": ecosystem_mac_health.get("mandatory_next"),
        "relieve_url": (ecosystem_mac_health.get("health_strip") or {}).get("relieve_url"),
        "mac_health_live": _mac_health_live_slice(),
        "cloud_glance_line": (ecosystem_mac_health.get("cloud_glance") or {}).get("founder_line"),
        "plans_unified": plans_unified,
        "cloud_forge_run_proceed": cloud_forge_run_proceed,
        "anti_theater": anti_theater,
        "agent_behavior": agent_behavior,
        "factory_cost_intelligence": factory_cost_intelligence,
        "world_model_check": world_model,
        "extended_api": EXTENDED_API_PATH,
        "inbox_pending": slices.get("inbox_pending"),
        "task_id": slices.get("task_id"),
        "task_title": slices.get("task_title"),
        "execution_surface": "inbox_only",
        "current_turn": current_turn,
        "next_steps_preview": next_steps,
        "connected": connected.get("connected"),
        "worker_connected": connected,
        "ecosystem_connected": ecosystem.get("ecosystem_connected"),
        "ecosystem_wire": ecosystem,
        "outbound_progress_line": connected.get("outbound_progress_line"),
        "execution_honesty_line": connected.get("execution_honesty_line"),
        "worker_busy": slices.get("worker_busy"),
        "worker_mode": slices.get("worker_mode"),
        "autorun_paused": slices.get("autorun_paused"),
        "hero_actions": [
            {
                "id": "h2_machines",
                "label": "Machine Hub",
                "path": "/machines/",
                "url": "http://127.0.0.1:13020/machines/",
            }
        ],
        "goal1_summary": {
            "autorun_state": slices.get("worker_mode"),
            "executor_busy": slices.get("worker_busy"),
            "inbox_pending": slices.get("inbox_pending"),
        },
        "health": health,
        "kernel_k1": {
            "verdict": kernel_k1.get("verdict"),
            "ok": kernel_k1.get("ok"),
            "founder_line": kernel_k1.get("founder_line"),
            "blockers": (kernel_k1.get("critic_boot") or {}).get("blockers") or [],
        },
        "daily_rooms": daily_rooms,
        "actions": {
            "safety": "founder-ecosystem-safety",
            "k1": "founder-enforcement-k1",
            "refresh": {"path": "/refresh", "mode": "light"},
            "heal": {"path": "/api/worker-hub/heal", "method": "POST"},
            "outbound_coherence_heal": {
                "path": "/api/worker-hub/outbound-coherence-heal/v1",
                "method": "POST",
                "label": "Outbound disk coherence heal",
            },
            "pipeline_node_graph_run": {
                "path": "/api/pipeline-node-graph/run/v1",
                "method": "POST",
                "label": "Run node graph T3 proof tier",
            },
            "rooms_run": {"path": "/api/worker-hub/rooms/run", "method": "POST"},
            "commercial_run": {"path": "/api/worker-hub/commercial/run", "method": "POST"},
            "loop_specialist_tick": {"path": "/api/loop-specialist/tick/v1", "method": "POST"},
            "investigator_circle_tick": {
                "path": "/api/investigator-circle/tick/v1",
                "method": "POST",
            },
            "judge_loop_tick": {"path": "/api/judge-loop/tick/v1", "method": "POST"},
            "routing_panel_refresh": {
                "path": "/api/routing-panel/tick/v1",
                "method": "POST",
            },
            "disclosure_ladder_tick": {
                "path": "/api/disclosure-ladder/tick/v1",
                "method": "POST",
            },
            "mcp_stack_tick": {
                "path": "/api/mcp-stack/tick/v1",
                "method": "POST",
            },
            "tool_pick_tick": {
                "path": "/api/tool-pick/tick/v1",
                "method": "POST",
            },
            "plans_unified_tick": {
                "path": "/api/plans-unified/tick/v1",
                "method": "POST",
            },
            "cloud_forge_run_proceed": {
                "path": "/api/cloud-forge-run/proceed/v1",
                "method": "POST",
                "label": "Proceed next cloud task (OpenRouter/Gemini on Railway)",
                "body": {"llm_provider": "openrouter", "full_motor": True},
            },
            "world_model_tick": {
                "path": "/api/world-model-plan-check/tick/v1",
                "method": "POST",
            },
            "loop_chain_tick": {
                "path": "/api/loop-chain/tick/v1",
                "method": "POST",
            },
            "form": "/api/live-founder-decision-form-v1",
            "extended": {"path": EXTENDED_API_PATH, "method": "GET"},
            "h2_machines": upgrade.get("h2_machines_url"),
        },
    }
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Worker hub v1 payload")
    p.add_argument("--json", action="store_true")
    p.add_argument("--extended", action="store_true", help="Emit extended hub slices (nerve, OQG, better-loop)")
    p.add_argument("--no-cache", action="store_true")
    args = p.parse_args()
    row = worker_hub_extended_payload() if args.extended else worker_hub_payload(skip_cache=args.no_cache)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        h = row.get("health") or {}
        print(
            f"WORKER-HUB: {row.get('queue_sa_id')} pos={row.get('queue_pos')} "
            f"freeze={row.get('freeze_status')} health={h.get('status')}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
