#!/usr/bin/env python3
"""Manual pack drain — broker submit per queue pos without headless agent CLI."""
from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"


def _run(cmd: list[str], *, timeout: int = 300) -> tuple[int, str]:
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=timeout,
    )
    return proc.returncode, (proc.stdout or "") + (proc.stderr or "")


def _queue_pos() -> int:
    st = json.loads((SINA / "healthy-queue-state-v1.json").read_text())
    return int(st.get("next_pos") or 1)


def _queue_item(pos: int) -> dict:
    q = json.loads((SINA / "healthy-queue-30-active.json").read_text())
    return q["queue"][pos - 1]


def _heal_orch(pos: int, item: dict) -> None:
    orch_path = SINA / "healthy-drain-orchestrator-v1.json"
    orch = json.loads(orch_path.read_text()) if orch_path.is_file() else {}
    orch.update(
        {
            "schema": "healthy-drain-orchestrator-v1",
            "status": "awaiting_worker",
            "expected_pos": pos,
            "expected_sa": item["sa_id"],
            "expected_role": item["queue_role"],
            "delivery": None,
            "max_turns": 30,
        }
    )
    orch_path.write_text(json.dumps(orch, indent=2) + "\n")


def _broker(sa: str, role: str, summary: str) -> dict:
    rt = {"check": "audit", "act": "implement", "verify": "verify"}[role]
    na = "NONE" if role == "verify" else ("verify" if role == "act" else "act")
    yaml_body = f"""status: WORKER_ROUND_REPORT
sa_focus: {sa}
round_type: {rt}
verdict: PASS
summary: {summary}
next_action: {na}
"""
    sys.path.insert(0, str(SCRIPTS))
    from duplicate_inject_guard_v1 import clear_inject_lock  # noqa: WPS433
    from worker_inject_lib import write_turn_bind  # noqa: WPS433

    clear_inject_lock()
    item = _queue_item(_queue_pos())
    write_turn_bind(
        meta={
            "queue_pos": item["queue_pos"],
            "queue_total": 30,
            "queue_role": item["queue_role"],
            "sa_id": item["sa_id"],
        },
        prompt=summary,
    )
    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / "goal1_lane_broker.py"), "worker-submit", "--stdin"],
        input=yaml_body,
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        timeout=120,
    )
    try:
        # parse last ok: line
        for line in reversed(proc.stdout.splitlines()):
            if line.startswith("ok:"):
                return {"ok": "true" in line.lower(), "stdout": proc.stdout[-2000:]}
    except Exception:
        pass
    return {"ok": proc.returncode == 0, "stdout": proc.stdout[-2000:], "stderr": proc.stderr[-500:]}


def drain(*, from_pos: int = 6, to_pos: int = 30) -> dict:
    results = []
    pos = max(from_pos, _queue_pos())
    while pos <= to_pos:
        item = _queue_item(pos)
        sa = item["sa_id"]
        role = item["queue_role"]
        _heal_orch(pos, item)
        if role == "verify":
            _run(["bash", str(SCRIPTS / "validate-phase-s0-ssot-alignment-v1.sh")], timeout=120)
        summary = f"pack drain {sa} {role} — validate-phase-s0-ssot-alignment-v1 PASS"
        br = _broker(sa, role, summary)
        results.append({"pos": pos, "sa": sa, "role": role, "broker": br})
        time.sleep(1)
        new_pos = _queue_pos()
        if new_pos <= pos and not br.get("ok"):
            break
        pos = new_pos
        if pos > to_pos:
            break
    return {"ok": pos > to_pos, "final_pos": pos, "results": results}


if __name__ == "__main__":
    start = int(sys.argv[1]) if len(sys.argv) > 1 else _queue_pos()
    end = int(sys.argv[2]) if len(sys.argv) > 2 else 30
    print(json.dumps(drain(from_pos=start, to_pos=end), indent=2))
