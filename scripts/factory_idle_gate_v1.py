#!/usr/bin/env python3
"""Factory idle probe — gate expensive E2E before mid-slice DENIED states."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
INBOX = ROOT / ".sina-loop" / "INBOX.md"
QUEUE_STATE = Path.home() / ".sina" / "healthy-queue-state-v1.json"
FACTORY_NOW = Path.home() / ".sina" / "factory-now-v1.json"


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def _inbox_pending() -> tuple[bool, str]:
    if not INBOX.is_file():
        return False, ""
    text = INBOX.read_text(encoding="utf-8", errors="replace")
    m = re.search(r"pending=(\d+)", text)
    if m and int(m.group(1)) == 1:
        role_m = re.search(r"role=([A-Z]+)", text)
        sa_m = re.search(r"sa[_-]?id=([a-z]+-\d+)", text, re.I)
        return True, f"INBOX pending=1 role={role_m.group(1) if role_m else '?'} sa={sa_m.group(1) if sa_m else '?'}"
    return False, ""


def _worker_turn_open() -> tuple[bool, str]:
    sys.path.insert(0, str(SCRIPTS))
    try:
        from worker_turn_lib import turn_open_block, turn_state  # noqa: WPS433

        if turn_open_block():
            st = turn_state() or {}
            return True, f"WORKER_TURN_OPEN sa={st.get('sa_id') or '?'}"
    except Exception as exc:
        return False, f"turn_probe_warn:{exc}"
    return False, ""


def _queue_head_act() -> tuple[bool, str]:
    fn = _load_json(FACTORY_NOW)
    role = str(fn.get("queue_role") or fn.get("expected_role") or "").upper()
    sa = str(fn.get("queue_sa") or "")
    if role == "ACT":
        return True, f"queue_head_ACT sa={sa}"
    st = _load_json(QUEUE_STATE)
    pos = int(st.get("next_pos") or 0)
    if pos:
        try:
            sys.path.insert(0, str(SCRIPTS))
            from healthy_queue_ssot_lib import load_healthy_queue, queue_items  # noqa: WPS433

            _, data = load_healthy_queue()
            items = queue_items(data)
            for row in items:
                if int(row.get("queue_pos") or 0) == pos:
                    if str(row.get("queue_role") or "").lower() == "act":
                        return True, f"queue_cursor_ACT pos={pos} sa={row.get('sa_id')}"
                    break
        except Exception:
            pass
    return False, ""


def _dual_proof_false() -> tuple[bool, str]:
    fn = _load_json(FACTORY_NOW)
    if fn.get("dual_proof") is False or fn.get("dual_proof_ok") is False:
        return True, f"dual_proof False vy={fn.get('valid_yes')} brain={fn.get('brain_vy')}"
    return False, ""


def _gatekeeper_blocked() -> tuple[bool, str]:
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "gatekeeper_v1.py"), "--no-broker", "--json"],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    try:
        row = json.loads((proc.stdout or "").strip() or "{}")
    except json.JSONDecodeError:
        return False, ""
    if not row.get("safe_to_execute"):
        reasons = row.get("reasons") or []
        return True, f"gatekeeper {row.get('status')}: {reasons[0] if reasons else 'blocked'}"
    return False, ""


def probe_factory_idle(*, check_gatekeeper: bool = True) -> dict:
    blockers: list[str] = []
    for fn in (_inbox_pending, _worker_turn_open, _queue_head_act, _dual_proof_false):
        hit, msg = fn()
        if hit and msg:
            blockers.append(msg)
    if check_gatekeeper:
        hit, msg = _gatekeeper_blocked()
        if hit and msg:
            blockers.append(msg)
    return {
        "ok": not blockers,
        "idle": not blockers,
        "blockers": blockers,
        "hint": (
            "SourceA Worker → run inbox once; then ONE brain_sync if dual_proof; "
            "do not run fast ladder until idle."
            if blockers
            else "idle — fast ladder allowed"
        ),
    }


def main() -> int:
    p = argparse.ArgumentParser(description="Factory idle gate for E2E ladders")
    p.add_argument("--json", action="store_true")
    p.add_argument("--no-gatekeeper", action="store_true")
    args = p.parse_args()
    row = probe_factory_idle(check_gatekeeper=not args.no_gatekeeper)
    if args.json:
        print(json.dumps(row, indent=2))
    elif row.get("idle"):
        print("OK: factory idle")
    else:
        print("BLOCKED:", "; ".join(row.get("blockers") or []))
        print(row.get("hint"))
    return 0 if row.get("idle") else 2


if __name__ == "__main__":
    raise SystemExit(main())
