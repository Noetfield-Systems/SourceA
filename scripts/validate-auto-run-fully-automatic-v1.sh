#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

test -f "$ROOT/brain-os/laws/AUTO_RUN_FULLY_AUTOMATIC_LOCKED_v1.md"
test -f "$ROOT/scripts/auto_run_worker_batch_v1.py"
test -f "$ROOT/scripts/auto_start_worker_batch_on_hub_v1.sh"
test -x "$ROOT/scripts/auto_start_worker_batch_on_hub_v1.sh"
test -f "$ROOT/launch/com.sourcea.autorun-worker.plist"
test -f "$ROOT/scripts/install-autorun-launchd-v1.sh"
grep -q "schedule_after_batch" "$ROOT/scripts/goal1_worker_batch_loop_v1.py"
grep -q "_kick_autorun_on_hub_start" "$ROOT/scripts/sina-command-server.py"
grep -q "auto_start_worker_batch_on_hub_v1.sh" "$ROOT/scripts/serve-sina-command.sh"
grep -q "SINA_AUTORUN_ENABLED" "$ROOT/launch/com.sourcea.autorun-worker.plist"

launchctl print "gui/$(id -u)/com.sourcea.autorun-worker" >/dev/null 2>&1 || {
  echo "WARN: autorun launchd not loaded — run install-autorun-launchd-v1.sh" >&2
}

python3 "$ROOT/scripts/auto_run_worker_batch_v1.py" --status --json | python3 -c "
import json, sys
s = json.load(sys.stdin)
assert 'should' in s
print('autorun_status_ok')
"

echo "OK: validate-auto-run-fully-automatic-v1"
