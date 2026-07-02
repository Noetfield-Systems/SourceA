#!/usr/bin/env python3
"""Ship-window E2E bundle — client proof + promote + autorun + brain gate."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

STEPS = [
    ("client_proof_public", [sys.executable, str(ROOT / "scripts/run_founder_proof_post_publish_v1.py"), "--json", "--min-seconds-after-deploy", "0"]),
    ("locked_definitions_promote", [sys.executable, str(ROOT / "scripts/promote_locked_definitions_v1.py"), "--json"]),
    ("autorun_sink_sustain", [sys.executable, str(ROOT / "scripts/verify_autorun_zero_manual_v1.py"), "--json"]),
    ("brain_core_production_gate", [sys.executable, str(ROOT / "scripts/verify_brain_core_production_gate_v1.py"), "--json", "--write-receipt"]),
]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows = []
    ok = True
    for step_id, cmd in STEPS:
        proc = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True)
        step_ok = proc.returncode == 0
        try:
            payload = json.loads(proc.stdout)
            step_ok = step_ok and payload.get("ok", True) is not False
        except json.JSONDecodeError:
            payload = {"stdout_tail": (proc.stdout or "")[-400:]}
        rows.append({"step": step_id, "ok": step_ok, "returncode": proc.returncode, "payload": payload})
        ok = ok and step_ok
    row = {"schema": "client-proof-ship-window-v1", "ok": ok, "steps": rows}
    if args.json:
        print(json.dumps(row, indent=2))
    else:
        print(f"ok={ok}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
