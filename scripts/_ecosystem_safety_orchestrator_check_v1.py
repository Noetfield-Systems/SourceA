#!/usr/bin/env python3
"""INBOX vs orchestrator — auto-sync drift then assert (sa-0055 class)."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


def _orch_status() -> dict:
    return json.loads(
        subprocess.check_output(
            [sys.executable, str(SCRIPTS / "healthy-drain-orchestrator-v1.py"), "status"],
            text=True,
        )
    )


def _inbox_status() -> dict:
    return json.loads(
        subprocess.check_output(
            [sys.executable, str(SCRIPTS / "worker_inject_lib.py"), "--status"],
            text=True,
        )
    )


def main() -> int:
    from worker_stuck_recovery_v1 import sync_orchestrator_from_inbox  # noqa: WPS433

    inbox = _inbox_status()
    orch = _orch_status()
    o = orch.get("orchestrator") or {}

    if inbox.get("pending"):
        sa_inbox = str(inbox.get("sa_id") or (inbox.get("meta") or {}).get("sa_id") or "")
        sa_orch = str(o.get("expected_sa") or "")
        if sa_inbox and sa_inbox != sa_orch:
            sync = sync_orchestrator_from_inbox()
            if not sync.get("ok"):
                print(f"FAIL: orchestrator sync: {sync}", file=sys.stderr)
                return 1
            if sync.get("synced"):
                print(f"healed: orchestrator aligned to inbox {sa_inbox}")
            orch = _orch_status()
            o = orch.get("orchestrator") or {}
        assert sa_inbox == str(o.get("expected_sa") or ""), (
            f"inbox {sa_inbox} != orchestrator {o.get('expected_sa')}"
        )

    print(
        f"orchestrator: {o.get('expected_sa')} role={o.get('expected_role')} "
        f"inbox_pending={inbox.get('pending')}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
