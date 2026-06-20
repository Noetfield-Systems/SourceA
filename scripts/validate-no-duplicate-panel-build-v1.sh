#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
export PATH="/opt/homebrew/bin:/usr/local/bin:${PATH:-/usr/bin:/bin}"

python3 - <<'PY'
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"

bowl = (SCRIPTS / "build-sina-daily-bowl.py").read_text(encoding="utf-8")
lib = (SCRIPTS / "sina_command_lib.py").read_text(encoding="utf-8")
fleet = (SCRIPTS / "scan-cursor-agent-fleet.py").read_text(encoding="utf-8")

assert "SINA_SKIP_PANEL_BUILD" in bowl, "bowl missing SINA_SKIP_PANEL_BUILD guard"
assert "skip nested panel build" in bowl, "bowl missing sa-0222 skip log"
assert "SINA_SKIP_PANEL_BUILD" in lib and '"SINA_SKIP_PANEL_BUILD": "1"' in lib, (
    "run_refresh_pipeline must set SINA_SKIP_PANEL_BUILD"
)
assert "SINA_SKIP_PANEL_BUILD" in fleet, "fleet scan missing panel skip guard"

env = {
    **os.environ,
    "SINA_SKIP_PANEL_BUILD": "1",
    "SINA_SKIP_FLEET_SCAN": "1",
}
proc = subprocess.run(
    [sys.executable, str(SCRIPTS / "build-sina-daily-bowl.py")],
    cwd=str(SCRIPTS),
    env=env,
    capture_output=True,
    text=True,
    timeout=120,
)
out = (proc.stdout or "") + (proc.stderr or "")
assert proc.returncode == 0, f"bowl failed under skip env: {out[-400:]}"
assert "skip nested panel build" in out, f"bowl did not log panel skip: {out[-400:]}"

print("OK: validate-no-duplicate-panel-build-v1 · bowl skips panel when SINA_SKIP_PANEL_BUILD=1")
PY
