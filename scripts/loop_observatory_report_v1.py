#!/usr/bin/env python3
"""Loop Observatory — unified observe/check report (OL1 · OL8 · OL9).

Reads factory-now, run-inbox truth, better-loop, nerve, outbound upgrade pulse,
freeze/resume, prompt composer. Writes ~/.sina/loop-observatory-report-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
RECEIPT = SINA / "loop-observatory-report-v1.json"
COMMERCIAL_COMPILE_ORDER = "SourceA Sina read → Noetfield compile → TrustField send"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _dual_pick() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    try:
        from _ecosystem_safety_dual_pick_check_v1 import dual_pick_check  # noqa: WPS433

        return dual_pick_check()
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def _critical_bugs() -> dict:
    last = _read_json(SINA / "find-bugs" / "last-run.json")
    if last:
        return {
            "critical_count": int(last.get("critical_count") or 0),
            "ok": int(last.get("critical_count") or 0) == 0,
            "path": str(SINA / "find-bugs" / "last-run.json"),
        }
    return {"critical_count": None, "ok": None, "path": str(SINA / "find-bugs" / "last-run.json")}


def _freeze_state(*, fn: dict) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from factory_control_v1 import load_resume_token  # noqa: WPS433
    from worker_inject_lib import act_blocked_by_freeze  # noqa: WPS433

    kill = bool(fn.get("kill_flag"))
    resume = load_resume_token()
    resume_valid = resume is not None
    act = act_blocked_by_freeze(queue_role="act")
    blocked = bool(act.get("prompt_blocked_by_freeze"))
    outbound_override = bool(act.get("outbound_queue_override"))
    cfg = _read_json(SINA / "loop-specialist-config-v1.json")
    orch = _read_json(SINA / "healthy-drain-orchestrator-v1.json")
    action = None
    if blocked:
        sys.path.insert(0, str(SCRIPTS))
        try:
            from outbound_factory_phase_complete_v1 import outbound_plan_progress  # noqa: WPS433
            from execution_path_vocabulary_v1 import execute_line, loop_auto_on  # noqa: WPS433

            if loop_auto_on() and outbound_plan_progress().get("complete"):
                action = execute_line()
            else:
                action = "ASF: Cloud Forge Run — max 1"
        except Exception:
            action = "ASF: Cloud Forge Run — max 1"
    elif outbound_override and bool(cfg.get("loop_auto_dispatch_enabled")):
        try:
            from execution_path_vocabulary_v1 import founder_daily_ops_line  # noqa: WPS433

            action = founder_daily_ops_line()
        except Exception:
            action = "Auto Runtime ON · Brain work-order dispatch · Hub glance only"
    return {
        "kill_flag": kill,
        "mode": str(fn.get("mode") or ""),
        "resume_valid": resume_valid,
        "prompt_blocked_by_freeze": blocked,
        "outbound_queue_override": outbound_override,
        "loop_auto_dispatch_enabled": bool(cfg.get("loop_auto_dispatch_enabled")),
        "orchestrator_status": str(orch.get("status") or "idle"),
        "action": action,
    }


def _founder_action(*, commercial_reds: list[dict], level_gates: dict, commercial_red_map: dict | None = None) -> str:
    sys.path.insert(0, str(SCRIPTS))
    try:
        from execution_path_vocabulary_v1 import commercial_smart_loop_line, post_outbound_smart_loop_active  # noqa: WPS433

        if post_outbound_smart_loop_active():
            gates = (level_gates or {}).get("gates") or {}
            failing = [c.get("id") for c in commercial_reds if not c.get("ok")]
            l3_pct = (level_gates or {}).get("ready_pct")
            bits = []
            if failing:
                bits.append(f"machines clearing {','.join(failing[:3])}")
            if l3_pct is not None:
                bits.append(f"L3 {l3_pct}%")
            suffix = f" · {' · '.join(bits)}" if bits else ""
            return commercial_smart_loop_line() + suffix
    except Exception:
        pass
    gates = (level_gates or {}).get("gates") or {}
    if not gates.get("w3_sina_read"):
        return "fundmore Sina read on fundmore (w3_founder_review --show)"
    failing = [c.get("id") for c in commercial_reds if not c.get("ok")]
    rule_ids = list((commercial_red_map or {}).get("rule_ids") or [])
    if failing:
        base = f"commercial gate: {','.join(failing[:3])}"
        if rule_ids:
            shown = ",".join(rule_ids[:4])
            return f"{base} · rules={shown}"
        return base
    if not gates.get("w3_send_ready"):
        return "complete L3 Founder Send Loop gates (no auto-send)"
    return "commercial compile ready — founder ship authority only"


def _founder_one_line(
    *,
    fn: dict,
    freeze: dict,
    dual: dict,
    bl: dict,
    pulse: dict,
    inbox_pending: bool,
    icp: dict,
) -> str:
    queue_sa = str(fn.get("queue_sa") or "idle")
    mode = str(fn.get("mode") or "?")
    sys_red = int(bl.get("system_red_count") or 0)
    comm_red = int(bl.get("commercial_red_count") or 0)
    red_bit = f"{sys_red} sys · {comm_red} commercial" if comm_red else f"{bl.get('red_count', 0)} red"
    wave = pulse.get("active_wave") or "?"
    done = (pulse.get("progress") or {}).get("done_total", "?")
    total = (pulse.get("progress") or {}).get("total", "?")
    l3 = (pulse.get("level_gates") or {}).get("ready_pct", "?")
    compile_bit = COMMERCIAL_COMPILE_ORDER
    icp_pct = icp.get("fleet_compile_pct")
    icp_bit = f" · ICP {icp_pct}%" if icp_pct is not None else ""
    freeze_bit = " · FREEZE blocks ACT" if freeze.get("prompt_blocked_by_freeze") else ""
    inbox_bit = " · INBOX pending" if inbox_pending else ""
    dual_bit = " · dual_pick ok" if dual.get("ok") else " · dual_pick FAIL"
    sys.path.insert(0, str(SCRIPTS))
    try:
        from execution_path_vocabulary_v1 import post_outbound_smart_loop_active  # noqa: WPS433

        if post_outbound_smart_loop_active():
            return (
                f"auto-commercial · outbound complete · queue=idle · {mode} · {red_bit} · "
                f"L3 {l3}% · compile: {compile_bit}{icp_bit}{freeze_bit}{inbox_bit}{dual_bit}"
            )
    except Exception:
        pass
    return (
        f"observe · queue={queue_sa} · {mode} · {red_bit} · "
        f"upgrade {wave} {done}/{total} · L3 {l3}% · "
        f"compile: {compile_bit}{icp_bit}{freeze_bit}{inbox_bit}{dual_bit}"
    )


def run_report(*, write: bool = True) -> dict:
    fn = _read_json(SINA / "factory-now-v1.json")
    truth = _read_json(SINA / "run-inbox-disk-truth-v1.json")
    bl = _read_json(SINA / "better-loop-pulse-receipt-v1.json")
    nerve = _read_json(SINA / "agent-nerve-system-receipt-v1.json")
    pulse = _read_json(SINA / "outbound-factory-upgrade-pulse-v1.json")
    if not pulse or pulse.get("schema") != "outbound-factory-upgrade-pulse-v2":
        sys.path.insert(0, str(SCRIPTS))
        try:
            from outbound_factory_upgrade_pulse_v1 import run_pulse  # noqa: WPS433

            pulse = run_pulse(write=True)
        except Exception:
            pulse = pulse or {}
    inbox = _read_json(SINA / "worker-prompt-inbox-v1.json")
    composer = _read_json(SINA / "prompt-composer-receipt-v1.json")
    zd = _read_json(SINA / "governance-zero-drift-live-wire-v1.json")
    dual = _dual_pick()
    freeze = _freeze_state(fn=fn)
    bugs = _critical_bugs()
    icp = _read_json(ROOT / "data" / "icp-output-compiler-v1.json")
    sys.path.insert(0, str(SCRIPTS))
    try:
        from future_loop_prompt_advisory_circle_v1 import run_advisory  # noqa: WPS433

        advisory = run_advisory(write=True)
    except Exception:
        advisory = _read_json(SINA / "future-loop-prompt-advisory-v1.json")
    specialist = _read_json(SINA / "loop-specialist-tick-receipt-v1.json")
    loop_cfg = _read_json(SINA / "loop-specialist-config-v1.json")
    investigation = _read_json(SINA / "loop-health-investigation-receipt-v1.json")
    judge_loop = _read_json(SINA / "judge-loop" / "latest-verdict-v1.json")

    checks = bl.get("ship_checks") or bl.get("founder_checks") or []
    commercial_reds = [c for c in checks if c.get("class") == "commercial" and not c.get("ok")]
    level_gates = pulse.get("level_gates") or {}
    founder_action = _founder_action(
        commercial_reds=commercial_reds,
        level_gates=level_gates,
        commercial_red_map=bl.get("commercial_red_map") or {},
    )
    if advisory.get("advisory_line") and commercial_reds:
        sys.path.insert(0, str(SCRIPTS))
        try:
            from execution_path_vocabulary_v1 import post_outbound_smart_loop_active  # noqa: WPS433

            if not post_outbound_smart_loop_active():
                founder_action = f"{founder_action} · {advisory.get('advisory_line', '')[:80]}"
        except Exception:
            founder_action = f"{founder_action} · {advisory.get('advisory_line', '')[:80]}"

    queue_sa = str(fn.get("queue_sa") or (truth.get("queue") or {}).get("sa_id") or "")
    inbox_pending = bool(inbox.get("pending"))

    row = {
        "schema": "loop-observatory-report-v1",
        "ok": bool(dual.get("ok")) and bugs.get("ok") is not False,
        "at": _now(),
        "law": "docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md",
        "system": {
            "gate_ok": bl.get("ok"),
            "drift_score": zd.get("drift_score"),
            "drift_items": zd.get("drift_items"),
            "nerve_aligned": nerve.get("queue_aligned"),
            "critical_bugs": bugs,
            "factory_now_line": fn.get("line") or "",
        },
        "product": {
            "queue_sa": queue_sa,
            "dual_pick": dual,
            "inbox_pending": inbox_pending,
            "prompt_composer": {
                "at": composer.get("at"),
                "sa_id": composer.get("sa_id"),
                "blocked": composer.get("blocked"),
            },
        },
        "commercial": {
            "system_red_count": bl.get("system_red_count"),
            "commercial_red_count": bl.get("commercial_red_count"),
            "product_red_count": bl.get("product_red_count"),
            "reds": [c for c in checks if not c.get("ok")],
            "level_gates": level_gates,
            "compile_order": COMMERCIAL_COMPILE_ORDER,
            "icp_compiler": {
                "present": bool(icp),
                "fleet_compile_pct": icp.get("fleet_compile_pct"),
                "path": str(ROOT / "data" / "icp-output-compiler-v1.json"),
            },
            "founder_action": founder_action,
        },
        "freeze": freeze,
        "loop_specialist": {
            "tick_decision": specialist.get("tick_decision"),
            "loop_specialist_line": specialist.get("loop_specialist_line"),
            "loop_auto_dispatch_enabled": loop_cfg.get("loop_auto_dispatch_enabled"),
        },
        "advisory": {
            "deterministic_hash": advisory.get("deterministic_hash"),
            "advisory_line": advisory.get("advisory_line"),
            "ranked_prompts": advisory.get("ranked_prompts") or [],
            "compile_sequence": advisory.get("compile_sequence") or COMMERCIAL_COMPILE_ORDER,
            "path": str(SINA / "future-loop-prompt-advisory-v1.json"),
        },
        "investigator": {
            "investigation_verdict": investigation.get("investigation_verdict"),
            "investigator_line": investigation.get("investigator_line"),
            "specialist_routes_count": len(investigation.get("specialist_routes") or []),
            "path": str(SINA / "loop-health-investigation-receipt-v1.json"),
        },
        "judge_room": {
            "loop_verdict": judge_loop.get("loop_verdict"),
            "judge_loop_line": judge_loop.get("judge_loop_line"),
            "specialist_reports_count": len(judge_loop.get("specialist_reports") or []),
            "path": str(SINA / "judge-loop" / "latest-verdict-v1.json"),
        },
        "outbound_upgrade": {
            "pulse_line": pulse.get("pulse_line"),
            "maturity_level": pulse.get("maturity_level"),
            "active_wave": pulse.get("active_wave"),
            "progress": pulse.get("progress"),
        },
        "founder_one_line": "",
        "command": "python3 scripts/loop_observatory_report_v1.py --json",
    }
    row["founder_one_line"] = _founder_one_line(
        fn=fn,
        freeze=freeze,
        dual=dual,
        bl=bl,
        pulse=pulse,
        inbox_pending=inbox_pending,
        icp=icp,
    )
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Loop Observatory unified report")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--no-write", action="store_true")
    args = ap.parse_args()
    row = run_report(write=not args.no_write)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("founder_one_line") or "loop-observatory ok")
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
