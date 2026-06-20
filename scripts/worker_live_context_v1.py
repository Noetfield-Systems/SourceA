#!/usr/bin/env python3
"""Worker live context — one disk block prepended to INBOX (chat transcript is not SSOT).

Law: AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md · INCIDENT-034
Output: ~/.sina/worker-live-context-v1.json
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent
SINA = Path.home() / ".sina"
OUT = SINA / "worker-live-context-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def build_worker_live_context() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    surfaces = {}
    sp = SINA / "agent-live-surfaces-v1.json"
    if sp.is_file():
        try:
            surfaces = json.loads(sp.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            surfaces = {}

    factory_line = surfaces.get("factory_now_line") or ""
    h1 = (surfaces.get("h1_daily") or {}).get("url") or "http://127.0.0.1:13020/"
    h2 = (surfaces.get("h2_machines") or {}).get("url") or "http://127.0.0.1:13020/machines/"

    try:
        from execution_path_vocabulary_v1 import (  # noqa: WPS433
            execute_line,
            founder_close_line,
            live_disk_header,
        )

        close = founder_close_line()
        execute_line = execute_line()
        live_header = live_disk_header()
    except Exception:
        close = "Loop auto · Brain work-order dispatch · Hub glance only."
        execute_line = "Loop auto-tick ON · Brain work-order dispatch · Hub glance only"
        live_header = "LIVE DISK (wins over old chat — Brain work-order primary)"

    queue_sa = surfaces.get("queue_sa") or ""
    try:
        from factory_control_v1 import load_factory_now  # noqa: WPS433

        fn = load_factory_now()
        fn_sa = str(fn.get("queue_sa") or "")
        fn_line = str(fn.get("line") or "")
        if fn_sa and (not queue_sa or queue_sa != fn_sa):
            queue_sa = fn_sa
        if fn_line and (not factory_line or fn_sa not in factory_line):
            factory_line = fn_line
    except Exception:
        pass

    loop_spec = surfaces.get("loop_specialist_line") or ""
    inv_line = surfaces.get("investigator_line") or ""
    judge_line = surfaces.get("judge_loop_line") or ""
    routing_line = surfaces.get("founder_routing_panel_line") or ""
    disclosure_line = surfaces.get("disclosure_line") or ""
    mcp_stack_line = surfaces.get("mcp_stack_line") or ""
    tool_pick_line = surfaces.get("tool_pick_line") or ""
    full_stack_fix_line = surfaces.get("full_stack_fix_line") or ""
    loop_auto = bool((_read_json(SINA / "loop-specialist-config-v1.json")).get("loop_auto_dispatch_enabled"))

    outbound_line = surfaces.get("outbound_progress_line") or ""
    exec_honesty = surfaces.get("execution_honesty_line") or ""
    behavior_line = surfaces.get("behavior_line") or ""
    cost_intel_line = surfaces.get("cost_intelligence_line") or ""

    block = "\n".join(
        [
            live_header,
            f"factory_now: {factory_line}",
            f"queue_sa: {queue_sa}",
            f"behavior: {behavior_line or 'Founder intent first · clarify before substitute'}",
            f"cost-intel: {cost_intel_line or '—'}",
            f"outbound: {outbound_line or '—'}",
            f"execution: {exec_honesty or '—'}",
            "execution_surface: inbox_only — RUN INBOX head only · queue_pos>1 = preview not bound",
            f"zero_drift: {surfaces.get('zero_drift_line') or '—'}",
            f"better_loop: {surfaces.get('better_loop_line') or '—'}",
            f"output_quality: {surfaces.get('best_loop_oqg_line') or '—'}",
            f"nerve: {surfaces.get('nerve_system_line') or '—'}",
            f"loop_specialist: {loop_spec or '—'}",
            f"investigator: {inv_line or '—'}",
            f"judge_loop: {judge_line or '—'}",
            f"routing_panel: {routing_line or '—'}",
            f"disclosure: {disclosure_line or '—'}",
            f"mcp_stack: {mcp_stack_line or '—'}",
            f"tool_pick: {tool_pick_line or '—'}",
            f"full_stack_fix: {full_stack_fix_line or '—'}",
            f"execute: {execute_line}",
            f"optional: Worker Hub · Form · {h1}",
            f"h2: {h2}",
            f"close: {close}",
        ]
    )

    return {
        "schema": "worker-live-context-v1",
        "at": _now(),
        "factory_now_line": factory_line,
        "queue_sa": queue_sa,
        "zero_drift_line": surfaces.get("zero_drift_line") or "",
        "better_loop_line": surfaces.get("better_loop_line") or "",
        "best_loop_oqg_line": surfaces.get("best_loop_oqg_line") or "",
        "nerve_system_line": surfaces.get("nerve_system_line") or "",
        "loop_specialist_line": loop_spec,
        "investigator_line": inv_line,
        "judge_loop_line": judge_line,
        "founder_routing_panel_line": routing_line,
        "disclosure_line": disclosure_line,
        "mcp_stack_line": mcp_stack_line,
        "tool_pick_line": tool_pick_line,
        "full_stack_fix_line": full_stack_fix_line,
        "loop_auto_dispatch_enabled": loop_auto,
        "execution_surface": "inbox_only",
        "execution_bind_law": "Never execute queue_pos != 1 unless broker advanced",
        "outbound_progress_line": outbound_line,
        "execution_honesty_line": exec_honesty,
        "behavior_line": behavior_line,
        "cost_intelligence_line": cost_intel_line,
        "sascip_safety_line": surfaces.get("sascip_safety_line") or surfaces.get("sascip_line") or "",
        "h1_daily": h1,
        "h2_machines": h2,
        "founder_close_line": close,
        "text_block": block,
        "law": "AGENT_DISK_LIVE_WIRE_FIRST_LOCKED_v1.md",
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Worker live context block")
    p.add_argument("--json", action="store_true")
    p.add_argument("--text", action="store_true")
    args = p.parse_args()
    row = build_worker_live_context()
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
