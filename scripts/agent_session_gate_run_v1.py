#!/usr/bin/env python3
"""Universal session gate — memory mirror + truth bundle + rules loop + entry gate.

Law: AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md
Receipt: ~/.sina/agent_session_gate_receipt_v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RECEIPT = Path.home() / ".sina" / "agent_session_gate_receipt_v1.json"
TRUTH_CACHE = Path.home() / ".sina" / "last-truth-bundle-v1.json"
MIRROR_PATH = Path.home() / ".sina" / "agent-memory-mirror-v1.json"
PY = sys.executable
L2_GATE_ROLES = frozenset({"worker", "maintainer", "researcher", "archive", "any"})
L1_GATE_ROLES = frozenset({"brain", "governance", "commercial", "brief", "any"})
CONDUCT_ROLE_MAP = {
    "governance": "any",
    "commercial": "any",
    "brief": "any",
    "researcher": "any",
    "maintainer": "any",
}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str]) -> tuple[int, str]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True, cwd=str(ROOT))
        return 0, out
    except subprocess.CalledProcessError as e:
        return e.returncode, e.output or ""


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _mac_founder_session() -> bool:
    """Mac control plane — read receipts once; no governance full tier or audit loops."""
    return (Path.home() / ".sina" / "mac-control-plane-v1.flag").is_file()


def _poison_validate_step() -> dict:
    code, out = _run(
        [PY, str(SCRIPTS / "agent_mirror_poison_scrub_v1.py"), "--validate", "--json"]
    )
    row = json.loads(out[out.find("{") :]) if "{" in out else {}
    return {
        "step": "mirror_poison_validate",
        "ok": code == 0 and row.get("ok", False),
        "exit": code,
        "poison_hits": len(row.get("poison_hits") or []),
        "mode": "validate_only",
        "incident": "INCIDENT-041",
    }


def _wire_covers_agentic(wire: dict, role: str) -> bool:
    if not wire.get("ok"):
        return False
    layers = wire.get("layers") or {}
    l1 = (layers.get("L1") or {}).get("l1_to_brain") or 0
    l2 = (layers.get("L2") or {}).get("l2_wired") or 0
    if role in L1_GATE_ROLES:
        return l1 >= 3
    if role in L2_GATE_ROLES and role not in L1_GATE_ROLES:
        return l2 >= 4
    return True


def run_gate(role: str = "any", *, scan_text: str = "", pre_ship: bool = False, worker_wire: bool = False, graph_tier: bool = False, ecosystem_wire: bool = False) -> dict:
    steps: list[dict] = []
    ok = True
    mirror: dict = {}
    bundle: dict = {}
    conduct: dict = {}

    freeze_flag = Path.home() / ".sina" / "auto-run-disabled-v1.flag"
    focus_freeze = freeze_flag.is_file() and not pre_ship
    mac_session = _mac_founder_session() and not pre_ship
    mac_spine_fresh: dict = {}
    mac_spine_hb: dict = {}

    if not pre_ship:
        try:
            sys.path.insert(0, str(SCRIPTS))
            from mac_spine_bridge_v1 import (  # noqa: WPS433
                run_mac_spine_fresh_main,
                run_mac_spine_heartbeat,
            )

            agent_id = f"cursor-{role}" if role != "any" else "cursor"
            mac_spine_fresh = run_mac_spine_fresh_main(agent_id=agent_id)
            steps.append(
                {
                    "step": "mac_spine_fresh_main",
                    "ok": bool(mac_spine_fresh.get("ok")),
                    "verdict": mac_spine_fresh.get("verdict"),
                    "reason": mac_spine_fresh.get("reason"),
                    "local_main_sha": mac_spine_fresh.get("local_main_sha"),
                    "origin_main_sha": mac_spine_fresh.get("origin_main_sha"),
                    "sync_id": mac_spine_fresh.get("sync_id"),
                    "receipt_path": mac_spine_fresh.get("receipt_path"),
                    "law": "L16 W1",
                }
            )
            if not mac_spine_fresh.get("ok"):
                ok = False
            mac_spine_hb = run_mac_spine_heartbeat(agent_id=agent_id, role=role)
            steps.append(
                {
                    "step": "mac_spine_heartbeat",
                    "ok": bool(mac_spine_hb.get("ok")),
                    "agent_id": agent_id,
                    "dashboard_status": (mac_spine_hb.get("dashboard_row") or {}).get("status"),
                    "receipt_path": mac_spine_hb.get("receipt_path"),
                    "degraded": mac_spine_hb.get("degraded"),
                    "law": "L16 W2",
                }
            )
        except Exception as exc:
            steps.append(
                {
                    "step": "mac_spine_bridge",
                    "ok": False,
                    "error": str(exc)[:200],
                    "law": "L16",
                }
            )
            ok = False

    if pre_ship:
        if not scan_text.strip():
            return {
                "schema": "agent-session-gate-receipt-v1.1",
                "ok": False,
                "gate_id": f"ASG-{datetime.now(timezone.utc).strftime('%Y%m%d')}-pre-ship-empty",
                "at": _now(),
                "role": role,
                "steps": [{"step": "pre_ship", "ok": False, "error": "scan_text required"}],
                "mode": "pre_ship",
                "stack_version": 2,
            }
    else:
        if focus_freeze:
            mirror = _read_json(MIRROR_PATH)
            bundle = _read_json(TRUTH_CACHE)
            wire = _read_json(Path.home() / ".sina" / "anti-staleness-auto-wire-v1.json")
            code_ml, out_ml = _run(
                [
                    PY,
                    str(SCRIPTS / "mac_law_machine_enforce_v1.py"),
                    "--sync-receipt",
                    "--enforce",
                    "--json",
                ]
            )
            ml_fz = json.loads(out_ml[out_ml.find("{") :]) if "{" in out_ml else {}
            steps.extend(
                [
                    {"step": "anti_staleness_auto_wire", "ok": True, "exit": 0, "mode": "mac_focus_freeze", "skipped": True},
                    {"step": "memory_mirror_sync", "ok": bool(mirror), "exit": 0, "note": "cached"},
                    _poison_validate_step(),
                    {"step": "daily_duty_card", "ok": True, "exit": 0, "mode": "mac_focus_freeze"},
                    {
                        "step": "mac_law_machine_enforce",
                        "ok": code_ml == 0 and ml_fz.get("ok", True),
                        "exit": code_ml,
                        "line": (ml_fz.get("line") or "")[:120],
                        "mode": "mac_focus_freeze",
                    },
                    {
                        "step": "mac_law_universal_wire",
                        "ok": True,
                        "exit": 0,
                        "mode": "mac_focus_freeze",
                        "note": "light assess via machine enforce cache",
                    },
                    {
                        "step": "mac_law_agent_execution_plane_lock",
                        "ok": bool(
                            (_read_json(Path.home() / ".sina/mac-law-agent-execution-plane-lock-receipt-v1.json") or {}).get(
                                "ok"
                            )
                        ),
                        "exit": 0,
                        "mode": "mac_focus_freeze",
                        "note": "receipt cache",
                    },
                    {"step": "truth_bundle", "ok": bundle.get("schema") == "agent-truth-bundle-v1", "exit": 0, "note": "cached"},
                    {"step": "rules_loop", "ok": True, "exit": 0, "mode": "mac_focus_freeze", "skipped": True},
                ]
            )
            ok = all(s.get("ok", True) for s in steps)
        else:
            code, out = _run(
                [
                    PY,
                    str(SCRIPTS / "anti_staleness_auto_wire_v1.py"),
                    "--role",
                    role,
                    "--tier",
                    "session",
                    "--json",
                ]
            )
            wire = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and wire.get("ok", True)
            steps.append(
                {
                    "step": "anti_staleness_auto_wire",
                    "ok": step_ok,
                    "exit": code,
                    "queue_sa": wire.get("queue_sa"),
                    "factory_now_line": (wire.get("factory_now_line") or "")[:80],
                }
            )
            ok = ok and step_ok

            mirror = _read_json(MIRROR_PATH)
            steps.append(
                {
                    "step": "memory_mirror_sync",
                    "ok": bool(mirror.get("mirror_hash8") or mirror.get("validation", {}).get("ok")),
                    "exit": 0,
                    "note": "via anti_staleness disk_live_wire",
                }
            )
            poison_step = _poison_validate_step()
            steps.append(poison_step)
            ok = ok and poison_step.get("ok", True)

            code, out = _run([PY, str(SCRIPTS / "agent_daily_duty_card_v1.py"), "--validate", "--json"])
            daily = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and daily.get("ok")
            steps.append(
                {
                    "step": "daily_duty_card",
                    "ok": step_ok,
                    "exit": code,
                    "item_count": daily.get("item_count"),
                    "path": daily.get("card_path"),
                }
            )
            ok = ok and step_ok

            code, out = _run(
                [
                    PY,
                    str(SCRIPTS / "mac_law_machine_enforce_v1.py"),
                    "--sync-receipt",
                    "--enforce",
                    "--json",
                ]
            )
            ml = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and ml.get("ok", True)
            steps.append(
                {
                    "step": "mac_law_machine_enforce",
                    "ok": step_ok,
                    "exit": code,
                    "line": (ml.get("line") or "")[:120],
                    "issues": ml.get("issues") or [],
                }
            )
            ok = ok and step_ok

            code, out = _run(
                [
                    PY,
                    str(SCRIPTS / "mac_law_universal_wire_v1.py"),
                    "--sync-receipt",
                    "--json",
                ]
            )
            ulw = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and ulw.get("ok", True)
            steps.append(
                {
                    "step": "mac_law_universal_wire",
                    "ok": step_ok,
                    "exit": code,
                    "line": (ulw.get("line") or "")[:120],
                    "issues": (ulw.get("issues") or [])[:8],
                }
            )
            ok = ok and step_ok

            code, out = _run(
                [
                    PY,
                    str(SCRIPTS / "mac_law_agent_execution_plane_lock_v1.py"),
                    "--sync-receipt",
                    "--json",
                ]
            )
            mll = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and mll.get("ok", True)
            steps.append(
                {
                    "step": "mac_law_agent_execution_plane_lock",
                    "ok": step_ok,
                    "exit": code,
                    "line": (mll.get("line") or "")[:120],
                    "issues": (mll.get("issues") or [])[:8],
                }
            )
            ok = ok and step_ok

            bundle = _read_json(TRUTH_CACHE)
            step_ok = bundle.get("schema") == "agent-truth-bundle-v1"
            steps.append(
                {
                    "step": "truth_bundle",
                    "ok": step_ok,
                    "exit": 0,
                    "note": "cached via anti_staleness disk_live_wire",
                }
            )
            ok = ok and step_ok

            code, out = _run(
                [PY, str(SCRIPTS / "agent_rules_loop_orchestrator.py"), "--phase", "session_start", "--json-only"]
            )
            rules = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and rules.get("ok")
            steps.append({"step": "rules_loop", "ok": step_ok, "exit": code})
            ok = ok and step_ok

        if not focus_freeze and role in L1_GATE_ROLES and not _wire_covers_agentic(wire, role):
            code, out = _run([PY, str(SCRIPTS / "agentic_layer_pipeline_v2.py"), "--json", "--tier", "fast"])
            v2 = json.loads(out[out.find("{") :]) if "{" in out else {}
            health = v2.get("health") or {}
            step_ok = code == 0 and v2.get("schema") == "agentic-layer-pipeline-v2"
            step_ok = step_ok and (v2.get("l1_summary") or {}).get("l1_to_brain", 0) >= 3
            steps.append(
                {
                    "step": "agentic_pipeline_v2",
                    "ok": step_ok,
                    "exit": code,
                    "queue_head": (v2.get("brain_summary") or {}).get("queue_head"),
                    "health_status": health.get("status"),
                    "issues": len(v2.get("issues") or []),
                }
            )
            ok = ok and step_ok
        elif role in L1_GATE_ROLES:
            steps.append(
                {
                    "step": "agentic_pipeline_v2",
                    "ok": True,
                    "exit": 0,
                    "note": "via anti_staleness_auto_wire" if not focus_freeze else "mac_focus_freeze cached",
                    "queue_head": wire.get("queue_sa"),
                }
            )

        if not focus_freeze and role in L2_GATE_ROLES and role not in L1_GATE_ROLES and not _wire_covers_agentic(wire, role):
            code, out = _run([PY, str(SCRIPTS / "agentic_layer_pipeline_v2.py"), "--json", "--tier", "fast"])
            v2 = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and v2.get("schema") == "agentic-layer-pipeline-v2"
            step_ok = step_ok and (v2.get("brain_summary") or {}).get("l2_wired", 0) >= 4
            steps.append(
                {
                    "step": "agentic_pipeline_v2_l2",
                    "ok": step_ok,
                    "exit": code,
                    "queue_head": (v2.get("brain_summary") or {}).get("queue_head"),
                    "l2_count": (v2.get("brain_summary") or {}).get("l2_wired"),
                    "health_status": (v2.get("health") or {}).get("status"),
                }
            )
            ok = ok and step_ok
        elif role in L2_GATE_ROLES and role not in L1_GATE_ROLES:
            steps.append(
                {
                    "step": "agentic_pipeline_v2_l2",
                    "ok": True,
                    "exit": 0,
                    "note": "via anti_staleness_auto_wire",
                    "queue_head": wire.get("queue_sa"),
                    "l2_count": (wire.get("layers") or {}).get("L2", {}).get("l2_wired"),
                }
            )

    if not pre_ship:
        if focus_freeze or mac_session:
            bl_cached = _read_json(Path.home() / ".sina" / "better-loop-pulse-receipt-v1.json")
            nerve_cached = _read_json(Path.home() / ".sina" / "agent-nerve-system-receipt-v1.json")
            zero_cached = _read_json(Path.home() / ".sina" / "governance-zero-drift-live-wire-v1.json")
            mode_note = "mac_focus_freeze" if focus_freeze else "mac_control_plane_read_only"
            steps.extend(
                [
                    {"step": "stranger_agent_safety_live_wire", "ok": True, "exit": 0, "mode": mode_note, "skipped": True},
                    {
                        "step": "governance_zero_drift_live_wire",
                        "ok": True,
                        "exit": 0,
                        "mode": mode_note,
                        "skipped": True,
                        "note": "full tier FORBIDDEN on Mac — INCIDENT-041",
                        "zero_drift_line": (zero_cached.get("zero_drift_line") or "")[:96],
                    },
                    {"step": "sourcea_crawl_mirror_pipeline", "ok": True, "exit": 0, "mode": mode_note, "skipped": True},
                    {
                        "step": "better_loop_pulse",
                        "ok": bl_cached.get("schema") == "better-loop-pulse-receipt-v1",
                        "exit": 0,
                        "mode": mode_note,
                        "note": "cached receipt",
                        "better_loop_line": (bl_cached.get("better_loop_line") or "")[:96],
                    },
                    {
                        "step": "nerve_system",
                        "ok": nerve_cached.get("schema") == "agent-nerve-system-receipt-v1",
                        "exit": 0,
                        "mode": mode_note,
                        "note": "cached nerve receipt",
                        "nerve_system_line": (nerve_cached.get("nerve_system_line") or "")[:96],
                        "ship_gates": nerve_cached.get("ship_gates") or {},
                    },
                ]
            )
        else:
            code, out = _run(
                [
                    PY,
                    str(SCRIPTS / "stranger_agent_safety_live_wire_v1.py"),
                    "--role",
                    role,
                    "--tier",
                    "session",
                    "--agent",
                    "cursor",
                    "--json",
                ]
            )
            sascip = json.loads(out[out.find("{") :]) if "{" in out else {}
            admission = sascip.get("admission") or {}
            step_ok = code == 0 and sascip.get("schema") == "stranger-agent-safety-live-wire-v1"
            steps.append(
                {
                    "step": "stranger_agent_safety_live_wire",
                    "ok": step_ok,
                    "exit": code,
                    "trust_tier": admission.get("trust_tier"),
                    "resolved_agent_id": admission.get("resolved_agent_id"),
                    "stranger": admission.get("stranger"),
                    "admission_ok": admission.get("ok"),
                    "risk_score": admission.get("risk_score"),
                    "one_line": sascip.get("sascip_safety_line"),
                    "chains": sascip.get("chains"),
                    "elapsed_sec": sascip.get("elapsed_sec"),
                }
            )
            ok = ok and step_ok

            code, out = _run(
                [
                    PY,
                    str(SCRIPTS / "governance_zero_drift_live_wire_v1.py"),
                    "--role",
                    role,
                    "--tier",
                    "session",
                    "--skip-anti-staleness",
                    "--json",
                ]
            )
            zero = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and zero.get("ok", True)
            steps.append(
                {
                    "step": "governance_zero_drift_live_wire",
                    "ok": step_ok,
                    "exit": code,
                    "drift_score": zero.get("drift_score"),
                    "drift_items": zero.get("drift_items"),
                    "queue_sa": zero.get("queue_sa"),
                    "zero_drift_line": (zero.get("zero_drift_line") or "")[:96],
                    "chains": zero.get("chains"),
                }
            )
            ok = ok and step_ok

            code, out = _run(
                [
                    PY,
                    str(SCRIPTS / "sourcea_crawl_mirror_pipeline_v1.py"),
                    "--role",
                    role,
                    "--tier",
                    "session",
                    "--skip-anti-staleness",
                    "--json",
                ]
            )
            crawl = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and crawl.get("ok", True)
            steps.append(
                {
                    "step": "sourcea_crawl_mirror_pipeline",
                    "ok": step_ok,
                    "exit": code,
                    "queue_sa": crawl.get("queue_sa"),
                    "elapsed_sec": crawl.get("elapsed_sec"),
                    "within_budget": crawl.get("within_budget"),
                    "stages": crawl.get("stages"),
                }
            )
            ok = ok and step_ok

            code, out = _run([PY, str(SCRIPTS / "better_loop_pulse_v1.py"), "--json"])
            bl = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and bl.get("schema") == "better-loop-pulse-receipt-v1"
            steps.append(
                {
                    "step": "better_loop_pulse",
                    "ok": step_ok,
                    "exit": code,
                    "red_count": bl.get("red_count"),
                    "weekly_lever": bl.get("weekly_lever"),
                    "better_loop_line": (bl.get("better_loop_line") or "")[:96],
                    "better_loop": {"ok": bl.get("ok"), "mandatory": step_ok},
                }
            )
            ok = ok and step_ok

            code, out = _run([PY, str(SCRIPTS / "loop_observatory_report_v1.py"), "--json"])
            obs_row = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and obs_row.get("schema") == "loop-observatory-report-v1"
            steps.append(
                {
                    "step": "loop_observatory_report",
                    "ok": step_ok,
                    "exit": code,
                    "founder_one_line": (obs_row.get("founder_one_line") or "")[:96],
                }
            )
            ok = ok and step_ok

            code, out = _run([PY, str(SCRIPTS / "loop_specialist_tick_v1.py"), "--json"])
            spec_row = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and spec_row.get("schema") == "loop-specialist-tick-receipt-v1"
            steps.append(
                {
                    "step": "loop_specialist_tick",
                    "ok": step_ok,
                    "exit": code,
                    "tick_decision": spec_row.get("tick_decision"),
                    "loop_specialist_line": (spec_row.get("loop_specialist_line") or "")[:96],
                }
            )
            ok = ok and step_ok

            code, out = _run([PY, str(SCRIPTS / "investigator_circle_run_v1.py"), "--json"])
            inv_row = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and inv_row.get("schema") == "loop-health-investigation-receipt-v1"
            steps.append(
                {
                    "step": "investigator_circle",
                    "ok": step_ok,
                    "exit": code,
                    "investigation_verdict": inv_row.get("investigation_verdict"),
                    "investigator_line": (inv_row.get("investigator_line") or "")[:96],
                }
            )
            ok = ok and step_ok

            code, out = _run([PY, str(SCRIPTS / "judge_loop_room_v1.py"), "--json"])
            jv_row = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and jv_row.get("schema") == "judge-loop-verdict-v1"
            steps.append(
                {
                    "step": "judge_loop_room",
                    "ok": step_ok,
                    "exit": code,
                    "loop_verdict": jv_row.get("loop_verdict"),
                    "judge_loop_line": (jv_row.get("judge_loop_line") or "")[:96],
                }
            )
            ok = ok and step_ok

            code, out = _run([PY, str(SCRIPTS / "founder_routing_panel_v1.py"), "--json"])
            rp_row = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and rp_row.get("schema") == "founder-routing-panel-v1"
            steps.append(
                {
                    "step": "founder_routing_panel",
                    "ok": step_ok,
                    "exit": code,
                    "founder_routing_panel_line": (rp_row.get("founder_routing_panel_line") or "")[:96],
                }
            )
            ok = ok and step_ok

            code, out = _run([PY, str(SCRIPTS / "disclosure_ladder_v1.py"), "--json"])
            dl_row = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and dl_row.get("schema") == "disclosure-ladder-receipt-v1"
            steps.append(
                {
                    "step": "disclosure_ladder",
                    "ok": step_ok,
                    "exit": code,
                    "disclosure_line": (dl_row.get("disclosure_line") or "")[:96],
                    "icp_audit_ok": dl_row.get("icp_audit_ok"),
                }
            )
            ok = ok and step_ok

            code, out = _run([PY, str(SCRIPTS / "mcp_stack_free_tier_v1.py"), "--json"])
            ms_row = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and ms_row.get("schema") == "mcp-stack-free-tier-receipt-v1"
            steps.append(
                {
                    "step": "mcp_stack_free_tier",
                    "ok": step_ok,
                    "exit": code,
                    "mcp_stack_line": (ms_row.get("mcp_stack_line") or "")[:96],
                    "pending_p0": ms_row.get("pending_p0"),
                }
            )
            ok = ok and step_ok

            code, out = _run([PY, str(SCRIPTS / "full_stack_fix_plan_pulse_v1.py"), "--sync-plan", "--json"])
            fp_row = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and fp_row.get("schema") == "full-stack-fix-plan-pulse-v1"
            steps.append(
                {
                    "step": "full_stack_fix_plan_pulse",
                    "ok": step_ok,
                    "exit": code,
                    "full_stack_fix_line": (fp_row.get("full_stack_fix_line") or "")[:96],
                    "active_wave": fp_row.get("active_wave"),
                }
            )
            ok = ok and step_ok

            code, out = _run([PY, str(SCRIPTS / "agent_nerve_system_v1.py"), "--json"])
            nerve = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and nerve.get("schema") == "agent-nerve-system-receipt-v1"
            steps.append(
                {
                    "step": "nerve_system",
                    "ok": step_ok,
                    "exit": code,
                    "queue_aligned": nerve.get("queue_aligned"),
                    "nerve_system_line": (nerve.get("nerve_system_line") or "")[:96],
                    "ship_gates": nerve.get("ship_gates") or {},
                }
            )
            ok = ok and step_ok

            code, out = _run(
                [PY, str(SCRIPTS / "ui_upgrade_first_check_v1.py"), "--wire", "--surface", "worker_hub", "--json"]
            )
            ufc = json.loads(out[out.find("{") :]) if "{" in out else {}
            step_ok = code == 0 and bool(ufc.get("wire_ok"))
            steps.append(
                {
                    "step": "ui_upgrade_first_check",
                    "ok": step_ok,
                    "exit": code,
                    "ui_upgrade_first_check_line": (ufc.get("line") or "")[:96],
                    "wire_ok": ufc.get("wire_ok"),
                }
            )
            ok = ok and step_ok

    conduct_role = CONDUCT_ROLE_MAP.get(role, role)
    main_problem_row: dict = {}
    if scan_text.strip():
        code_mp, out_mp = _run(
            [
                PY,
                str(SCRIPTS / "main_problem_trigger_v1.py"),
                "--text",
                scan_text,
                "--activate",
                "--json",
            ]
        )
        main_problem_row = json.loads(out_mp[out_mp.find("{") :]) if "{" in out_mp else {}
        if main_problem_row.get("triggered"):
            steps.append(
                {
                    "step": "main_problem_trigger",
                    "ok": bool(main_problem_row.get("ok")),
                    "exit": code_mp,
                    "mode": "PREPARE_NOT_REPORT",
                    "next_action": main_problem_row.get("next_action"),
                    "line": (main_problem_row.get("main_problem_line") or "")[:120],
                }
            )
    next_task_row: dict = {}
    if not pre_ship:
        code_nt0, out_nt0 = _run(
            [PY, str(SCRIPTS / "next_task_trigger_v1.py"), "--refresh", "--json"]
        )
        next_task_row = json.loads(out_nt0[out_nt0.find("{") :]) if "{" in out_nt0 else {}
        steps.append(
            {
                "step": "task_plan_validate_baseline",
                "ok": bool(next_task_row.get("ok")),
                "exit": code_nt0,
                "always_apply": bool(next_task_row.get("always_apply")),
                "mode": next_task_row.get("mode"),
                "line": (next_task_row.get("next_task_line") or "")[:120],
            }
        )
        code_tp, out_tp = _run([PY, str(SCRIPTS / "task_plan_priority_v1.py"), "--refresh", "--json"])
        tp_row = json.loads(out_tp[out_tp.find("{") :]) if "{" in out_tp else {}
        steps.append(
            {
                "step": "task_plan_priority",
                "ok": bool(tp_row.get("ok")),
                "exit": code_tp,
                "smart_pick": (tp_row.get("smart_pick") or {}).get("task_id"),
                "line": (tp_row.get("task_plan_priority_line") or "")[:120],
            }
        )
    if scan_text.strip():
        code_nt, out_nt = _run(
            [
                PY,
                str(SCRIPTS / "next_task_trigger_v1.py"),
                "--text",
                scan_text,
                "--activate",
                "--json",
            ]
        )
        next_task_row = json.loads(out_nt[out_nt.find("{") :]) if "{" in out_nt else next_task_row
        if next_task_row.get("triggered"):
            steps.append(
                {
                    "step": "next_task_trigger",
                    "ok": bool(next_task_row.get("ok")),
                    "exit": code_nt,
                    "mode": "VALIDATE_THEN_PROCEED",
                    "pipeline": next_task_row.get("pipeline"),
                    "line": (next_task_row.get("next_task_line") or "")[:120],
                }
            )
        else:
            code_det, out_det = _run(
                [
                    PY,
                    str(SCRIPTS / "next_task_trigger_v1.py"),
                    "--detect-topic",
                    scan_text,
                    "--json",
                ]
            )
            det = json.loads(out_det[out_det.find("{") :]) if "{" in out_det else {}
            if det.get("topic"):
                steps.append(
                    {
                        "step": "task_plan_validate_topic",
                        "ok": bool(next_task_row.get("ok")),
                        "exit": code_nt,
                        "mode": "VALIDATE_ON_TOPIC",
                        "pipeline": next_task_row.get("pipeline"),
                        "line": (next_task_row.get("next_task_line") or "")[:120],
                    }
                )
    conduct_cmd = [PY, str(SCRIPTS / "agentic_conduct_gate_v1.py"), "--role", conduct_role, "--json"]
    if scan_text:
        conduct_cmd.extend(["--task-text", scan_text])
    code, out = _run(conduct_cmd)
    conduct = json.loads(out[out.find("{") :]) if "{" in out else {}
    conduct_ok = code == 0 and conduct.get("ok", True)
    if role in ("brain", "worker", "maintainer") and conduct.get("violations"):
        conduct_ok = False
    steps.append(
        {
            "step": "conduct_gate",
            "ok": conduct_ok,
            "exit": code,
            "warnings": conduct.get("warnings") or [],
            "violations": conduct.get("violations") or [],
        }
    )
    if role in ("brain", "worker", "maintainer"):
        ok = ok and conduct_ok

    if role in ("brain", "worker", "archive") and (not pre_ship or role == "worker"):
        cmd = [PY, str(SCRIPTS / "cursor_entry_gate.py"), "--role", role]
        if scan_text and role == "worker":
            cmd.extend(["--scan-text", scan_text])
        code, out = _run(cmd)
        step_ok = code == 0
        steps.append({"step": f"entry_gate_{role}", "ok": step_ok, "exit": code})
        ok = ok and step_ok
    else:
        steps.append({"step": "entry_gate_skipped", "ok": True, "note": f"role={role} pre_ship={pre_ship}"})

    if not pre_ship and not focus_freeze:
        code, out = _run([PY, str(SCRIPTS / "critic_boot_v1.py"), "--json", "--in-gate"])
        boot = json.loads(out[out.find("{") :]) if "{" in out else {}
        step_ok = code == 0 and boot.get("ok")
        steps.append(
            {
                "step": "critic_boot",
                "ok": step_ok,
                "exit": code,
                "verdict": boot.get("verdict"),
                "blockers": boot.get("blockers") or [],
            }
        )
        ok = ok and step_ok
    elif not pre_ship and focus_freeze:
        steps.append({"step": "critic_boot", "ok": True, "exit": 0, "mode": "mac_focus_freeze", "skipped": True})

    if worker_wire and not pre_ship:
        try:
            sys.path.insert(0, str(SCRIPTS))
            from validate_sourcea_worker_connected_v1 import assess_connected  # noqa: WPS433

            wire = assess_connected(hub_check=True, write_receipt=True)
            step_ok = bool(wire.get("ok"))
            steps.append(
                {
                    "step": "sourcea_worker_connected",
                    "ok": step_ok,
                    "connected": wire.get("connected"),
                    "line": (wire.get("line") or "")[:96],
                    "outbound_progress_line": (wire.get("outbound_progress_line") or "")[:96],
                }
            )
            ok = ok and step_ok
        except Exception as exc:
            steps.append({"step": "sourcea_worker_connected", "ok": False, "error": str(exc)})
            ok = False

    if graph_tier and not pre_ship and not focus_freeze:
        try:
            sys.path.insert(0, str(SCRIPTS))
            from pipeline_node_graph_runner_v1 import run_session_tiers  # noqa: WPS433

            graph = run_session_tiers(dry_run=False)
            step_ok = bool(graph.get("ok")) or bool(graph.get("degraded"))
            steps.append(
                {
                    "step": "pipeline_node_graph_session",
                    "ok": step_ok,
                    "degraded": graph.get("degraded"),
                    "tiers": graph.get("tiers"),
                    "receipt": graph.get("receipt"),
                }
            )
            if not graph.get("ok") and not graph.get("degraded"):
                ok = False
        except Exception as exc:
            steps.append({"step": "pipeline_node_graph_session", "ok": False, "error": str(exc)})
            ok = False

    if role in ("worker", "brain") and not pre_ship and not focus_freeze:
        code, out = _run(["bash", str(SCRIPTS / "validate-brain-l2-wire-v1.sh")])
        steps.append({"step": "brain_l2_wire", "ok": code == 0, "exit": code})
        if code != 0:
            ok = False

    if ecosystem_wire and not pre_ship:
        try:
            sys.path.insert(0, str(SCRIPTS))
            from validate_sourcea_ecosystem_connected_v1 import assess_ecosystem_connected  # noqa: WPS433

            eco = assess_ecosystem_connected(write_receipt=True)
            step_ok = bool(eco.get("ok"))
            steps.append(
                {
                    "step": "sourcea_ecosystem_connected",
                    "ok": step_ok,
                    "ecosystem_connected": eco.get("ecosystem_connected"),
                    "line": (eco.get("line") or "")[:96],
                }
            )
            ok = ok and step_ok
        except Exception as exc:
            steps.append({"step": "sourcea_ecosystem_connected", "ok": False, "error": str(exc)})
            ok = False

    mp_flag = Path.home() / ".sina" / "main-problem-trigger-active-v1.flag"
    if mp_flag.is_file() and not main_problem_row.get("triggered"):
        code_mp2, out_mp2 = _run(
            [PY, str(SCRIPTS / "main_problem_trigger_v1.py"), "--activate", "--json"]
        )
        mp_refresh = json.loads(out_mp2[out_mp2.find("{") :]) if "{" in out_mp2 else {}
        steps.append(
            {
                "step": "main_problem_prepare_active",
                "ok": bool(mp_refresh.get("ok")),
                "exit": code_mp2,
                "mode": "PREPARE_NOT_REPORT",
                "next_action": mp_refresh.get("next_action"),
                "line": (mp_refresh.get("main_problem_line") or "")[:120],
            }
        )
        if not main_problem_row:
            main_problem_row = mp_refresh

    gate_id = f"ASG-{datetime.now(timezone.utc).strftime('%Y%m%d')}-{uuid.uuid4().hex[:8]}"
    receipt = {
        "schema": "agent-session-gate-receipt-v1.1",
        "ok": ok,
        "gate_id": gate_id,
        "at": _now(),
        "role": role,
        "steps": steps,
        "conduct": {
            "ok": conduct.get("ok"),
            "warnings": conduct.get("warnings") or [],
            "violations": conduct.get("violations") or [],
            "read_order_ok": conduct.get("read_order_ok"),
            "limits": conduct.get("limits") or {},
            "main_problem_trigger": main_problem_row if main_problem_row.get("triggered") else None,
            "next_task_trigger": next_task_row
            if (next_task_row.get("triggered") or next_task_row.get("always_apply"))
            else None,
            "incident_041": "Mac founder session: read session gate receipt + truth bundle once; never spawn audit-of-audit loops.",
            "mac_read_once": [
                str(RECEIPT),
                str(TRUTH_CACHE),
            ],
            "mac_forbidden": [
                "governance_zero_drift_live_wire --tier full",
                "audit-of-audit loops",
                "poison scrub --all mid-turn",
                "validate-* && validate-* chains",
            ],
            "deprecate_doc": "brain-os/law/enforcement/SOURCEA_MAC_READ_PATHS_ONLY_LOCKED_v1.md",
        },
        "mirror_hash8": mirror.get("mirror_hash8"),
        "mirror_path": str(MIRROR_PATH),
        "truth_bundle_mode": bundle.get("mode"),
        "inject": bundle.get("inject") or mirror.get("inject"),
        "law_doc": "SOURCEA_AGENTIC_ENFORCEMENT_STACK_LOCKED_v2.md",
        "law_doc_legacy": "AGENT_MEMORY_MIRROR_ENFORCEMENT_LOCKED_v1.md",
        "receipt_path": str(RECEIPT),
        "stack_version": 2,
        "mode": "mac_focus_freeze" if focus_freeze and not pre_ship else ("pre_ship" if pre_ship else "session_start"),
    }
    if not pre_ship:
        receipt["pipelines_policy"] = {
            "session_start": "agent_session_gate_run_v1.py only",
            "forbidden_on_session_start": ["orientation", "hospital", "maze"],
            "founder_triggers": ["orientation", "hospital", "maze"],
            "law": "AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md",
        }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if not pre_ship:
        try:
            from mac_spine_bridge_v1 import dual_write_mac_truth  # noqa: WPS433

            spine_gate = dual_write_mac_truth(
                "MAC_SESSION_GATE",
                payload={
                    **receipt,
                    "mac_spine_fresh": mac_spine_fresh or None,
                    "mac_spine_heartbeat": mac_spine_hb or None,
                },
                receipt_id=str(receipt.get("gate_id") or ""),
            )
            receipt["mac_spine_truth_log"] = spine_gate
            RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception:
            pass

    if not pre_ship:
        try:
            from agent_session_cost_v1 import post_session_cost_receipt  # noqa: WPS433

            agent_id = f"cursor-{role}" if role != "any" else "cursor"
            cost_row = post_session_cost_receipt(
                agent_id=agent_id,
                role=role,
                step_count=len(steps),
                gate_id=str(receipt.get("gate_id") or ""),
            )
            receipt["session_cost"] = cost_row
            steps.append(
                {
                    "step": "agent_session_cost",
                    "ok": bool(cost_row.get("ok")),
                    "tier": cost_row.get("tier"),
                    "usd_marginal": cost_row.get("usd_marginal"),
                    "usd_list_equiv": cost_row.get("usd_list_equiv"),
                    "receipt_path": cost_row.get("receipt_path"),
                    "law": "L17 W3",
                }
            )
            RECEIPT.write_text(json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except Exception as exc:
            steps.append({"step": "agent_session_cost", "ok": False, "error": str(exc)[:200], "law": "L17"})

    try:
        from governance_event_spine_v1 import append_event  # noqa: WPS433

        append_event(
            event_type="AGENT_SESSION_GATE",
            object_id=f"agent_session_gate:{gate_id}",
            object_kind="system",
            agent_id=role if role != "any" else "cursor",
            law_id="AGENTIC_ENFORCEMENT_V2",
            skill_id="agent-memory-mirror",
            validator_set=["validate-agentic-enforcement-stack-v2-v1.sh"],
            affected_objects=[f"receipt:{RECEIPT.name}"],
            payload={
                "ok": ok,
                "role": role,
                "conduct_warnings": len(conduct.get("warnings") or []),
                "conduct_violations": len(conduct.get("violations") or []),
                "mirror_hash8": mirror.get("mirror_hash8"),
            },
            projection_targets=["hub", "monitor"],
            gate="agent_session_gate_run_v1",
            proof=str(RECEIPT),
            status="committed" if ok else "rejected",
        )
    except Exception:
        pass

    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Agent session gate — all chats")
    ap.add_argument(
        "--role",
        default="any",
        choices=["any", "brain", "worker", "archive", "maintainer", "researcher", "governance", "commercial", "brief"],
    )
    ap.add_argument("--scan-text", default="")
    ap.add_argument("--pre-ship", action="store_true", help="Fast reply check — conduct + worker entry only")
    ap.add_argument("--worker-wire", action="store_true", help="Run SourceA Worker connected gate tier")
    ap.add_argument("--graph-tier", action="store_true", help="Run pipeline node graph session tiers T0-T3")
    ap.add_argument("--ecosystem-wire", action="store_true", help="Run full ecosystem connected gate")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    receipt = run_gate(
        args.role,
        scan_text=args.scan_text or "",
        pre_ship=args.pre_ship,
        worker_wire=args.worker_wire,
        graph_tier=args.graph_tier,
        ecosystem_wire=args.ecosystem_wire,
    )
    if args.scan_text:
        try:
            from founder_intent_approval_machine_v1 import classify_intent  # noqa: WPS433

            intent = classify_intent(args.scan_text)
            if intent == "ambiguous":
                subprocess.run(
                    [
                        sys.executable,
                        str(Path(__file__).resolve().parents[1] / "scripts" / "uncertainty_research_enqueue_v1.py"),
                        "--question",
                        args.scan_text[:500],
                        "--intent",
                        intent,
                        "--json",
                    ],
                    cwd=str(Path(__file__).resolve().parents[1]),
                    timeout=30,
                    check=False,
                )
                receipt["uncertainty_enqueued"] = True
        except Exception:
            pass
    if args.json:
        print(json.dumps(receipt, indent=2, ensure_ascii=False))
    else:
        print(f"SESSION_GATE ok={receipt['ok']} gate_id={receipt['gate_id']}")
        print(f"RECEIPT={RECEIPT}")
    return 0 if receipt.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
