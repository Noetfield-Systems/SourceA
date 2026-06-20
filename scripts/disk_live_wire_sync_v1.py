#!/usr/bin/env python3
"""Unified disk live wire — truth bundle + live surfaces + mirror sync (INCIDENT-034).

Law: AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md
Receipt: ~/.sina/disk-live-wire-receipt-v1.json
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
ROOT = SCRIPTS.parent
SINA = Path.home() / ".sina"
RECEIPT = SINA / "disk-live-wire-receipt-v1.json"
TRUTH_CACHE = SINA / "last-truth-bundle-v1.json"
AGENT_SURFACES = SINA / "agent-live-surfaces-v1.json"
BRAIN_SURFACES = SINA / "brain" / "BRAIN_LIVE_SURFACES_v1.json"
PY = sys.executable


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


def _sascip_line() -> str:
    path = SINA / "stranger-agent-monitor-v1.json"
    if not path.is_file():
        return ""
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        return str(row.get("one_line") or "")
    except (OSError, json.JSONDecodeError):
        return ""


def _zero_drift_line() -> str:
    path = SINA / "governance-zero-drift-live-wire-v1.json"
    if not path.is_file():
        return ""
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        return str(row.get("zero_drift_line") or "")
    except (OSError, json.JSONDecodeError):
        return ""


def _voyage_line() -> str:
    path = SINA / "voyage-ai-live-wire-v1.json"
    if not path.is_file():
        return ""
    try:
        row = json.loads(path.read_text(encoding="utf-8"))
        return str(row.get("voyage_line") or "")
    except (OSError, json.JSONDecodeError):
        return ""


def _maze_line() -> str:
    receipt = SINA / "agent-maze-receipt-v1.json"
    if not receipt.is_file():
        return ""
    try:
        sys.path.insert(0, str(SCRIPTS))
        from agent_three_pipelines_lib_v1 import maze_status_line  # noqa: WPS433

        row = json.loads(receipt.read_text(encoding="utf-8"))
        line = str(row.get("maze_status_line") or "").strip()
        return line or maze_status_line(receipt=row)
    except (OSError, json.JSONDecodeError, ImportError):
        return ""


def _best_loop_oqg_line() -> str:
    receipt = SINA / "best-loop-oqg-receipt-v1.json"
    if receipt.is_file():
        try:
            row = json.loads(receipt.read_text(encoding="utf-8"))
            line = str(row.get("best_loop_oqg_line") or "").strip()
            if line:
                return line
        except (OSError, json.JSONDecodeError):
            pass
    try:
        code, out = _run([PY, str(SCRIPTS / "best_loop_oqg_score_v1.py"), "--json"])
        if code == 0 and "{" in out:
            row = json.loads(out[out.find("{") :])
            return str(row.get("best_loop_oqg_line") or "")
    except (json.JSONDecodeError, ValueError):
        return ""
    return ""


def _better_loop_line() -> str:
    receipt = SINA / "better-loop-pulse-receipt-v1.json"
    if receipt.is_file():
        try:
            row = json.loads(receipt.read_text(encoding="utf-8"))
            line = str(row.get("better_loop_line") or "").strip()
            if line:
                return line
        except (OSError, json.JSONDecodeError):
            pass
    try:
        code, out = _run([PY, str(SCRIPTS / "better_loop_pulse_v1.py"), "--json"])
        if code == 0 and "{" in out:
            row = json.loads(out[out.find("{") :])
            return str(row.get("better_loop_line") or "")
    except (json.JSONDecodeError, ValueError):
        return ""
    return ""


def _cil_fleet_surfaces() -> dict:
    """U050 — fleet CIL avg quoted on agent-live-surfaces."""
    receipt = SINA / "cil-fleet-receipt-v1.json"
    row: dict = {}
    if receipt.is_file():
        try:
            row = json.loads(receipt.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            row = {}
    if not row or row.get("schema") != "cil-fleet-receipt-v1":
        try:
            code, out = _run([PY, str(SCRIPTS / "conversation_interest_loop_v1.py"), "--fleet", "--json"])
            if code == 0 and "{" in out:
                row = json.loads(out[out.find("{") :])
        except (json.JSONDecodeError, ValueError):
            row = {}
    line = str(row.get("cil_fleet_line") or "").strip()
    pct = row.get("conversation_interest_avg_pct")
    try:
        pct_int = int(pct) if pct is not None else None
    except (TypeError, ValueError):
        pct_int = None
    return {
        "line": line,
        "pct": pct_int,
        "meta": {
            "receipt": str(receipt),
            "law": "docs/SOURCEA_FOUNDER_EMAIL_FACTORY_v2_SPEC_LOCKED_v1.md",
            "fleet": "scripts/conversation_interest_loop_v1.py --fleet",
            "bar": row.get("quality_bar_pct"),
            "ok": row.get("ok"),
            "upgrade": "U050",
        },
    }


def _thread_room_line() -> str:
    try:
        sys.path.insert(0, str(SCRIPTS))
        from worker_hub_daily_rooms_v1 import thread_room_pin  # noqa: WPS433

        pin = thread_room_pin()
        arcs = pin.get("arcs_preview") or []
        arc_str = ",".join(str(a) for a in arcs[:4]) if arcs else "none"
        age = pin.get("age_sec")
        age_bit = f"{round(float(age) / 3600, 1)}h" if age is not None else "?"
        run_due = "run_due" if pin.get("run_due") else "fresh"
        return (
            f"THREAD ROOM · {pin.get('case_id') or '?'} · "
            f"{pin.get('arc_count') or 0} arcs · {arc_str} · "
            f"drafts={pin.get('thread_drafts') or 0} · age={age_bit} · {run_due} · H2"
        )
    except Exception:
        return ""


def _founder_daily_ops_line() -> str:
    try:
        sys.path.insert(0, str(SCRIPTS))
        from execution_path_vocabulary_v1 import founder_daily_ops_line  # noqa: WPS433

        return founder_daily_ops_line()
    except Exception:
        return "Loop specialist tick on Hub · ASF resume drain if FREEZE"


def _form_official_line() -> str:
    try:
        sys.path.insert(0, str(SCRIPTS))
        from live_founder_decision_form_v1 import form_official_line  # noqa: WPS433

        return form_official_line()
    except Exception:
        wire = _read_json(SINA / "form-official-wire-receipt-v1.json")
        return str(wire.get("form_official_line") or "")


def _surfaces_from_bundle(bundle: dict) -> dict:
    fn = bundle.get("factory_now") or {}
    inject = bundle.get("inject") or {}
    sascip = _sascip_line()
    zero_drift = _zero_drift_line()
    voyage = _voyage_line()
    maze = _maze_line()
    thread_room = _thread_room_line()
    surfaces = {
        "schema": "agent-live-surfaces-v1",
        "synced_at": _now(),
        "law": "AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md",
        "factory_now_line": bundle.get("factory_now_line") or "",
        "mode": fn.get("mode") or "",
        "queue_sa": fn.get("queue_sa") or "",
        "dual_pick": bundle.get("dual_pick") or {},
        "h1_daily": {
            "name": "Worker Hub (H1 Daily Necessities)",
            "url": "http://127.0.0.1:13020/",
            "api": "GET /api/worker-hub/v1",
        },
        "h2_machines": {
            "name": "Machine Hub (H2)",
            "url": "http://127.0.0.1:13020/machines/",
        },
        "founder_daily_ops": _founder_daily_ops_line(),
        "next_steps": {
            "disk": str(SINA / "live-ongoing-prompts-next-10-v1.json"),
            "law": "SOURCEA_LIVE_ONGOING_PROMPTS_LOCKED_v1.md",
        },
        "inject_execution_path": inject.get("execution_path") or "",
        "truth_bundle_at": bundle.get("at") or "",
    }
    if sascip:
        surfaces["sascip_line"] = sascip
        surfaces["stranger_agent_monitor"] = {
            "path": str(SINA / "stranger-agent-monitor-v1.json"),
            "url": "http://127.0.0.1:13024/",
        }
    if zero_drift:
        surfaces["zero_drift_line"] = zero_drift
        surfaces["governance_live_wire"] = {
            "path": str(SINA / "governance-zero-drift-live-wire-v1.json"),
            "law": "governance_zero_drift_live_wire_v1.py",
        }
    if voyage:
        surfaces["voyage_line"] = voyage
        surfaces["voyage_ai"] = {
            "path": str(SINA / "voyage-ai-live-wire-v1.json"),
            "api": "GET /api/vector-retrieval-v1",
            "law": "voyage_ai_live_wire_v1.py",
        }
    if maze:
        surfaces["maze_line"] = maze
        surfaces["maze_pipeline"] = {
            "receipt": str(SINA / "agent-maze-receipt-v1.json"),
            "passport": str(SINA / "agent-maze-passport-v1.json"),
            "quarantine": str(SINA / "agent-maze-quarantine-v1.json"),
            "law": "AGENT_THREE_PIPELINES_ORIENTATION_HOSPITAL_MAZE_LOCKED_v1.md",
            "founder_word": "maze",
            "not_session_start": True,
        }
    better_loop = _better_loop_line()
    if better_loop:
        surfaces["better_loop_line"] = better_loop
        surfaces["better_loop"] = {
            "receipt": str(SINA / "better-loop-pulse-receipt-v1.json"),
            "checkcart": str(SINA / "better-loop-checkcart-v1.json"),
            "law": "docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md",
            "pulse": "scripts/better_loop_pulse_v1.py",
        }
    oqg_line = _best_loop_oqg_line()
    if oqg_line:
        surfaces["best_loop_oqg_line"] = oqg_line
        surfaces["best_loop_oqg"] = {
            "receipt": str(SINA / "best-loop-oqg-receipt-v1.json"),
            "law": "docs/SOURCEA_BEST_LOOP_OUTPUT_QUALITY_GATE_LOCKED_v1.md",
            "score": "scripts/best_loop_oqg_score_v1.py",
            "metric": "output_clean_pct",
            "bar": 90,
        }
    cil_fleet = _cil_fleet_surfaces()
    if cil_fleet.get("line") and cil_fleet.get("pct") is not None:
        surfaces["cil_fleet_line"] = cil_fleet["line"]
        surfaces["cil_fleet_pct"] = cil_fleet["pct"]
        surfaces["cil_fleet"] = cil_fleet["meta"]
    if thread_room:
        surfaces["thread_room_line"] = thread_room
        surfaces["thread_room"] = {
            "spine": str(SINA / "thread-room/latest-curation-v1.json"),
            "map": str(SINA / "thread-room/latest-map-v1.json"),
            "law": "SINA_THREAD_ROOM_LOCKED_v1.md",
            "h2_url": "http://127.0.0.1:13020/machines/",
            "h1_rule": "one_line_only — full map on H2",
            "cadence": "weekly run · daily read every session",
            "activate_api": "POST /api/worker-hub/rooms/run body room=thread",
        }
    try:
        sys.path.insert(0, str(SCRIPTS))
        from execution_plane_honesty_v1 import assess_commercial_readiness, assess_execution_plane  # noqa: WPS433

        exec_row = assess_execution_plane()
        comm_row = assess_commercial_readiness()
        if exec_row.get("execution_honesty_line"):
            surfaces["execution_honesty_line"] = exec_row["execution_honesty_line"]
            surfaces["execution_plane"] = {
                "ok": exec_row.get("ok"),
                "receipt": "scripts/execution_plane_honesty_v1.py",
                "checks": exec_row.get("checks"),
            }
        if comm_row.get("commercial_readiness_line"):
            surfaces["commercial_readiness_line"] = comm_row["commercial_readiness_line"]
            surfaces["commercial_plane"] = {
                "ready_pct": comm_row.get("ready_pct"),
                "gates": comm_row.get("gates"),
                "receipt": str(SINA / "commercial-command-pulse-v1.json"),
            }
        from agent_rule_live_wire_v1 import pulse_registry_to_surfaces  # noqa: WPS433

        pulse_registry_to_surfaces(surfaces, write=True)
        from anti_theater_validator_loop_v1 import run_loop as anti_theater_run  # noqa: WPS433

        at_row = anti_theater_run(write=True)
        if at_row.get("anti_theater_line"):
            surfaces["anti_theater_line"] = at_row["anti_theater_line"]
            surfaces["anti_theater_loop"] = {
                "ok": at_row.get("ok"),
                "receipt": str(SINA / "anti-theater-validator-loop-receipt-v1.json"),
                "passed": at_row.get("passed"),
                "total": at_row.get("total"),
                "sina_pending": at_row.get("sina_pending"),
            }
        from agent_behavior_settings_v1 import sync_receipt as behavior_sync  # noqa: WPS433

        beh = behavior_sync(write=True)
        if beh.get("behavior_line"):
            surfaces["behavior_line"] = beh["behavior_line"]
            surfaces["agent_behavior"] = {
                "ok": beh.get("ok"),
                "receipt": str(SINA / "agent-behavior-settings-receipt-v1.json"),
                "one_law": beh.get("one_law"),
                "ssot": "data/agent-behavior-settings-v1.json",
            }
        mp_receipt = SINA / "main-problem-trigger-receipt-v1.json"
        mp_flag = SINA / "main-problem-trigger-active-v1.flag"
        if mp_flag.is_file() and mp_receipt.is_file():
            try:
                mp_row = json.loads(mp_receipt.read_text(encoding="utf-8"))
                if mp_row.get("main_problem_line"):
                    surfaces["main_problem_line"] = mp_row["main_problem_line"]
                    surfaces["main_problem_trigger"] = {
                        "active": True,
                        "mode": mp_row.get("mode"),
                        "next_action": mp_row.get("next_action"),
                        "receipt": str(mp_receipt),
                        "ssot": "data/sourcea-main-problem-trigger-v1.json",
                    }
            except (OSError, json.JSONDecodeError):
                pass
        from cloud_comprehension_pipeline_loop_v1 import inject_slice as comprehension_inject  # noqa: WPS433

        comp_inj = comprehension_inject()
        if comp_inj.get("output_quality_line") or comp_inj.get("comprehension_line"):
            if comp_inj.get("output_quality_line"):
                surfaces["output_quality_line"] = comp_inj["output_quality_line"]
            if comp_inj.get("comprehension_line"):
                surfaces["comprehension_line"] = comp_inj["comprehension_line"]
            surfaces["comprehension_pipeline"] = {
                "circles": "C1→C7",
                "output_verdicts": "ACCEPT|RETURN_TO_AGENT|FIX_DISK|FIX_MACHINES",
                "one_law": comp_inj.get("one_law"),
                "ssot": "data/cloud-comprehension-pipeline-loop-v1.json",
            }
        from factory_cost_intelligence_v1 import sync_receipt as cost_intel_sync  # noqa: WPS433

        ci = cost_intel_sync(write=True)
        if ci.get("cost_intelligence_line"):
            surfaces["cost_intelligence_line"] = ci["cost_intelligence_line"]
            surfaces["factory_cost_intelligence"] = {
                "ok": ci.get("ok"),
                "receipt": str(SINA / "factory-cost-intelligence-receipt-v1.json"),
                "registry_count": ci.get("registry_count"),
                "wef_gln_total": ci.get("wef_gln_total"),
                "ssot": "data/factory-cost-intelligence-loop-v1.json",
            }
        from outbound_queue_coherence_v1 import assess_queue_coherence, compose_outbound_progress_line  # noqa: WPS433

        coh = assess_queue_coherence()
        surfaces["outbound_progress_line"] = compose_outbound_progress_line()
        surfaces["outbound_factory"] = {
            "done": coh.get("outbound_done"),
            "total": coh.get("outbound_total"),
            "head": coh.get("head"),
            "coherence_ok": coh.get("ok"),
            "receipt": "scripts/outbound_queue_coherence_v1.py",
        }
    except Exception:
        pass
    form_line = _form_official_line()
    if form_line:
        surfaces["form_official_line"] = form_line
        try:
            from form_official_canvas_route_v1 import hub_canvas_target  # noqa: WPS433

            route = hub_canvas_target()
            canvas_path = str(route.get("path") or "")
            hub_label = str(route.get("button_label") or "FORM_OFFICIAL (M1 Canvas)")
        except Exception:
            canvas_path = str(
                Path.home()
                / ".cursor/projects/Users-sinakazemnezhad-Desktop-SinaaiDataBase/canvases/sourcea-system-integrity-100.canvas.tsx"
            )
            hub_label = "FORM_OFFICIAL (M1 Canvas)"
            route = {}
        surfaces["form_official"] = {
            "receipt": str(SINA / "form-official-wire-receipt-v1.json"),
            "nerve_map": str(ROOT / "data/form_official_nerve_map_v1.json"),
            "wire": "scripts/form_official_wire_e2e_v1.py",
            "route": "scripts/form_official_canvas_route_v1.py",
            "canvas": canvas_path,
            "hub_action": hub_label,
            "hub_url": str(route.get("hub_url") or "http://127.0.0.1:13020/"),
            "h2_machines_url": str(route.get("h2_machines_url") or "http://127.0.0.1:13020/machines/"),
            "museum_url": str(route.get("museum_url") or "http://127.0.0.1:13020/legacy/"),
            "form_action_id": str(route.get("form_action_id") or "founder-open-integrity-form"),
            "form_hub_line": str(route.get("form_hub_line") or ""),
            "law": "INCIDENT-029 · INTEGRITY PACK 5 slot D",
        }
    try:
        ufc_path = SINA / "ui-upgrade-first-check-receipt-v1.json"
        if ufc_path.is_file():
            ufc = json.loads(ufc_path.read_text(encoding="utf-8"))
            if ufc.get("line"):
                surfaces["ui_upgrade_first_check_line"] = ufc["line"]
            surfaces["ui_upgrade_first_check"] = {
                "receipt": str(ufc_path),
                "ok": bool(ufc.get("wire_ok")),
                "law": "SOURCEA_UI_UPGRADE_MANDATORY_PROCESS_LOCKED_v1.md",
                "surfaces_count": 7,
                "validator": "scripts/validate-ui-upgrade-first-check-live-wire-v1.sh",
                "ack_cmd": "python3 scripts/ui_upgrade_first_check_v1.py --surface <id> --ack --json",
            }
    except Exception:
        pass
    return surfaces


_L1_WIRE_ROLES = frozenset({"commercial", "governance", "brief"})


def _normalize_wire_role(role: str) -> str:
    """L1 specialist chats use same wire path as any (INCIDENT-034 / PT-P0-S1)."""
    if role in _L1_WIRE_ROLES:
        return "any"
    return role


def sync_disk_live_wire(*, role: str = "any", skip_factory: bool = False) -> dict:
    role = _normalize_wire_role(role)
    sys.path.insert(0, str(SCRIPTS))
    steps: list[dict] = []
    ok = True

    if not skip_factory:
        code, _ = _run([PY, str(SCRIPTS / "active_now_sync_from_factory_now_v1.py"), "--json"])
        step_ok = code == 0
        steps.append({"step": "active_now_sync", "ok": step_ok, "exit": code})
        ok = ok and step_ok

    from agent_truth_bundle_v1 import build_agent_truth_bundle  # noqa: WPS433

    bundle = build_agent_truth_bundle()
    SINA.mkdir(parents=True, exist_ok=True)
    TRUTH_CACHE.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
    steps.append({"step": "truth_bundle", "ok": bundle.get("schema") == "agent-truth-bundle-v1"})

    surfaces = _surfaces_from_bundle(bundle)
    AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
    steps.append({"step": "agent_live_surfaces", "ok": True, "path": str(AGENT_SURFACES)})

    if role in ("brain", "any"):
        brain_surfaces = dict(surfaces)
        brain_surfaces["schema"] = "brain-live-surfaces-v1"
        BRAIN_SURFACES.parent.mkdir(parents=True, exist_ok=True)
        BRAIN_SURFACES.write_text(json.dumps(brain_surfaces, indent=2) + "\n", encoding="utf-8")
        master = SINA / "brain" / "BRAIN_MASTER_MEMORY_LOCKED_v1.md"
        if master.is_file():
            text = master.read_text(encoding="utf-8")
            marker = "## LIVE SURFACES (auto-sync — do not hand-edit)"
            block = (
                f"{marker}\n\n"
                f"**Synced:** `{surfaces['synced_at']}` · **Law:** `AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md`\n\n"
                f"```json\n{json.dumps(brain_surfaces, indent=2)}\n```\n"
            )
            if marker in text:
                head, _, _ = text.partition(marker)
                text = head.rstrip() + "\n\n" + block
            else:
                text = text.rstrip() + "\n\n" + block
            master.write_text(text, encoding="utf-8")
        steps.append({"step": "brain_live_surfaces", "ok": True, "path": str(BRAIN_SURFACES)})

    mac_law_ok = False
    try:
        sys.path.insert(0, str(SCRIPTS))
        from mac_law_universal_wire_v1 import sync_receipt as mac_universal_sync  # noqa: WPS433
        from mac_law_agent_execution_plane_lock_v1 import sync_receipt as mac_lock_sync  # noqa: WPS433

        mu = mac_universal_sync(enforce=False)
        ml = mac_lock_sync(enforce=False)
        mac_law_ok = bool(mu.get("ok")) and bool(ml.get("ok"))
        surfaces = _read_json(AGENT_SURFACES)
        if mu.get("line"):
            surfaces["mac_law_universal_line"] = mu["line"]
        if ml.get("line"):
            surfaces["mac_law_agent_lock_line"] = ml["line"]
        surfaces["mac_law_agent_no_factory_on_mac"] = bool(ml.get("ok"))
        AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "mac_law_agent_execution_plane_lock",
                "ok": mac_law_ok,
                "universal_ok": bool(mu.get("ok")),
                "lock_ok": bool(ml.get("ok")),
            }
        )
        ok = ok and mac_law_ok
    except Exception as exc:
        steps.append({"step": "mac_law_agent_execution_plane_lock", "ok": False, "error": str(exc)})
        ok = False

    nerve_ok = False
    nerve_line = ""
    try:
        sys.path.insert(0, str(SCRIPTS))
        from agent_nerve_system_v1 import run_nerve_pulse, patch_surfaces  # noqa: WPS433

        nerve = run_nerve_pulse(write=True)
        patch_surfaces(row=nerve)
        nerve_ok = bool(nerve.get("ok"))
        nerve_line = str(nerve.get("nerve_system_line") or "")
        surfaces = _read_json(AGENT_SURFACES)
        steps.append(
            {
                "step": "nerve_system_pulse",
                "ok": nerve_ok,
                "queue_aligned": nerve.get("queue_aligned"),
                "nerve_system_line": nerve_line[:120],
            }
        )
        ok = ok and nerve_ok
    except Exception as exc:
        steps.append({"step": "nerve_system_pulse", "ok": False, "error": str(exc)})
        ok = False

    observatory_ok = False
    observatory_line = ""
    try:
        from loop_observatory_report_v1 import run_report  # noqa: WPS433

        obs = run_report(write=True)
        observatory_ok = bool(obs.get("ok"))
        observatory_line = str(obs.get("founder_one_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if observatory_line:
            surfaces["loop_observatory_line"] = observatory_line
            surfaces["loop_observatory"] = {
                "receipt": str(SINA / "loop-observatory-report-v1.json"),
                "law": "docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md",
                "pulse": "scripts/loop_observatory_report_v1.py",
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "loop_observatory_report",
                "ok": observatory_ok,
                "founder_one_line": observatory_line[:120],
            }
        )
        ok = ok and observatory_ok
    except Exception as exc:
        steps.append({"step": "loop_observatory_report", "ok": False, "error": str(exc)})
        ok = False

    specialist_ok = False
    specialist_line = ""
    try:
        from loop_specialist_tick_v1 import run_tick  # noqa: WPS433

        spec = run_tick(write=True, dispatch=False)
        specialist_ok = bool(spec.get("ok"))
        specialist_line = str(spec.get("loop_specialist_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if specialist_line:
            surfaces["loop_specialist_line"] = specialist_line
            surfaces["loop_specialist"] = {
                "receipt": str(SINA / "loop-specialist-tick-receipt-v1.json"),
                "config": str(SINA / "loop-specialist-config-v1.json"),
                "tick_decision": spec.get("tick_decision"),
                "hub_api": "POST /api/loop-specialist/tick/v1",
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "loop_specialist_tick",
                "ok": specialist_ok,
                "tick_decision": spec.get("tick_decision"),
                "loop_specialist_line": specialist_line[:120],
            }
        )
    except Exception as exc:
        steps.append({"step": "loop_specialist_tick", "ok": False, "error": str(exc)})

    investigator_ok = False
    investigator_line = ""
    try:
        from investigator_circle_run_v1 import run_investigation  # noqa: WPS433

        inv = run_investigation(write=True)
        investigator_ok = bool(inv.get("investigation_verdict"))
        investigator_line = str(inv.get("investigator_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if investigator_line:
            surfaces["investigator_line"] = investigator_line
            surfaces["investigator_room"] = {
                "receipt": str(SINA / "loop-health-investigation-receipt-v1.json"),
                "verdict": inv.get("investigation_verdict"),
                "hub_api": "POST /api/investigator-circle/tick/v1",
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "investigator_circle",
                "ok": investigator_ok,
                "investigation_verdict": inv.get("investigation_verdict"),
                "investigator_line": investigator_line[:120],
            }
        )
    except Exception as exc:
        steps.append({"step": "investigator_circle", "ok": False, "error": str(exc)})

    judge_loop_ok = False
    judge_loop_line = ""
    try:
        from judge_loop_room_v1 import run_judge_loop  # noqa: WPS433

        jv = run_judge_loop(write=True)
        judge_loop_ok = bool(jv.get("loop_verdict"))
        judge_loop_line = str(jv.get("judge_loop_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if judge_loop_line:
            surfaces["judge_loop_line"] = judge_loop_line
            surfaces["judge_room"] = {
                "receipt": str(SINA / "judge-loop" / "latest-verdict-v1.json"),
                "loop_verdict": jv.get("loop_verdict"),
                "hub_api": "POST /api/judge-loop/tick/v1",
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "judge_loop_room",
                "ok": judge_loop_ok,
                "loop_verdict": jv.get("loop_verdict"),
                "judge_loop_line": judge_loop_line[:120],
            }
        )
    except Exception as exc:
        steps.append({"step": "judge_loop_room", "ok": False, "error": str(exc)})

    routing_ok = False
    routing_line = ""
    try:
        from founder_routing_panel_v1 import run_panel  # noqa: WPS433

        rp = run_panel(write=True)
        routing_ok = bool(rp.get("ok"))
        routing_line = str(rp.get("founder_routing_panel_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if routing_line:
            surfaces["founder_routing_panel_line"] = routing_line
            surfaces["routing_panel"] = {
                "receipt": str(SINA / "founder-routing-panel-v1.json"),
                "active_primary": (rp.get("active_route") or {}).get("primary"),
                "loop_verdict": (rp.get("active_route") or {}).get("loop_verdict"),
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "founder_routing_panel",
                "ok": routing_ok,
                "founder_routing_panel_line": routing_line[:120],
            }
        )
    except Exception as exc:
        steps.append({"step": "founder_routing_panel", "ok": False, "error": str(exc)})

    disclosure_ok = False
    disclosure_line = ""
    try:
        from disclosure_ladder_v1 import run_tick  # noqa: WPS433

        dl = run_tick(write=True)
        disclosure_ok = bool(dl.get("wired")) and bool(dl.get("icp_audit_ok", True))
        disclosure_line = str(dl.get("disclosure_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if disclosure_line:
            surfaces["disclosure_line"] = disclosure_line
            surfaces["disclosure_ladder"] = {
                "receipt": str(SINA / "disclosure-ladder-receipt-v1.json"),
                "icp_audit_ok": dl.get("icp_audit_ok"),
                "wired": dl.get("wired"),
                "hub_api": "POST /api/disclosure-ladder/tick/v1",
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "disclosure_ladder",
                "ok": disclosure_ok,
                "disclosure_line": disclosure_line[:120],
                "icp_audit_ok": dl.get("icp_audit_ok"),
            }
        )
    except Exception as exc:
        steps.append({"step": "disclosure_ladder", "ok": False, "error": str(exc)})

    mcp_stack_ok = False
    mcp_stack_line = ""
    try:
        from mcp_stack_free_tier_v1 import run_tick  # noqa: WPS433

        ms = run_tick(write=True)
        mcp_stack_ok = bool(ms.get("wired"))
        mcp_stack_line = str(ms.get("mcp_stack_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if mcp_stack_line:
            surfaces["mcp_stack_line"] = mcp_stack_line
            surfaces["mcp_stack"] = {
                "receipt": str(SINA / "mcp-stack-free-tier-receipt-v1.json"),
                "wired": ms.get("wired"),
                "pending_p0": ms.get("pending_p0"),
                "hub_api": "POST /api/mcp-stack/tick/v1",
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "mcp_stack_free_tier",
                "ok": mcp_stack_ok,
                "mcp_stack_line": mcp_stack_line[:120],
                "pending_p0": ms.get("pending_p0"),
            }
        )
    except Exception as exc:
        steps.append({"step": "mcp_stack_free_tier", "ok": False, "error": str(exc)})

    tool_pick_ok = False
    tool_pick_line = ""
    try:
        from tool_pick_two_phase_v1 import run_tick as tool_pick_tick  # noqa: WPS433

        tp = tool_pick_tick(write=True)
        tool_pick_ok = bool(tp.get("wired"))
        tool_pick_line = str(tp.get("tool_pick_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if tool_pick_line:
            surfaces["tool_pick_line"] = tool_pick_line
            surfaces["tool_pick"] = {
                "receipt": str(SINA / "tool-pick-two-phase-receipt-v1.json"),
                "phase_1_exhaust_pct": (tp.get("phase_1") or {}).get("exhaust_pct"),
                "pending_founder_approval": (tp.get("phase_2") or {}).get("pending_founder_approval"),
                "hub_api": "POST /api/tool-pick/tick/v1",
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "tool_pick_two_phase",
                "ok": tool_pick_ok,
                "tool_pick_line": tool_pick_line[:120],
                "pending_founder_approval": (tp.get("phase_2") or {}).get("pending_founder_approval"),
            }
        )
    except Exception as exc:
        steps.append({"step": "tool_pick_two_phase", "ok": False, "error": str(exc)})

    fix_plan_ok = False
    fix_plan_line = ""
    try:
        from full_stack_fix_plan_pulse_v1 import run_pulse as fix_plan_pulse  # noqa: WPS433

        fp = fix_plan_pulse(write=True)
        fix_plan_ok = bool(fp.get("ok"))
        fix_plan_line = str(fp.get("full_stack_fix_line") or fp.get("pulse_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if fix_plan_line:
            surfaces["full_stack_fix_line"] = fix_plan_line
            surfaces["full_stack_fix_plan"] = {
                "receipt": str(SINA / "full-stack-fix-plan-pulse-v1.json"),
                "plan": str(ROOT / "data" / "sourcea-full-stack-100-fix-plan-v1.json"),
                "active_wave": fp.get("active_wave"),
                "critical_path_head": fp.get("critical_path_head"),
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "full_stack_fix_plan_pulse",
                "ok": fix_plan_ok,
                "full_stack_fix_line": fix_plan_line[:120],
                "active_wave": fp.get("active_wave"),
            }
        )
    except Exception as exc:
        steps.append({"step": "full_stack_fix_plan_pulse", "ok": False, "error": str(exc)})

    brain_cloud_ok = False
    brain_cloud_line = ""
    try:
        from brain_cloud_reasoning_plan_pulse_v1 import run_pulse as brain_cloud_pulse  # noqa: WPS433

        bc = brain_cloud_pulse(write=True)
        brain_cloud_ok = bool(bc.get("ok"))
        brain_cloud_line = str(bc.get("brain_cloud_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if brain_cloud_line:
            surfaces["brain_cloud_line"] = brain_cloud_line
            surfaces["brain_cloud_reasoning"] = {
                "receipt": str(SINA / "brain-cloud-reasoning-plan-pulse-v1.json"),
                "plan": str(ROOT / "data" / "brain-cloud-reasoning-1000-upgrade-plan-v1.json"),
                "active_epic": bc.get("active_epic"),
                "real_blocker": (bc.get("brain_blocker") or {}).get("real"),
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "brain_cloud_reasoning_plan_pulse",
                "ok": brain_cloud_ok,
                "brain_cloud_line": brain_cloud_line[:120],
                "active_epic": bc.get("active_epic"),
            }
        )
    except Exception as exc:
        steps.append({"step": "brain_cloud_reasoning_plan_pulse", "ok": False, "error": str(exc)})

    cloud_practical_300_ok = False
    cloud_practical_300_line = ""
    try:
        from brain_cloud_practical_300_pulse_v1 import run_pulse as cloud_300_pulse  # noqa: WPS433

        c3 = cloud_300_pulse(write=True)
        cloud_practical_300_ok = bool(c3.get("ok"))
        cloud_practical_300_line = str(c3.get("cloud_practical_300_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if cloud_practical_300_line:
            surfaces["cloud_practical_300_line"] = cloud_practical_300_line
            surfaces["cloud_practical_300"] = {
                "receipt": str(SINA / "brain-cloud-practical-300-pulse-v1.json"),
                "plan": str(ROOT / "data" / "brain-cloud-practical-300-plan-v1.json"),
                "head_id": c3.get("head_id"),
                "head_goal": c3.get("head_goal"),
                "plan_version": c3.get("plan_version"),
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "brain_cloud_practical_300_pulse",
                "ok": cloud_practical_300_ok,
                "cloud_practical_300_line": cloud_practical_300_line[:120],
                "head_id": c3.get("head_id"),
            }
        )
    except Exception as exc:
        steps.append({"step": "brain_cloud_practical_300_pulse", "ok": False, "error": str(exc)})

    plans_unified_ok = False
    plans_unified_line = ""
    try:
        from plans_unified_upgrade_v1 import run_upgrade  # noqa: WPS433

        pu = run_upgrade(write=True)
        plans_unified_ok = bool(pu.get("ok"))
        plans_unified_line = str(pu.get("plans_unified_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if plans_unified_line:
            surfaces["plans_unified_line"] = plans_unified_line
            surfaces["plans_unified"] = {
                "receipt": str(SINA / "plans-unified-upgrade-receipt-v1.json"),
                "orchestrator": str(ROOT / "scripts" / "plans_unified_upgrade_v1.py"),
                "outbound": pu.get("outbound"),
                "full_stack": pu.get("full_stack"),
                "brain_cloud": pu.get("brain_cloud"),
                "phase0": pu.get("phase0_check"),
            }
            p0_line = str((pu.get("phase0_check") or {}).get("line") or "")[:160]
            if p0_line:
                surfaces["phase0_line"] = p0_line
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "plans_unified_upgrade",
                "ok": plans_unified_ok,
                "plans_unified_line": plans_unified_line[:120],
            }
        )
    except Exception as exc:
        steps.append({"step": "plans_unified_upgrade", "ok": False, "error": str(exc)})

    wtm_ok = False
    wtm_line = ""
    try:
        from world_model_plan_check_v1 import run_check as wtm_run  # noqa: WPS433

        wtm = wtm_run(write=True)
        wtm_ok = bool(wtm.get("ok"))
        wtm_line = str(wtm.get("world_model_line") or "")[:160]
        surfaces = _read_json(AGENT_SURFACES)
        if wtm_line:
            surfaces["world_model_line"] = wtm_line
            surfaces["world_model_check"] = {
                "receipt": str(SINA / "world-model-plan-check-receipt-v1.json"),
                "ssot": str(ROOT / "data" / "platform-neutral-world-model-v1.json"),
                "advisory_count": wtm.get("advisory_count"),
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append({"step": "world_model_plan_check", "ok": wtm_ok, "world_model_line": wtm_line[:120]})
    except Exception as exc:
        steps.append({"step": "world_model_plan_check", "ok": False, "error": str(exc)})

    brain_outbound_ok = False
    brain_outbound_line = ""
    try:
        active_wo = _read_json(SINA / "brain-outbound-work-order-active-v1.json")
        dispatch_rcpt = _read_json(SINA / "brain-outbound-dispatch-receipt-v1.json")
        brain_outbound_line = str(
            active_wo.get("founder_note")
            or dispatch_rcpt.get("brain_outbound_line")
            or ""
        )[:160]
        if not brain_outbound_line and active_wo.get("work_order_id"):
            ref = active_wo.get("upgrade_ref") or "?"
            pending = "signed" if active_wo.get("pending_cloud_bay") else "PASS"
            brain_outbound_line = (
                f"brain-outbound · {ref} · wo={str(active_wo.get('work_order_id'))[:16]} · "
                f"bay={active_wo.get('bay_slug') or '?'} · {pending} · local_worker=NO"
            )
        brain_outbound_ok = bool(active_wo.get("work_order_id")) or bool(dispatch_rcpt.get("ok"))
        surfaces = _read_json(AGENT_SURFACES)
        if brain_outbound_line:
            surfaces["brain_outbound_line"] = brain_outbound_line
            surfaces["brain_outbound_work_order"] = {
                "receipt": str(SINA / "brain-outbound-work-order-active-v1.json"),
                "dispatch": str(SINA / "brain-outbound-dispatch-receipt-v1.json"),
                "compiler": "scripts/brain_outbound_work_order_v1.py",
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append(
            {
                "step": "brain_outbound_work_order",
                "ok": brain_outbound_ok,
                "brain_outbound_line": brain_outbound_line[:120],
            }
        )
    except Exception as exc:
        steps.append({"step": "brain_outbound_work_order", "ok": False, "error": str(exc)})

    try:
        from cloud_factory_10_steps_v1 import _patch_federated_honesty  # noqa: WPS433

        fed = _patch_federated_honesty()
        steps.append(
            {
                "step": "federated_honesty_patch",
                "ok": bool(fed.get("ok")),
                "remote_status": fed.get("remote_status"),
                "cloud_worker_url": fed.get("cloud_worker_url"),
            }
        )
        ok = ok and bool(fed.get("ok"))
    except Exception as exc:
        steps.append({"step": "federated_honesty_patch", "ok": False, "error": str(exc)})

    code, _ = _run([PY, str(SCRIPTS / "worker_live_context_v1.py"), "--json"])
    worker_ctx_ok = code == 0
    steps.append({"step": "worker_live_context", "ok": worker_ctx_ok, "exit": code})
    ok = ok and worker_ctx_ok

    code, _ = _run([PY, str(SCRIPTS / "brain_live_context_v1.py"), "--json"])
    brain_ctx_ok = code == 0
    steps.append({"step": "brain_live_context", "ok": brain_ctx_ok, "exit": code})
    ok = ok and brain_ctx_ok

    if role in ("brain", "any"):
        code, _ = _run([PY, str(SCRIPTS / "brain_stale_prompt_scrub_v1.py"), "--json"])
        steps.append({"step": "brain_stale_prompt_scrub", "ok": code == 0, "exit": code})

    code, out = _run([PY, str(SCRIPTS / "agent_memory_mirror_v1.py"), "--sync", "--json"])
    mirror = json.loads(out[out.find("{") :]) if "{" in out else {}
    step_ok = code == 0 and mirror.get("validation", {}).get("ok", True)
    steps.append({"step": "memory_mirror_sync", "ok": step_ok, "exit": code})
    ok = ok and step_ok

    try:
        from agent_truth_bundle_v1 import build_agent_truth_bundle  # noqa: WPS433

        bundle = build_agent_truth_bundle()
        TRUTH_CACHE.write_text(json.dumps(bundle, indent=2) + "\n", encoding="utf-8")
        steps.append({"step": "truth_bundle_refresh", "ok": bundle.get("schema") == "agent-truth-bundle-v1"})
    except Exception as exc:
        steps.append({"step": "truth_bundle_refresh", "ok": False, "error": str(exc)})

    try:
        from governance_gate_cart_v1 import run_cart  # noqa: WPS433

        cart = run_cart(tier="fast", write=True)
        cart_line = str(cart.get("cart_line") or "")
        if cart_line:
            surfaces["gate_cart_line"] = cart_line
            surfaces["governance_gate_cart"] = {
                "receipt": str(SINA / "governance-gate-cart-v1.json"),
                "passed": cart.get("passed"),
                "total": cart.get("total"),
            }
            if AGENT_SURFACES.is_file():
                AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        cart_step_ok = bool(cart.get("governance_ok")) and bool(cart.get("execution_plane_ok", True))
        steps.append(
            {
                "step": "governance_gate_cart",
                "ok": cart_step_ok,
                "cart_ok": bool(cart.get("ok")),
                "cart_line": cart_line[:120],
            }
        )
    except Exception as exc:
        steps.append({"step": "governance_gate_cart", "ok": False, "error": str(exc)})

    try:
        from commercial_command_pulse_v1 import run_pulse as commercial_pulse  # noqa: WPS433

        comm = commercial_pulse(write=True)
        comm_line = str(comm.get("pulse_line") or "")
        if comm_line:
            surfaces = _read_json(AGENT_SURFACES)
            surfaces["commercial_command_line"] = comm_line
            surfaces["commercial_command"] = {
                "receipt": str(SINA / "commercial-command-pulse-v1.json"),
                "l3_ready_pct": comm.get("l3_ready_pct"),
            }
            AGENT_SURFACES.write_text(json.dumps(surfaces, indent=2) + "\n", encoding="utf-8")
        steps.append({"step": "commercial_command_pulse", "ok": True, "pulse_line": comm_line[:120]})
    except Exception as exc:
        steps.append({"step": "commercial_command_pulse", "ok": False, "error": str(exc)})

    receipt = {
        "schema": "disk-live-wire-receipt-v1",
        "ok": ok,
        "at": _now(),
        "role": role,
        "law": "AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md",
        "factory_now_line": surfaces.get("factory_now_line") or "",
        "queue_sa": surfaces.get("queue_sa") or "",
        "nerve_system_line": surfaces.get("nerve_system_line") or nerve_line,
        "mode": surfaces.get("mode") or "",
        "paths": {
            "truth_bundle": str(TRUTH_CACHE),
            "agent_surfaces": str(AGENT_SURFACES),
            "brain_surfaces": str(BRAIN_SURFACES) if role in ("brain", "any") else None,
            "mirror": str(SINA / "agent-memory-mirror-v1.json"),
            "worker_live_context": str(SINA / "worker-live-context-v1.json"),
            "brain_live_context": str(SINA / "brain-live-context-v1.json"),
        },
        "steps": steps,
    }
    RECEIPT.write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    return receipt


def main() -> int:
    ap = argparse.ArgumentParser(description="Unified disk live wire sync")
    ap.add_argument(
        "--role",
        default="any",
        choices=["any", "brain", "worker", "maintainer", "archive", "commercial", "governance", "brief"],
    )
    ap.add_argument("--skip-factory", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = sync_disk_live_wire(role=args.role, skip_factory=args.skip_factory)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"DISK_LIVE_WIRE ok={row['ok']} queue={row.get('queue_sa')} line={row.get('factory_now_line', '')[:72]}")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
