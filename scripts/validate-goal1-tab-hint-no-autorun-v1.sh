#!/usr/bin/env bash
# validate-goal1-tab-hint-no-autorun-v1.sh — Goal1 tab must not promote START AUTO RUN under FREEZE (AS-18)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from factory_control_v1 import load_factory_now

fn = load_factory_now()
freeze = bool(fn.get("kill_flag")) or str(fn.get("mode")) == "FREEZE"

cmd = Path("agent-control-panel/command-data.json")
if not cmd.is_file():
    print("FAIL: command-data.json missing")
    sys.exit(1)

data = json.loads(cmd.read_text(encoding="utf-8"))
# Refresh projection before read
import subprocess
subprocess.run(["python3", "scripts/align_command_data_ui_v1.py"], cwd=".", capture_output=True, timeout=120)
data = json.loads(cmd.read_text(encoding="utf-8"))
g1 = data.get("goal1_auto_run") or data.get("goal1_loop") or {}
hint = str(g1.get("tab_hint") or "").lower()

if freeze:
    for bad in ("start auto run", "▶ start", "goal 1 auto-run"):
        if bad in hint:
            print(f"FAIL: goal1 tab_hint promotes AUTO-RUN under FREEZE: {hint[:96]!r}")
            sys.exit(1)
    if g1.get("primary_action_id") == "founder-goal1-autorun-start":
        print("FAIL: primary_action_id still autorun-start under FREEZE")
        sys.exit(1)

print("OK: validate-goal1-tab-hint-no-autorun-v1")
PY
