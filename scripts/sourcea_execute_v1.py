#!/usr/bin/env python3
"""SourceA single execution entry — Gatekeeper first, then executor.

Law: brain-os/laws/SOURCEA_INVARIANT_GATEKEEPER_BLUEPRINT_LOCKED_v1.md

Usage:
  python3 scripts/sourcea_execute_v1.py --dry-run
  python3 scripts/sourcea_execute_v1.py --engine worker
  python3 scripts/sourcea_execute_v1.py --engine cli
  python3 scripts/sourcea_execute_v1.py --engine api
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


def main() -> int:
    p = argparse.ArgumentParser(description="SourceA execute — gatekeeper → executor")
    p.add_argument("--engine", choices=("worker", "cli", "api", "auto"), default="auto")
    p.add_argument("--role", default="")
    p.add_argument("--sa", default="")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--json", action="store_true")
    p.add_argument("--demo-enforcement", action="store_true")
    p.add_argument("--case", choices=("block", "allow"), default="allow")
    args = p.parse_args()

    if args.demo_enforcement:
        cmd = [
            sys.executable,
            str(SCRIPTS / "commit_intent_v1.py"),
            "--demo-enforcement",
            "--case",
            args.case,
        ]
        if args.dry_run:
            cmd.append("--dry-run")
        if args.json:
            cmd.append("--json")
        proc = subprocess.run(cmd, cwd=str(ROOT))
        return proc.returncode

    sys.path.insert(0, str(SCRIPTS))
    from gatekeeper_v1 import run_gatekeeper, format_human  # noqa: WPS433
    from healthy_queue_ssot_lib import load_healthy_queue, queue_items  # noqa: WPS433

    _, qdata = load_healthy_queue()
    items = queue_items(qdata)
    role = (args.role or "").lower().strip()
    if not role and items:
        import json
        from pathlib import Path as P

        st = P.home() / ".sina/healthy-queue-state-v1.json"
        pos = 1
        if st.is_file():
            pos = int(json.loads(st.read_text()).get("next_pos") or 1)
        idx = max(0, pos - 1)
        if idx < len(items):
            role = (items[idx].get("queue_role") or "act").lower()

    from active_now_v1 import load_active_now  # noqa: WPS433

    mode = (load_active_now().get("founder_mode") or "founder_busy").lower()
    engine = args.engine
    if engine == "auto":
        api_roles = {"check", "verify", "audit", "review", "test", "validate", "read"}
        if any(r in role for r in api_roles):
            engine = "api"
        elif mode == "founder_busy":
            engine = "worker"
        else:
            engine = "cli"

    gate = run_gatekeeper(
        sa_id=args.sa,
        role=role,
        engine=engine,
        caller="sourcea_execute",
    )
    if args.json:
        import json

        print(json.dumps({"gatekeeper": gate}))
    elif not gate.get("safe_to_execute"):
        print(format_human(gate))
        return 1

    if args.dry_run:
        print(format_human(gate))
        print(f"\nDRY RUN: would execute engine={engine} role={role}")
        return 0

    script = {
        "worker": "start_goal1_worker_turn_v1.py",
        "cli": "claude_code_agent_v1.py",
        "api": "claude_api_agent_v1.py",
    }[engine]

    proc = subprocess.run(
        [sys.executable, str(SCRIPTS / script)] + (["--dry-run"] if args.dry_run else []),
        cwd=str(ROOT),
    )
    return proc.returncode


if __name__ == "__main__":
    raise SystemExit(main())
