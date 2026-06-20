#!/usr/bin/env bash
# validate-factory-conduct-v1.sh — unified conduct plane (spawn · now · start law)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"

fail() { echo "FAIL: validate-factory-conduct-v1 — $*" >&2; exit 1; }

[[ -f "$SCRIPTS/factory_control_v1.py" ]] || fail "missing factory_control_v1.py"
grep -q "def drain_spawn_allowed" "$SCRIPTS/factory_control_v1.py" || fail "missing drain_spawn_allowed"
grep -q "def rebuild_factory_now" "$SCRIPTS/factory_control_v1.py" || fail "missing rebuild_factory_now"

for file in \
  worker_healthy_pack_autodrain_v1.py \
  worker_healthy_pack_loop_v1.py \
  goal1_auto_run_v1.py \
  goal1_worker_batch_loop_v1.py \
  goal1_unified_autorun_v1.py \
  goal1_auto_run_deliver_v1.py \
  healthy-drain-orchestrator-v1.py \
  auto_run_worker_batch_v1.py; do
  grep -q "factory_spawn_gate_v1\|factory_control_v1" "$SCRIPTS/$file" \
    || fail "$file must call spawn gate"
done

grep -q "write_stop_receipt" "$SCRIPTS/stop_goal1_auto_run_v1.py" \
  || fail "stop script must write stop receipt"

if grep -q 'rm -f.*auto-run-disabled-v1.flag' "$SCRIPTS/start-sourcea.sh"; then
  fail "start-sourcea.sh still removes kill flag"
fi
for bad in install-autorun.sh start-overnight-3engine-v1.sh; do
  if grep -q 'rm -f.*auto-run-disabled-v1.flag' "$SCRIPTS/$bad"; then
    fail "$bad still removes kill flag"
  fi
done
if grep -q 'rm -f.*auto-run-disabled-v1.flag' "$SCRIPTS/install-autorun.sh"; then
  fail "install-autorun.sh still documents illegal rm resume"
fi
grep -q "factory_control_v1.py resume" "$SCRIPTS/install-autorun.sh" \
  || fail "install-autorun.sh must document factory_control resume"

grep -q "factory_now_line\|factory_control_v1" "$SCRIPTS/cursor_entry_gate.py" \
  || fail "entry gate must cite factory-now"

python3 "$SCRIPTS/factory_control_v1.py" now --rebuild >/dev/null \
  || fail "factory_now rebuild smoke failed"

NOW="${HOME}/.sina/factory-now-v1.json"
[[ -f "$NOW" ]] || fail "factory-now-v1.json missing"
python3 -c "
import json
d=json.load(open('$NOW'))
assert d.get('schema')=='factory-now-v1' and 'line' in d
"

# STOP receipt + kill flag when FREEZE (INCIDENT-015 conduct)
python3 -c "
import json
from pathlib import Path
now = json.load(open(Path.home() / '.sina/factory-now-v1.json'))
if now.get('mode') == 'FREEZE' or now.get('kill_flag'):
    stop = Path.home() / '.sina/founder-stop-receipt-v1.json'
    flag = Path.home() / '.sina/auto-run-disabled-v1.flag'
    assert flag.is_file(), 'kill flag must exist under FREEZE'
"

echo "OK: validate-factory-conduct-v1"
