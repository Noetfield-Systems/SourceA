"""Mechanical one-sa-per-turn — file gate (law: GOAL_EXECUTION_ACTIVE §2)."""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

TURN_STATE = Path.home() / ".sina" / "worker_turn_state_v1.json"
ROUND_REPORT = Path.home() / ".sina" / "worker_round_report_v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _read(path: Path) -> dict:
    if not path.is_file():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


def turn_state() -> dict:
    return _read(TURN_STATE)


def turn_open_block() -> dict | None:
    """Block new session if prior turn not closed with round report."""
    st = turn_state()
    if st.get("status") != "open":
        return None
    return {
        "ok": False,
        "error": (
            f"WORKER_TURN_OPEN sa={st.get('sa_id')} — close prior turn first "
            f"(closeout_sa_task.py + WORKER_ROUND_REPORT)"
        ),
        "turn_blocked": True,
        "open_sa": st.get("sa_id"),
        "opened_at": st.get("opened_at"),
        "hint": "Write ~/.sina/worker_round_report_v1.json via scripts/worker_turn_lib.py --report",
    }


def open_turn(*, sa_id: str, path: str = "") -> dict:
    block = turn_open_block()
    if block:
        if str(block.get("open_sa") or "") == sa_id:
            return {"ok": True, "opened": sa_id, "already_open": True}
        return block
    payload = {
        "status": "open",
        "sa_id": sa_id,
        "path": path,
        "opened_at": _now(),
        "law": "GOAL_EXECUTION_ACTIVE_LOCKED_v1.md",
    }
    TURN_STATE.parent.mkdir(parents=True, exist_ok=True)
    TURN_STATE.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "opened": sa_id}


def write_round_report(*, sa_id: str, round_type: str = "implement", critical: int = 0) -> dict:
    payload = {
        "status": "WORKER_ROUND_REPORT",
        "sa_focus": sa_id,
        "round_type": round_type,
        "critical_bugs": critical,
        "at": _now(),
        "turn_closed": True,
    }
    ROUND_REPORT.parent.mkdir(parents=True, exist_ok=True)
    ROUND_REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    try:
        broker_note = Path.home() / ".sina" / "brain-broker-inbox-v1.json"
        broker_note.parent.mkdir(parents=True, exist_ok=True)
        broker_note.write_text(
            json.dumps(
                {
                    "schema": "brain-broker-inbox-v1",
                    "at": payload["at"],
                    "status": "report_on_disk",
                    "worker_report": payload,
                    "founder_action": "Brain: goal1_lane_broker.py brain-poll",
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass
    return payload


def close_turn(
    *,
    sa_id: str,
    round_type: str = "implement",
    critical: int = 0,
    force: bool = False,
) -> dict:
    st = turn_state()
    if (
        st.get("status") == "open"
        and st.get("sa_id")
        and st.get("sa_id") != sa_id
        and not force
    ):
        return {
            "ok": False,
            "error": f"turn open for {st.get('sa_id')} not {sa_id}",
        }
    write_round_report(sa_id=sa_id, round_type=round_type, critical=critical)
    closed = {
        "status": "closed",
        "sa_id": sa_id,
        "closed_at": _now(),
        "last_report": str(ROUND_REPORT),
    }
    TURN_STATE.write_text(json.dumps(closed, indent=2) + "\n", encoding="utf-8")
    return {"ok": True, "closed": sa_id}


def live_pick_id() -> str | None:
    import subprocess
    import sys

    root = Path(__file__).resolve().parents[1]
    proc = subprocess.run(
        ["bash", str(root / "scripts" / "plan-no-asf-run.sh"), "pick", "1"],
        capture_output=True,
        text=True,
        cwd=str(root),
    )
    for line in proc.stdout.splitlines():
        if line.startswith("sa-"):
            return line.split("\t", 1)[0].strip()
    return None


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Worker one-sa turn gate")
    p.add_argument("--open", action="store_true", help="Open turn for live pick 1")
    p.add_argument("--close", metavar="SA_ID")
    p.add_argument("--force", action="store_true", help="Close turn even if sa_id mismatches open turn")
    p.add_argument("--check", action="store_true", help="Show turn state (alias: --status)")
    p.add_argument("--status", action="store_true", help=argparse.SUPPRESS)
    p.add_argument("--report", metavar="SA_ID")
    args = p.parse_args()

    if args.check or args.status:
        block = turn_open_block()
        if block:
            print(json.dumps(block, indent=2))
            return 1
        print(json.dumps({"ok": True, "turn": turn_state()}, indent=2))
        return 0
    if args.open:
        sa = live_pick_id()
        if not sa:
            print("FAIL: no live pick")
            return 1
        out = open_turn(sa_id=sa)
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 1
    if args.close:
        out = close_turn(sa_id=args.close, force=args.force)
        print(json.dumps(out, indent=2))
        return 0 if out.get("ok") else 1
    if args.report:
        write_round_report(sa_id=args.report)
        print(f"OK: round report {args.report}")
        return 0
    p.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
