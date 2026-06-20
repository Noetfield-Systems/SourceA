#!/usr/bin/env python3
"""Brain-side Goal 1 loop driver — starts turns without editor-tab false start.

When Worker chat is silent: Brain executor runs deliver + prints YAML for founder.
Law: SINA_GOAL1_OPERATING_MODEL_LOCKED_v1.md
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def _load_orch():
    spec = importlib.util.spec_from_file_location("orch", SCRIPTS / "healthy-drain-orchestrator-v1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


def start(*, force_deliver: bool = False) -> dict:
    sys.path.insert(0, str(SCRIPTS))
    from goal1_lane_broker import brain_poll, pickup_prompt_for_worker  # noqa: WPS433
    from worker_inject_lib import inbox_status  # noqa: WPS433

    orch = _load_orch()
    st = orch.orchestrator_state()
    inbox = inbox_status()

    if not inbox.get("pending") or force_deliver:
        if st.get("status") == "awaiting_worker" and inbox.get("pending"):
            pass
        elif st.get("status") != "awaiting_worker":
            orch.deliver_current(force=force_deliver)
        inbox = inbox_status()

    meta = inbox.get("meta") or {}
    out = {
        "status": "GOAL1_LOOP_START",
        "loop_started": True,
        "editor_opened": False,
        "note": "Disk delivery only — NOT an editor tab. Worker or Brain executor runs the turn.",
        "queue": f"{meta.get('queue_pos')}/{meta.get('queue_total')}",
        "role": meta.get("queue_role"),
        "sa_id": meta.get("sa_id"),
        "inbox_pending": inbox.get("pending"),
        "founder_brain": "Say 'execute turn' — Brain runs: python3 scripts/brain_execute_turn_v1.py --yaml",
        "founder_worker": "SourceA Worker chat → say run inbox (attach rule 099-worker-inbox-active.mdc)",
        "brain_poll": "python3 scripts/goal1_lane_broker.py brain-poll",
        "pickup": "python3 scripts/goal1_lane_broker.py pickup",
    }
    return out


def execute(*, loop: int = 1, yaml_out: bool = False) -> int:
    """Brain Core Executor — one agent turn (law: BRAIN_CORE_EXECUTOR_LOCKED_v1)."""
    cmd = [sys.executable, str(SCRIPTS / "brain_execute_turn_v1.py")]
    if loop > 1:
        cmd.extend(["--loop", str(min(loop, 5))])
    if yaml_out:
        cmd.append("--yaml")
    return subprocess.call(cmd, cwd=str(ROOT))


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("cmd", choices=("start", "execute", "status", "pickup"))
    p.add_argument("--force-deliver", action="store_true")
    p.add_argument("--loop", type=int, default=1)
    p.add_argument("--yaml", action="store_true")
    args = p.parse_args()

    if args.cmd == "execute":
        return execute(loop=args.loop, yaml_out=args.yaml)
    if args.cmd == "start":
        print(json.dumps(start(force_deliver=args.force_deliver), indent=2))
        return 0
    if args.cmd == "status":
        sys.path.insert(0, str(SCRIPTS))
        from goal1_lane_broker import brain_poll  # noqa: WPS433

        brain_poll(as_yaml=True)
        return 0
    if args.cmd == "pickup":
        sys.path.insert(0, str(SCRIPTS))
        from goal1_lane_broker import pickup_prompt_for_worker  # noqa: WPS433

        pickup_prompt_for_worker()
        return 0
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
