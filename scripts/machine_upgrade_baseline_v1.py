#!/usr/bin/env python3
"""Baseline snapshot for machine upgrades — before/after photo on disk.

Law: REFINEMENT_UNIFIED_AGENT_MACHINE_LOCKED_v1.md
Output: ~/.sina/machine-upgrade-baseline-v1.json
        ~/.sina/machine-upgrade-baseline-<tag>-v1.json when --tag set
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
SCHEMA = "machine-upgrade-baseline-v1"


def _now() -> str:
    from datetime import datetime, timezone

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _form_open() -> dict:
    try:
        out = subprocess.check_output(
            [sys.executable, str(SCRIPTS / "live_founder_decision_form_v1.py"), "--json"],
            cwd=str(ROOT),
            text=True,
            timeout=30,
        )
        i = out.find("{")
        return json.loads(out[i:]) if i >= 0 else {}
    except (subprocess.CalledProcessError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return {}


def capture_baseline(*, tag: str = "current", upgrade_id: str = "") -> dict:
    agentic = _read_json(SINA / "agentic-layer-pipeline-v2.json")
    crit = _read_json(SINA / "find-bugs" / "last-run.json")
    h2 = _read_json(SINA / "h2-pending-registry-v1.json")
    ladder = _read_json(SINA / "machine-test-ladder-receipt-v1.json")
    tune = _read_json(SINA / "machine-tune-receipt-v1.json")
    form = _form_open()
    broker = _read_json(SINA / "goal1-lane-broker-state-v1.json")

    row = {
        "schema": SCHEMA,
        "at": _now(),
        "tag": tag,
        "upgrade_id": upgrade_id or None,
        "queue": {
            "factory_mode": broker.get("factory_mode") or broker.get("mode"),
            "head_sa": broker.get("head_sa_id") or broker.get("current_sa"),
        },
        "agentic_health": (agentic.get("health") or {}).get("status"),
        "critical_count": int(crit.get("critical_count") or 0),
        "h2_pending_total": h2.get("pending_total") or len(h2.get("next_phase") or []),
        "form_open_count": form.get("open_questions_count") or form.get("open_count") or 0,
        "ladder_ok": ladder.get("ok"),
        "ladder_tier": ladder.get("tier"),
        "tune_ok": tune.get("ok"),
        "paths": {
            "agentic": str(SINA / "agentic-layer-pipeline-v2.json"),
            "find_bugs": str(SINA / "find-bugs" / "last-run.json"),
            "h2": str(SINA / "h2-pending-registry-v1.json"),
            "ladder": str(SINA / "machine-test-ladder-receipt-v1.json"),
        },
    }
    SINA.mkdir(parents=True, exist_ok=True)
    main = SINA / "machine-upgrade-baseline-v1.json"
    main.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if tag and tag != "current":
        tagged = SINA / f"machine-upgrade-baseline-{tag}-v1.json"
        tagged.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Machine upgrade baseline snapshot")
    ap.add_argument("--tag", default="current", help="before | after | current")
    ap.add_argument("--upgrade-id", default="")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = capture_baseline(tag=args.tag, upgrade_id=args.upgrade_id)
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"BASELINE tag={args.tag} critical={row['critical_count']} agentic={row['agentic_health']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
