#!/usr/bin/env python3
"""Brain live context — disk block Brain must read before founder-facing reply.

Law: AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md · INCIDENT-034 (positive disk, not chat memory)
Output: ~/.sina/brain-live-context-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SINA = Path.home() / ".sina"
OUT = SINA / "brain-live-context-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _queue_exhausted() -> bool:
    hq = _read_json(SINA / "healthy-queue-30-active.json")
    if hq.get("queue_exhausted") or hq.get("phase_strict_complete"):
        return True
    fn = _read_json(SINA / "factory-now-v1.json")
    return (
        int(fn.get("valid_yes") or 0) >= 1000
        and int(fn.get("backlog") or 0) == 0
        and bool(fn.get("dual_proof_ok"))
        and not str(fn.get("queue_sa") or "").strip()
    )


def _ensure_run_inbox_close(line: str) -> str:
    """INCIDENT-034 — founder_close_line must always carry RUN INBOX positive path."""
    text = str(line or "").strip()
    if "RUN INBOX" in text:
        return text
    suffix = "When inbox pending: Worker chat → RUN INBOX head only."
    return f"{text} · {suffix}" if text else suffix


def build_brain_live_context() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    surfaces = _read_json(SINA / "agent-live-surfaces-v1.json")
    brain_action = _read_json(SINA / "brain-current-action-v1.json")
    brain_val = _read_json(SINA / "brain-goal1-validation-v1.json")
    wire = _read_json(SINA / "governance-brain-wire-v1.json")
    exhausted = _queue_exhausted()

    factory_line = surfaces.get("factory_now_line") or ""
    queue_sa = str(surfaces.get("queue_sa") or "").strip()
    if not queue_sa and not exhausted:
        queue_sa = str((wire.get("queue_head") or {}).get("sa_id") or "").strip()
    if not queue_sa and not exhausted:
        queue_sa = str((brain_val.get("queue_head") or {}).get("sa_id") or "").strip()
    if exhausted:
        queue_sa = ""
    h1 = (surfaces.get("h1_daily") or {}).get("url") or "http://127.0.0.1:13020/"
    h2 = (surfaces.get("h2_machines") or {}).get("url") or "http://127.0.0.1:13020/machines/"

    loop_spec = surfaces.get("loop_specialist_line") or ""
    inv_line = surfaces.get("investigator_line") or ""
    judge_line = surfaces.get("judge_loop_line") or ""
    routing_line = surfaces.get("founder_routing_panel_line") or ""
    disclosure_line = surfaces.get("disclosure_line") or ""
    loop_auto = bool((_read_json(SINA / "loop-specialist-config-v1.json")).get("loop_auto_dispatch_enabled"))
    post_outbound_auto = False
    try:
        from execution_path_vocabulary_v1 import (  # noqa: WPS433
            commercial_smart_loop_line,
            post_outbound_smart_loop_active,
        )

        post_outbound_auto = post_outbound_smart_loop_active()
    except Exception:
        pass

    mandatory = (
        commercial_smart_loop_line()
        if exhausted and post_outbound_auto
        else (
            "Goal 1 complete · queue idle · Worker Hub → Next steps · commercial P0"
            if exhausted
            else (
                "Loop auto-tick · Worker executes one sa/turn when inbox pending"
                if loop_auto
                else (
                    brain_val.get("mandatory_next")
                    or f"Loop specialist tick · ASF resume if FREEZE · queue {queue_sa}"
                    if queue_sa
                    else "Loop specialist observe · ASF resume drain or commercial P0"
                )
            )
        )
    )
    brain_route = brain_val.get("brain_action") or brain_action.get("founder_line") or "route Worker INBOX"

    try:
        from agent_memory_mirror_v1 import INJECT_LAW  # noqa: WPS433

        close = INJECT_LAW.get("founder_close_line") or ""
        if exhausted and post_outbound_auto:
            close = (
                f"{commercial_smart_loop_line()} · "
                "Quote factory_now_line + loop_specialist_line from truth bundle."
            )
        elif exhausted:
            close = (
                "Goal 1 idle · Worker Hub → Next steps · commercial P0 · "
                "When inbox pending: Worker chat → RUN INBOX head only. "
                "Quote factory_now_line + loop_specialist_line from truth bundle."
            )
        elif not exhausted:
            close = "Worker chat → RUN INBOX head only · Loop auto observes · Hub glance only."
    except Exception:
        close = (
            "Worker chat → RUN INBOX head only · Loop auto observes · Hub glance only."
            if not exhausted
            else (
                f"{commercial_smart_loop_line()} · Quote factory_now_line from truth bundle."
                if post_outbound_auto
                else (
                    "Goal 1 idle · Worker Hub → Next steps · commercial P0 · "
                    "When inbox pending: Worker chat → RUN INBOX head only. "
                    "Quote factory_now_line from truth bundle."
                )
            )
        )

    form_line = surfaces.get("form_official_line") or ""
    form_official = surfaces.get("form_official") or {}
    form_canvas_path = str(form_official.get("canvas") or "")
    try:
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433
        from form_official_canvas_route_v1 import form_hub_line, hub_canvas_target  # noqa: WPS433

        form_live = live_form_payload()
        form_open = int(form_live.get("open_questions_count") or 0)
        if not form_line:
            form_line = str(form_live.get("form_official_line") or "")
        route = hub_canvas_target()
        form_hub_line = form_hub_line() or str(route.get("form_hub_line") or "")
        form_canvas_path = str(route.get("path") or form_canvas_path)
    except Exception:
        form_live = {}
        form_open = int((_read_json(SINA / "live-founder-decision-form-v1.json")).get("open_questions_count") or 0)
        form_hub_line = (
            f"Worker Hub {h1} · FORM_OFFICIAL · {form_line}"
            if form_line
            else f"Worker Hub {h1} · FORM_OFFICIAL"
        )

    outbound_line = surfaces.get("outbound_progress_line") or ""
    exec_honesty = surfaces.get("execution_honesty_line") or ""
    behavior_line = surfaces.get("behavior_line") or ""
    try:
        from agent_behavior_settings_v1 import brain_truth_line, load_settings  # noqa: WPS433

        ssot = load_settings()
        brain_anchor = (ssot.get("role_anchors") or {}).get("brain") or {}
        brain_title = str(brain_anchor.get("title") or "Brain — route · handoff Worker")
        brain_job = str(brain_anchor.get("main_job") or "Read disk · route · dispatch Worker RUN INBOX")
        brain_truth = brain_truth_line(ssot=ssot)
        reply_shape = str(
            brain_anchor.get("reply_shape")
            or "Problem · disk truth (PASS/FAIL/RED) — no invitation · STOP"
        )
    except Exception:
        brain_title = "Brain — route · handoff Worker"
        brain_job = "Read disk · route · dispatch Worker RUN INBOX · never implement sa"
        brain_truth = "disk truth only · RED stays RED · no green theater · no sweet lies"
        reply_shape = "Problem · disk truth (PASS/FAIL/RED) — no invitation · STOP"
    cost_intel_line = surfaces.get("cost_intelligence_line") or ""
    wc = _read_json(SINA / "sourcea-worker-connected-receipt-v1.json")
    worker_connected = bool(wc.get("ok"))
    head_upgrade = str((wire.get("queue_head") or {}).get("upgrade_id") or "")
    if not head_upgrade:
        hq = _read_json(SINA / "healthy-queue-30-active.json")
        head_upgrade = str(((hq.get("queue") or [{}])[0]).get("upgrade_id") or "")

    close = _ensure_run_inbox_close(close)

    block = "\n".join(
        [
            "BRAIN LIVE DISK (wins over chat memory — route founder · do not implement sa)",
            f"factory_now: {factory_line}",
            f"queue_sa: {queue_sa}",
            f"behavior: {behavior_line or 'Founder intent first · clarify before substitute'}",
            f"brain_title: {brain_title}",
            f"brain_job: {brain_job}",
            f"brain_truth: {brain_truth}",
            f"reply_shape: {reply_shape}",
            f"cost-intel: {cost_intel_line or '—'}",
            f"outbound: {outbound_line or '—'}",
            f"execution: {exec_honesty or '—'}",
            f"worker_connected: {'PASS' if worker_connected else 'BLOCK'}",
            f"head_upgrade: {head_upgrade or '—'}",
            "execution_surface: inbox_only — Brain routes Worker RUN INBOX head only",
            f"form_official: {form_line or '—'}",
            f"form_hub_line: {form_hub_line or '—'}",
            f"form_canvas: {form_canvas_path or '—'}",
            f"zero_drift: {surfaces.get('zero_drift_line') or '—'}",
            f"better_loop: {surfaces.get('better_loop_line') or '—'}",
            f"output_quality: {surfaces.get('best_loop_oqg_line') or '—'}",
            f"nerve: {surfaces.get('nerve_system_line') or '—'}",
            f"loop_specialist: {loop_spec or '—'}",
            f"investigator: {inv_line or '—'}",
            f"judge_loop: {judge_line or '—'}",
            f"routing_panel: {routing_line or '—'}",
            f"disclosure: {disclosure_line or '—'}",
            f"brain_role: route · handoff Worker · {'idle advisory' if exhausted else 'one sa/turn'} · truth-first",
            f"mandatory_next: {mandatory}",
            f"optional: Worker Hub · Form · {h1}",
            f"h2_machines: {h2}",
            f"founder_close: {close}",
        ]
    )

    return {
        "schema": "brain-live-context-v1",
        "at": _now(),
        "factory_now_line": factory_line,
        "queue_sa": queue_sa,
        "queue_exhausted": exhausted,
        "zero_drift_line": surfaces.get("zero_drift_line") or "",
        "better_loop_line": surfaces.get("better_loop_line") or "",
        "best_loop_oqg_line": surfaces.get("best_loop_oqg_line") or "",
        "nerve_system_line": surfaces.get("nerve_system_line") or "",
        "loop_specialist_line": loop_spec,
        "investigator_line": inv_line,
        "judge_loop_line": judge_line,
        "founder_routing_panel_line": routing_line,
        "disclosure_line": disclosure_line,
        "loop_auto_dispatch_enabled": loop_auto,
        "outbound_progress_line": outbound_line,
        "execution_honesty_line": exec_honesty,
        "behavior_line": behavior_line,
        "brain_title": brain_title,
        "brain_job": brain_job,
        "brain_truth_line": brain_truth,
        "reply_shape": reply_shape,
        "cost_intelligence_line": cost_intel_line,
        "worker_connected": worker_connected,
        "head_upgrade_id": head_upgrade,
        "execution_surface": "inbox_only",
        "sascip_safety_line": surfaces.get("sascip_safety_line") or surfaces.get("sascip_line") or "",
        "form_official_line": form_line,
        "form_hub_line": form_hub_line,
        "form_canvas_path": form_canvas_path,
        "form_open_count": form_open,
        "mandatory_next": (
            f"{form_hub_line} · official form {h1}form/ · then brain route"
            if form_open > 0 and form_hub_line
            else (
                f"Official form — {form_open} decisions · {h1}form/ · pick A/B/C/D"
                if form_open > 0
                else mandatory
            )
        ),
        "brain_action": brain_route,
        "h1_daily": h1,
        "h2_machines": h2,
        "founder_close_line": close,
        "text_block": block,
        "read_first": str(OUT),
        "wire_path": str(SINA / "governance-brain-wire-v1.json"),
        "law": "AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Brain live context block")
    p.add_argument("--json", action="store_true")
    p.add_argument("--text", action="store_true")
    args = p.parse_args()
    row = build_brain_live_context()
    SINA.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.text:
        print(row.get("text_block") or "")
    elif args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("text_block") or "")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
