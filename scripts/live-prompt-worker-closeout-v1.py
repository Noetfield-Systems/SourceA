#!/usr/bin/env python3
"""Worker Live Prompt Finish v3 closeout receipt — reads disk receipts, no validator re-run."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from governance_paths_v1 import SINA_STATIC_PROMPT_INCIDENT_024

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUT = SINA / "live-prompt-worker-closeout-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def closeout(*, write: bool = True) -> dict:
    audit = _read_json(SINA / "live-prompt-lane-receipt-v1.json")
    score = _read_json(SINA / "live-prompt-lane-score-v1.json")
    cross = _read_json(SINA / "cross-plan-readiness-v1.json")

    phases = {
        "w1_audit": bool(audit.get("ok")),
        "w2_e2e": any(c.get("id") == "e2e" and c.get("ok") for c in (audit.get("checks") or [])),
        "w3_edit_ui": "data-live-edit" in (ROOT / "agent-control-panel/assets/app.js").read_text(encoding="utf-8"),
        "w4_incident_024": SINA_STATIC_PROMPT_INCIDENT_024.is_file(),
        "w5_lane_score": bool(score.get("ok")) and float(score.get("score_pct") or 0) >= 90.0,
        "w6_monitor": "live-next-10-panel" in (ROOT / "monitor.html").read_text(encoding="utf-8"),
        "w7_s10": "live_ongoing_prompts" in (SCRIPTS / "s10_eternal_audit_loop_v1.py").read_text(encoding="utf-8"),
        "w8_freeze": "FREEZE_ACT_BLOCKED" in (SCRIPTS / "healthy-drain-orchestrator-v1.py").read_text(encoding="utf-8"),
        "w9_cross_plan": bool(cross.get("schema")),
    }

    worker_phases_ok = all(phases.values())
    row = {
        "schema": "live-prompt-worker-closeout-v1",
        "at": _now(),
        "plan": "worker_live_prompt_finish_v3",
        "phases": phases,
        "worker_phases_ok": worker_phases_ok,
        "cross_plan": cross,
        "global_done": worker_phases_ok and bool(cross.get("worker_global_done")),
        "receipts": {
            "audit_at": audit.get("at"),
            "score_at": score.get("at"),
            "score_pct": score.get("score_pct"),
            "cross_plan_at": cross.get("at"),
        },
        "tracking": {
            "quarantine_at_deliver": phases.get("w8_freeze") and phases.get("w2_e2e"),
            "edit_in_prompt_feed": phases.get("w3_edit_ui"),
            "incident_024_close": phases.get("w4_incident_024"),
            "monitor_next_10": phases.get("w6_monitor"),
            "lane_score": phases.get("w5_lane_score"),
            "anti_staleness_global": cross.get("anti_staleness_v2"),
            "finish_plan_global": cross.get("finish_plan_10phase"),
        },
        "note": "Receipt-based closeout — validators not re-run (avoids brain_sync multiplication)",
    }
    if write:
        SINA.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser()
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = closeout()
    if args.json:
        print(json.dumps(row, indent=2))
    return 0 if row.get("worker_phases_ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
