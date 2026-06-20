#!/usr/bin/env bash
# Choice 1+ unified auto-run — hub hero START/STOP only; orchestrator flag lifecycle.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f "$ROOT/scripts/goal1_unified_autorun_v1.py"
python3 -m py_compile "$ROOT/scripts/goal1_unified_autorun_v1.py"

grep -q "founder-goal1-autorun-start" "$ROOT/scripts/sina_command_lib.py"
grep -q "founder-goal1-autorun-stop" "$ROOT/scripts/sina_command_lib.py"
grep -q "goal1_unified_autorun_start" "$ROOT/scripts/sina_command_lib.py"
grep -q '"hidden": True' "$ROOT/scripts/sina_command_lib.py"

grep -q "goal1-autorun-start" "$ROOT/scripts/sina-command-server.py"
grep -q "goal1-autorun-stop" "$ROOT/scripts/sina-command-server.py"

WORKER_HUB=$(
  python3 - <<'PY'
import sys
sys.path.insert(0, "scripts")
from hub_worker_mode_v1 import worker_hub_mode
print("1" if worker_hub_mode() else "0")
PY
)

if [[ "$WORKER_HUB" == "1" ]]; then
  python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
from goal1_unified_autorun_v1 import ORCH_FLAG

for needle in (
    "founder-goal1-autorun-start",
    "founder-goal1-autorun-stop",
    "goal1_unified_autorun_start",
):
    lib = Path("scripts/sina_command_lib.py").read_text(encoding="utf-8")
    assert needle in lib, f"missing {needle} in sina_command_lib.py"

server = Path("scripts/sina-command-server.py").read_text(encoding="utf-8")
assert "goal1-autorun-start" in server and "goal1-autorun-stop" in server

ORCH_FLAG.parent.mkdir(parents=True, exist_ok=True)
ORCH_FLAG.write_text(json.dumps({"schema": "validate-test"}) + "\n", encoding="utf-8")
assert ORCH_FLAG.is_file()
ORCH_FLAG.unlink(missing_ok=True)
print("OK: validate-goal1-unified-autorun-v1 · H1 worker-hub — server+lib wired · app.js retired")
PY
else
APP="$ROOT/agent-control-panel/assets/app.js"
grep -q "founder-goal1-autorun-start" "$APP"
grep -q "founder-goal1-autorun-stop" "$APP"
grep -q "sc-goal1-autorun-hero" "$APP"
grep -q "renderGoal1AutorunHero" "$APP"
grep -q "data-autorun-toggle" "$APP"
grep -q "goal1AutorunAction" "$APP"
! grep -q "founder-start-worker-batch-5" "$APP"
! grep -q "founder-start-worker-batch-10" "$APP"
! grep -q "founder-execute-turn" "$APP"
! grep -q "START BATCH" "$APP"

python3 <<'PY'
import re
from pathlib import Path

app = Path("agent-control-panel/assets/app.js").read_text(encoding="utf-8")
m = re.search(r"function renderGoal1AutoRun\(\).*?(?=function \w+\()", app, re.S)
if not m:
    raise SystemExit("FAIL: renderGoal1AutoRun missing")
body = m.group(0)
if "renderGoal1AutorunHero" not in body:
    raise SystemExit("FAIL: renderGoal1AutoRun must use renderGoal1AutorunHero")
for bad in (
    "founder-execute-turn",
    "founder-start-worker-batch-5",
    "founder-start-worker-batch-10",
):
    if bad in body:
        raise SystemExit(f"FAIL: renderGoal1AutoRun still references {bad}")
print("OK: renderGoal1AutoRun primary surfaces clean")
PY

python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
from goal1_unified_autorun_v1 import ORCH_FLAG

ORCH_FLAG.parent.mkdir(parents=True, exist_ok=True)
ORCH_FLAG.write_text(json.dumps({"schema": "validate-test"}) + "\n", encoding="utf-8")
assert ORCH_FLAG.is_file(), "flag not created"
ORCH_FLAG.unlink(missing_ok=True)
assert not ORCH_FLAG.is_file(), "flag not cleared"
print("OK: orchestrator autorun flag lifecycle (no live loop kill)")
PY
fi

echo "OK: validate-goal1-unified-autorun-v1"
