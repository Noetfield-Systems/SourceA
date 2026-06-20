#!/usr/bin/env python3
"""Validate command-data.json SA queue + P0 pick align with queue_sa (dual-pick law)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CMD = ROOT / "agent-control-panel" / "command-data.json"

sys.path.insert(0, str(ROOT / "scripts"))
from queue_sa_pick_lib_v1 import queue_sa_from_disk  # noqa: E402
from sourcea_pick_lib import pick_backlog_plans  # noqa: E402


def main() -> int:
    if not CMD.is_file():
        print("FAIL: command-data.json missing — run build-sina-command-panel.py")
        return 1

    reg = json.loads(
        (ROOT / "brain-os/plan-registry/sourcea-1000/REGISTRY.json").read_text(encoding="utf-8")
    )
    plans = reg["plans"]
    backlog_count = sum(1 for pl in plans if pl.get("status") == "backlog")
    phase_first = pick_backlog_plans(plans, tiers=["T0", "T1", "T2", "T3"], limit=1, order="phase-first")
    queue_sa = queue_sa_from_disk()
    if not phase_first:
        if backlog_count == 0 and queue_sa:
            head_id = queue_sa
        else:
            print("FAIL: no phase-first pick from REGISTRY")
            return 1
    else:
        head_id = queue_sa or phase_first[0]["id"]

    data = json.loads(CMD.read_text(encoding="utf-8"))
    sq = data.get("sourcea_sa_queue") or {}
    live = (sq.get("live_pick") or {}).get("id")
    if live != head_id:
        print(f"FAIL: sourcea_sa_queue.live_pick={live!r} != expected {head_id!r}")
        return 1

    fs = (
        ((data.get("command_center") or {}).get("founder") or {}).get("factory_state") or {}
    )
    fs_q = str(fs.get("queue_sa") or "")
    if queue_sa and fs_q and fs_q != queue_sa:
        print(f"FAIL: founder.factory_state.queue_sa={fs_q!r} != disk queue {queue_sa!r}")
        return 1

    p0_action = (
        ((data.get("command_center") or {}).get("founder") or {}).get("p0") or {}
    ).get("next_action") or ""
    try:
        from founder_p0_next_action_v1 import rt_live_gate_active  # noqa: WPS433

        rt_gate = rt_live_gate_active()
    except Exception:
        rt_gate = False
    open_picks = False
    try:
        from live_founder_decision_form_v1 import payload as live_form_payload  # noqa: WPS433

        open_picks = int(live_form_payload().get("open_questions_count") or 0) > 0
    except Exception:
        open_picks = False
    if open_picks:
        if "QUESTIONS" not in p0_action.upper() and "FORM" not in p0_action.upper():
            print(f"FAIL: form-office P0 expected when open picks: {p0_action[:80]!r}")
            return 1
        if head_id in p0_action:
            print(f"FAIL: form-office P0 must not cite live_pick {head_id} (INCIDENT-027)")
            return 1
    elif head_id not in p0_action and queue_sa and not rt_gate:
        print(f"FAIL: founder p0 next_action missing {head_id}: {p0_action[:80]!r}")
        return 1
    if rt_gate and "RT LIVE" not in p0_action:
        print(f"FAIL: RT LIVE gate active but p0 missing RT LIVE copy: {p0_action[:80]!r}")
        return 1

    print(f"OK: command-data SA queue aligned pick={head_id}")
    print("VALIDATE-COMMAND-DATA-SA-QUEUE ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
