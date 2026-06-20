#!/usr/bin/env python3
"""Patch command-data.json after hub refresh — all UI blocks wired (light + heavy).

TRACE: AUTO-TRACE-RUNTIME-UI-ALIGN-v1.0 · agent Auto
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from sina_command_lib import (  # noqa: E402
    PANEL_DIR,
    build_payload,
    goal1_auto_run_payload,
    goal1_hub_status_bundle,
    sync_sa_queue_into_payload,
    write_panel_outputs,
)


def _open_picks_block_p0_append() -> bool:
    try:
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        form = live_form_payload()
        return int(form.get("open_questions_count") or 0) > 0
    except Exception:
        return False


def _align_p0_pick(payload: dict) -> None:
    from founder_p0_next_action_v1 import rt_live_gate_active  # noqa: WPS433

    if rt_live_gate_active() or _open_picks_block_p0_append():
        return
    sq = payload.get("sourcea_sa_queue") or {}
    pick_id = str((sq.get("live_pick") or {}).get("id") or "")
    if not pick_id.startswith("sa-"):
        return
    cc = payload.get("command_center") or {}
    founder = cc.get("founder") or {}
    p0 = founder.get("p0") or {}
    na = str(p0.get("next_action") or "")
    if pick_id not in na:
        p0["next_action"] = f"{na} · pick {pick_id}" if na else f"Live pick: {pick_id}"
    founder["p0"] = p0
    cc["founder"] = founder
    payload["command_center"] = cc


def _refresh_live_blocks(payload: dict) -> None:
    """Re-pull panels that drift on hub-sync-only refresh."""
    try:
        from system_roadmap import system_roadmap_payload  # noqa: WPS433

        payload["system_roadmap"] = system_roadmap_payload()
    except Exception:
        pass
    try:
        from agent_scoreboard import scoreboard_payload  # noqa: WPS433

        payload["agent_scoreboard"] = scoreboard_payload()
    except Exception:
        pass
    try:
        from agent_essay_discourse import essay_discourse_payload  # noqa: WPS433

        payload["essay_discourse"] = essay_discourse_payload()
    except Exception:
        pass
    try:
        from strategic_synthesis_hub import strategic_synthesis_payload  # noqa: WPS433

        payload["strategic_synthesis"] = strategic_synthesis_payload()
    except Exception:
        pass
    payload.update(goal1_hub_status_bundle(goal1_auto_run_payload()))
    try:
        from founder_p0_next_action_v1 import build_founder_p0_next_action  # noqa: WPS433
        from sina_command_lib import _must_do_today_lines  # noqa: WPS433

        cc = payload.get("command_center") or {}
        founder = cc.get("founder") or {}
        bowl = payload.get("daily_bowl") or payload.get("bowl") or {}
        founder["must_do_today"] = _must_do_today_lines(bowl)
        p0 = founder.get("p0") or {}
        p0["next_action"] = build_founder_p0_next_action()
        founder["p0"] = p0
        cc["founder"] = founder
        payload["command_center"] = cc
    except Exception:
        pass


def align_command_data_ui(*, refresh_scripts: bool = False) -> dict:
    try:
        from governance_projection_g3_v1 import authorize_projection_write  # noqa: WPS433

        authorize_projection_write(
            ["hub", "monitor", "truth_bundle"],
            reason="align_command_data_ui_v1",
        )
    except Exception:
        pass
    payload = build_payload(run_refresh_scripts=refresh_scripts)
    _refresh_live_blocks(payload)
    sync_sa_queue_into_payload(payload)
    _align_p0_pick(payload)
    write_panel_outputs(payload, json_only=True)
    sr = payload.get("system_roadmap") or {}
    evb = sr.get("eval_packet_v1b") or {}
    sb = payload.get("agent_scoreboard") or {}
    p0 = ((payload.get("command_center") or {}).get("founder") or {}).get("p0") or {}
    live = ((payload.get("sourcea_sa_queue") or {}).get("live_pick") or {}).get("id")
    return {
        "ok": True,
        "live_pick": live,
        "eval_1b_pct": evb.get("packet_win_pct"),
        "fleet_auto_green": sb.get("fleet_auto_green_count"),
        "next_action": p0.get("next_action", ""),
        "has_strategic_synthesis": bool(payload.get("strategic_synthesis")),
    }


def main() -> int:
    row = align_command_data_ui()
    out = PANEL_DIR / "command-data.json"
    if not out.is_file():
        print("FAIL: command-data.json missing after UI align")
        return 1
    data = json.loads(out.read_text(encoding="utf-8"))
    errors: list[str] = []
    from founder_p0_next_action_v1 import rt_live_gate_active, validate_next_action  # noqa: WPS433

    live = ((data.get("sourcea_sa_queue") or {}).get("live_pick") or {}).get("id")
    na = (
        ((data.get("command_center") or {}).get("founder") or {}).get("p0") or {}
    ).get("next_action") or ""
    if rt_live_gate_active():
        ok, msg = validate_next_action(na)
        if not ok:
            errors.append(f"RT LIVE next_action invalid: {msg}")
    elif _open_picks_block_p0_append():
        ok, msg = validate_next_action(na)
        if not ok:
            errors.append(f"open-questions next_action invalid: {msg}")
    elif not live or live not in na:
        errors.append(f"P0 pick drift live={live!r}")
    if not (data.get("goal1_loop") or {}).get("ok"):
        errors.append("goal1_loop missing or not ok")
    if not data.get("system_roadmap"):
        errors.append("system_roadmap missing")
    if not data.get("agent_scoreboard"):
        errors.append("agent_scoreboard missing")
    import os

    if not os.environ.get("SINA_ALIGN_SKIP_VALIDATORS"):
        proc = subprocess.run(
            ["bash", str(ROOT / "scripts/validate-no-agent-invitation-v1.sh")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if proc.returncode != 0:
            errors.append("validate-no-agent-invitation-v1 FAIL")
        proc_ui = subprocess.run(
            ["bash", str(ROOT / "scripts/validate-ui-zero-drift-v1.sh")],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
        )
        if proc_ui.returncode != 0:
            errors.append("validate-ui-zero-drift-v1 FAIL")
    if errors:
        print("FAIL: align_command_data_ui_v1 — " + "; ".join(errors))
        return 1
    print(
        f"OK: align_command_data_ui_v1 live={live} "
        f"eval_1b={row.get('eval_1b_pct')}% fleet_green={row.get('fleet_auto_green')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
