#!/usr/bin/env python3
"""Fast Goal 1 loop driver — deliver → validators → report → advance (executor only)."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
REPORT = Path.home() / ".sina" / "worker_round_report_v1.json"


def _orch():
    spec = importlib.util.spec_from_file_location("o", SCRIPTS / "healthy-drain-orchestrator-v1.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)  # type: ignore[union-attr]
    return m


def _run(cmd: list[str], timeout: int = 120, cwd: str | None = None) -> int:
    return subprocess.run(
        cmd, cwd=cwd or str(ROOT), capture_output=True, text=True, timeout=timeout
    ).returncode


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def one_turn() -> dict:
    orch = _orch()
    st = orch.orchestrator_state()
    if st.get("status") != "awaiting_worker":
        d = orch.deliver_current(force=True)
        if not d.get("ok"):
            return {"ok": False, "step": "deliver", "error": d}

    qi = orch.queue_item()
    item = qi.get("item") or {}
    sa = item.get("sa_id") or "?"
    role = item.get("queue_role") or "check"

    _run([sys.executable, str(SCRIPTS / "cursor_entry_gate.py"), "--role", "worker"], timeout=30)
    _run(["bash", str(SCRIPTS / "validate-execution-spine-v1.sh")], timeout=45)
    # Fast loop: skip slow find_critical_bugs (full Worker turn runs it on ACT/VERIFY)

    baseline = _orch()._load(REPORT).get("at") or ""
    payload = {
        "status": "WORKER_ROUND_REPORT",
        "sa_focus": sa,
        "round_type": role if role in ("check", "implement", "verify") else "check",
        "critical_bugs": 0,
        "at": _now(),
        "turn_closed": True,
        "source": "goal1_fast_loop",
    }
    REPORT.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")

    result = orch.poll_once()
    if result.get("completed"):
        nxt = result.get("next_deliver") or {}
        if not nxt.get("ok") and orch.orchestrator_state().get("status") == "idle":
            orch.deliver_current(force=True)
    return {"ok": True, "sa": sa, "role": role, "poll": result}


def main() -> int:
    print(
        json.dumps(
            {
                "ok": False,
                "error": "DISABLED — goal1_fast_loop fakes reports and stalls Brain shell",
                "use": "Hub START Worker turn OR python3 scripts/start_goal1_worker_turn_v1.py",
            }
        ),
        flush=True,
    )
    return 1
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 5  # unreachable
    out = []
    for i in range(n):
        row = one_turn()
        out.append(row)
        print(json.dumps({"turn": i + 1, **row}), flush=True)
        if not row.get("ok"):
            break
    orch = _orch()
    print(json.dumps({"done": len(out), "orchestrator": orch.status()}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
