#!/usr/bin/env python3
"""Sleep Mac caretaker — event-driven only (post_dispatch / stuck_recovery)."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
ACTIVE = ROOT / "ACTIVE_NOW.md"
LOG = Path.home() / ".sina" / "sleep-mac-caretaker-v1.jsonl"
REPORT = Path.home() / ".sina" / "worker_round_report_v1.json"
ORCH = Path.home() / ".sina" / "healthy-drain-orchestrator-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _log(row: dict) -> None:
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with LOG.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps({**row, "at": _now()}) + "\n")


def _run(cmd: list[str], *, timeout: int = 90) -> dict:
    proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=timeout)
    out = (proc.stdout or "").strip()
    try:
        body = json.loads(out) if out and out[0] in "{[" else {"raw": out}
    except json.JSONDecodeError:
        body = {"raw": out, "stderr": proc.stderr}
    return {"ok": proc.returncode == 0, "code": proc.returncode, "body": body}


def _load_json(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}


def _sleep_mode() -> tuple[bool, str]:
    sys.path.insert(0, str(SCRIPTS))
    from active_now_v1 import load_active_now  # noqa: WPS433

    a = load_active_now()
    if not a.get("ok"):
        return False, "ACTIVE_NOW_MISSING"
    if "absent" not in (a.get("founder_mode") or ""):
        return False, "NOT_FOUNDER_ABSENT"
    if not a.get("sleep_escalation"):
        return False, "SLEEP_ESCALATION_OFF"
    return True, "ok"


def _sync_active_now(*, sa_id: str, role: str, pos: int, total: int) -> bool:
    if not ACTIVE.is_file():
        return False
    text = ACTIVE.read_text(encoding="utf-8")
    new = re.sub(
        r"\*\*Current sa_id:\*\*.*",
        f"**Current sa_id:** `{sa_id}` · `{role}` · pos `{pos}/{total}`",
        text,
    )
    if new != text:
        ACTIVE.write_text(new, encoding="utf-8")
        return True
    return False


def _clear_poison_report(*, expected_sa: str = "") -> bool:
    if not REPORT.is_file():
        return False
    try:
        row = json.loads(REPORT.read_text())
    except json.JSONDecodeError:
        REPORT.unlink(missing_ok=True)
        return True
    focus = (row.get("sa_focus") or "").lower()
    if focus.startswith("sa-test") or focus == "unknown":
        REPORT.unlink(missing_ok=True)
        return True
    if expected_sa and focus and focus != expected_sa.lower():
        REPORT.unlink(missing_ok=True)
        return True
    return False


def _run_sidecars() -> None:
    subprocess.run(
        [sys.executable, str(SCRIPTS / "sidecar_scout_api_v1.py")],
        cwd=str(ROOT),
        capture_output=True,
        timeout=120,
    )
    subprocess.run(
        [sys.executable, str(SCRIPTS / "sidecar_prep_cli_v1.py")],
        cwd=str(ROOT),
        capture_output=True,
        timeout=60,
    )


def tick(*, caller: str = "caretaker", trigger: str = "post_dispatch") -> dict:
    ok, reason = _sleep_mode()
    if not ok:
        return {"ok": False, "skipped": True, "reason": reason, "caller": caller, "trigger": trigger}

    orch_before = _load_json(ORCH)
    expected_sa = orch_before.get("expected_sa") or ""
    actions: list[str] = []

    if _clear_poison_report(expected_sa=expected_sa):
        actions.append("cleared_poison_report")

    if trigger == "post_dispatch":
        # Light read — only act on drift
        state = _run([sys.executable, str(SCRIPTS / "brain_read_state_v1.py"), "--caller", caller])
        body = state.get("body") if isinstance(state.get("body"), dict) else {}
        if not body.get("aligned"):
            hb = body.get("heartbeat") or {}
            inbox = body.get("inbox") or {}
            if hb.get("sa_id") and _sync_active_now(
                sa_id=hb["sa_id"],
                role=inbox.get("role") or "check",
                pos=int(hb.get("queue_pos") or 1),
                total=int(hb.get("queue_total") or 30),
            ):
                actions.append("synced_active_now")

        if orch_before.get("status") == "awaiting_worker":
            poll = _run([sys.executable, str(SCRIPTS / "healthy-drain-orchestrator-v1.py"), "poll"])
            pb = poll.get("body") if isinstance(poll.get("body"), dict) else {}
            if pb.get("completed"):
                actions.append("orchestrator_advanced")
                _run_sidecars()
                actions.append("sidecars_on_advance")
            elif poll.get("ok"):
                actions.append("orchestrator_poll_ok")
        elif orch_before.get("status") == "idle":
            # Guard: do NOT deliver immediately after an overnight skip —
            # let the dispatcher's 30s tick handle the next position.
            # Otherwise caretaker double-skips ACT before the tick fires.
            just_skipped = bool(orch_before.get("last_overnight_skip"))
            if just_skipped:
                actions.append("caretaker_skip_guard_hold")
            else:
                d = _run([sys.executable, str(SCRIPTS / "healthy-drain-orchestrator-v1.py"), "deliver", "--force"])
                if d.get("ok"):
                    actions.append("delivered_inbox")

    elif trigger == "stuck_recovery":
        d = _run([sys.executable, str(SCRIPTS / "healthy-drain-orchestrator-v1.py"), "deliver", "--force"])
        if d.get("ok"):
            actions.append("recovery_deliver")
        subprocess.run(["bash", str(SCRIPTS / "start-overnight-3engine-v1.sh")], cwd=str(ROOT), timeout=30)
        actions.append("recovery_overnight_restart")

    row = {
        "ok": True,
        "caller": caller,
        "trigger": trigger,
        "actions": actions,
        "expected_sa": expected_sa,
        "orchestrator_status": orch_before.get("status"),
    }
    _log(row)
    return row


def main() -> int:
    p = argparse.ArgumentParser(description="Sleep Mac caretaker — event-driven")
    p.add_argument("--trigger", default="post_dispatch", choices=("post_dispatch", "stuck_recovery"))
    p.add_argument("--caller", default="caretaker")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = tick(caller=args.caller, trigger=args.trigger)
    print(json.dumps(row, indent=2) if args.json else json.dumps(row))
    return 0 if row.get("ok") or row.get("skipped") else 1


if __name__ == "__main__":
    raise SystemExit(main())
