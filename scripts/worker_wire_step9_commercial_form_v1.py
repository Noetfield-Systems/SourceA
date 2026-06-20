#!/usr/bin/env python3
"""Step 9 machine wire — commercial L3 pulse + FORM UNIFY founder picks status."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OUT = SINA / "worker-wire-step9-commercial-form-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def assess_step9() -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from execution_plane_honesty_v1 import assess_commercial_readiness  # noqa: WPS433

    commercial = assess_commercial_readiness()
    form = _read(SINA / "live-founder-decision-form-intake-v1.json")
    open_picks = int(form.get("open_questions_count") or form.get("open_count") or 0)
    w3_show: dict = {}
    try:
        proc = subprocess.run(
            [sys.executable, str(SCRIPTS / "w3_founder_review_v1.py"), "--show"],
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=30,
        )
        w3_show = {"exit": proc.returncode, "stdout": (proc.stdout or "")[:500]}
    except Exception as exc:
        w3_show = {"error": str(exc)}

    founder_picks = {
        "Q-FINAL-05": "UNIFY option A — founder must confirm in M1 Canvas",
        "Q-FINAL-01": "founder PICK pending",
        "Q-FINAL-02": "founder PICK pending",
    }
    comm_ok = int(commercial.get("ready_pct") or 0) >= 100
    row = {
        "schema": "worker-wire-step9-commercial-form-v1",
        "at": _now(),
        "ok": comm_ok and open_picks == 0,
        "machine_wired": True,
        "commercial": commercial,
        "commercial_l3_blocked": not comm_ok,
        "founder_unblock": [
            "w3_sina_read",
            "w3_mail_from",
            "w3_send_ready",
        ],
        "form": {
            "open_picks": open_picks,
            "founder_picks_required": founder_picks,
            "hub_action": "FORM_OFFICIAL (M1 Canvas) · Pending confirmations",
        },
        "w3_founder_review": w3_show,
        "line": (
            f"step9 · commercial={commercial.get('ready_pct')}% · form_picks={open_picks}"
            + (" · founder ACTION required" if not comm_ok or open_picks else " · READY")
        ),
    }
    return row


def main() -> int:
    ap = argparse.ArgumentParser(description="Worker wire step 9 — commercial + FORM status")
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    row = assess_step9()
    if args.write:
        SINA.mkdir(parents=True, exist_ok=True)
        OUT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(row.get("line"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
