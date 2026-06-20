#!/usr/bin/env bash
# sa-0626 — system_roadmap Phase D column: 16 steps, status done when D16 shipped
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
import json
import subprocess
from pathlib import Path

scripts = Path.cwd()
out = subprocess.check_output(
    [__import__("sys").executable, str(scripts / "system_roadmap.py"), "--json"],
    text=True,
    cwd=str(scripts),
)
d = json.loads(out)
ph = next((p for p in d.get("phases") or [] if p.get("id") == "D"), {})
ui = (d.get("ui_contract") or {}).get("phase_d") or {}
live = (d.get("live") or {}).get("future_phase") or {}

assert ph.get("status") == "done", f"phases[D].status={ph.get('status')}"
assert ui.get("step_count") == 16, f"step_count={ui.get('step_count')}"
assert live.get("status") == "done", f"future_phase={live.get('status')}"

print(
    f"OK: validate-system-roadmap-phase-d-v1 · D=done steps=16 future_phase=done"
)
PY
