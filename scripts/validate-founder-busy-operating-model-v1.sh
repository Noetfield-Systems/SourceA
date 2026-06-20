#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f "$ROOT/brain-os/laws/FOUNDER_BUSY_OPERATING_MODEL_LOCKED_v1.md"
test -f "$ROOT/scripts/operating_mode_enforce_v1.py"
grep -q "FOUNDER_BUSY_OPERATING_MODEL" "$ROOT/scripts/cursor_entry_gate.py"

ROOT="$ROOT" python3 -c '
import json
import os
import subprocess
import sys
from pathlib import Path

root = Path(os.environ["ROOT"])
script = root / "scripts" / "operating_mode_enforce_v1.py"

def run(args):
    proc = subprocess.run(
        [sys.executable, str(script), *args, "--json"],
        cwd=str(root),
        capture_output=True,
        text=True,
    )
    raw = (proc.stdout or "").strip()
    assert raw, proc.stdout + proc.stderr
    return json.loads(raw)

sit = run(["--check-situation"])
assert sit.get("valid"), sit
print("situation", sit.get("founder_mode"))

act_w = run(["--check-engine", "--role", "act", "--engine", "worker"])
assert act_w.get("valid"), act_w
print("act_worker_ok")

act_cli = run(["--check-engine", "--role", "act", "--engine", "cli"])
assert not act_cli.get("valid"), act_cli
print("act_cli_blocked_busy_ok")

act_api = run(["--check-engine", "--role", "act", "--engine", "api"])
assert not act_api.get("valid"), act_api
print("act_api_blocked_ok")

chk_api = run(["--check-engine", "--role", "check", "--engine", "api"])
assert chk_api.get("valid"), chk_api
print("check_api_awake_ok")

ver_api = run(["--check-engine", "--role", "verify", "--engine", "api"])
assert ver_api.get("valid"), ver_api
print("verify_api_awake_ok")

autorun = run(["--check-autorun"])
assert not autorun.get("valid"), autorun
print("autorun_off_busy_ok")
'

echo "OK: validate-founder-busy-operating-model-v1"
