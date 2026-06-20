#!/usr/bin/env python3
"""Goal 1 E2E repair — kill leftovers, reconcile SSOT, run validators.

Executor only. Law: BRAIN_NO_LEFTOVER_PROCESS_LOCKED_v1.md
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
RECEIPT = Path.home() / ".sina" / "repair-goal1-e2e-v1.json"


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run(cmd: list[str], *, timeout: int = 120) -> dict:
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(ROOT),
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return {
            "ok": proc.returncode == 0,
            "exit_code": proc.returncode,
            "stdout": (proc.stdout or "")[-3000:],
            "stderr": (proc.stderr or "")[-1500:],
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc)}


def repair(*, run_e2e: bool = True) -> dict:
    steps: list[dict] = []
    sys.path.insert(0, str(SCRIPTS))

    cleanup = _run([sys.executable, str(SCRIPTS / "cleanup-goal1-leftovers-v1.py"), "--json"])
    steps.append({"id": "cleanup", **cleanup})
    try:
        cleanup_row = json.loads(cleanup.get("stdout") or "{}")
        steps[-1]["remaining_count"] = cleanup_row.get("remaining_count")
    except json.JSONDecodeError:
        pass

    from duplicate_inject_guard_v1 import clear_inject_lock  # noqa: WPS433
    from worker_inject_lib import clear_inbox, inbox_status  # noqa: WPS433

    steps.append({"id": "clear_inject_lock", **clear_inject_lock()})
    ib = inbox_status()
    if ib.get("pending"):
        steps.append(
            {
                "id": "clear_inbox",
                "ok": True,
                "skipped": True,
                "reason": "inbox_pending_preserved",
                "sa_id": ib.get("sa_id"),
                "queue_pos": ib.get("queue_pos"),
            }
        )
    else:
        steps.append({"id": "clear_inbox", **clear_inbox(reason="repair_goal1_e2e")})

    ptr = _run([sys.executable, str(SCRIPTS / "sync_next_execution_pointer_v1.py")])
    steps.append({"id": "sync_pointer", **ptr})

    from active_now_v1 import sync_active_now_from_queue  # noqa: WPS433

    steps.append({"id": "sync_active_now", **sync_active_now_from_queue()})

    spec = importlib.util.spec_from_file_location("orch", SCRIPTS / "healthy-drain-orchestrator-v1.py")
    orch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(orch)  # type: ignore[union-attr]
    steps.append({"id": "orchestrator_reset", **orch.reset(reason="repair_goal1_e2e")})

    brain = _run([sys.executable, str(SCRIPTS / "brain_read_state_v1.py")])
    steps.append({"id": "brain_read_state", **brain})
    try:
        st = json.loads(brain.get("stdout") or "{}")
        steps[-1]["aligned"] = st.get("aligned")
    except json.JSONDecodeError:
        pass

    gate = _run([sys.executable, str(SCRIPTS / "gatekeeper_v1.py"), "--no-broker"])
    steps.append({"id": "gatekeeper", **gate})

    if run_e2e:
        e2e = _run(["bash", str(SCRIPTS / "validate-goal1-e2e-v1.sh")], timeout=180)
        steps.append({"id": "validate_goal1_e2e", **e2e})
        ib_post = inbox_status()
        if ib_post.get("pending"):
            steps.append(
                {
                    "id": "post_e2e_clear_inbox",
                    "ok": True,
                    "skipped": True,
                    "reason": "inbox_pending_preserved",
                }
            )
        else:
            steps.append({"id": "post_e2e_clear_inbox", **clear_inbox(reason="repair_post_e2e")})
        steps.append({"id": "post_e2e_orchestrator_reset", **orch.reset(reason="repair_post_e2e")})
        clear_inject_lock()

    brain_aligned = False
    try:
        brain_row = json.loads(steps[6].get("stdout") or "{}")
        brain_aligned = bool(brain_row.get("aligned"))
    except (json.JSONDecodeError, IndexError, KeyError):
        pass
    ok = (
        steps[0].get("remaining_count", 1) == 0
        and steps[4].get("ok", True)
        and brain_aligned
        and steps[7].get("ok", False)
        and (not run_e2e or steps[-1].get("ok"))
    )
    row_extra = {"brain_aligned": brain_aligned}
    row = {
        "schema": "repair-goal1-e2e-v1",
        "at": _now(),
        "ok": ok,
        **row_extra,
        "steps": steps,
    }
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text(json.dumps(row, indent=2) + "\n", encoding="utf-8")
    return row


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description="Repair Goal 1 E2E SSOT alignment")
    p.add_argument("--skip-e2e", action="store_true")
    p.add_argument("--json", action="store_true")
    args = p.parse_args()
    row = repair(run_e2e=not args.skip_e2e)
    print(json.dumps(row, indent=2))
    return 0 if row.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
