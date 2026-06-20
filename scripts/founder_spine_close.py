#!/usr/bin/env python3
"""Founder one-tap helpers — close spine loop using hub running task."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from execution_state_hub import mark_done, mark_failed, mark_verifying, status_payload  # noqa: E402


def _running_task(lane: str) -> str:
    st = status_payload(lane=lane)
    tid = st.get("running_task_id") or ""
    if not tid:
        tasks = st.get("runtime_tasks") or {}
        for k, v in tasks.items():
            if v in ("running", "verifying", "scheduled"):
                return k
    return tid


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--action", required=True, choices=["mark-done", "mark-verifying", "mark-failed"])
    parser.add_argument("--lane", default="sourcea")
    parser.add_argument("--id", default="")
    parser.add_argument("--verify-failed", action="store_true")
    parser.add_argument("--reason", default="")
    args = parser.parse_args()

    task_id = (args.id or "").strip() or _running_task(args.lane)
    if not task_id:
        print(json.dumps({"ok": False, "error": "no running task for lane"}))
        sys.exit(1)

    if args.action == "mark-done":
        out = mark_done(lane=args.lane, task_id=task_id, verify_passed=not args.verify_failed)
    elif args.action == "mark-verifying":
        out = mark_verifying(lane=args.lane, task_id=task_id)
    else:
        out = mark_failed(lane=args.lane, task_id=task_id, reason=args.reason or "founder marked failed")

    print(json.dumps(out, indent=2))
    sys.exit(0 if out.get("ok") else 1)


if __name__ == "__main__":
    main()
