#!/usr/bin/env bash
# validate-mac-health-log-shield-v1.sh — Log Shield probe + hub truth schema gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
MH_VER="$(python3 -c "from mac_health_version_v1 import MAC_HEALTH_VERSION; print(MAC_HEALTH_VERSION)")"
fail=0

check() {
  if "$@"; then
    echo "PASS: $*"
  else
    echo "FAIL: $*"
    fail=1
  fi
}

echo "=== Mac Health Log Shield v1 validator ==="

check test -f scripts/mac_health_log_shield_v1.py
check grep -q 'build_log_shield_probe' scripts/mac_health_log_shield_v1.py
check grep -q 'probe_hub_truth' scripts/mac_health_log_shield_v1.py
check grep -q 'hub_health_ok' scripts/mac_health_log_shield_v1.py
check grep -q 'truncate_runaway_logs' scripts/mac_health_log_shield_v1.py
check grep -q 'mac_health_log_shield_v1' scripts/mac_health_guard.py
check grep -q 'id="log-shield"' scripts/mac-health-standalone/index.html
check grep -q 'hub-truth-badge' scripts/mac-health-standalone/index.html
check grep -q 'paintLogShield' scripts/mac-health-standalone/app.js
check grep -q "v${MH_VER}" scripts/mac-health-standalone/index.html

python3 scripts/mac_health_log_shield_v1.py --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('schema')=='mac-health-log-shield-probe-v1', d
assert 'hub_health_ok' in d, d
assert 'sina_log_bomb' in d, d
assert 'stuck_log_readers' in d, d
print('PASS: log shield probe schema')
" || fail=1

python3 scripts/mac_health_live_v1.py --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
mp=d.get('machine_pressure') or {}
assert 'hub_health_ok' in mp, 'missing hub_health_ok in live pulse'
assert 'sina_log_bomb' in mp, 'missing sina_log_bomb in live pulse'
print('PASS: live pulse carries log shield fields')
" || fail=1

if grep -q 'LOG.read_text' scripts/find_critical_bugs.py; then
  echo "FAIL: find_critical_bugs must not use LOG.read_text"
  fail=1
else
  echo "PASS: find_critical_bugs tail-only log scan"
fi

if [[ "$fail" -eq 0 ]]; then
  echo "=== validate-mac-health-log-shield-v1: ALL PASS ==="
else
  echo "=== validate-mac-health-log-shield-v1: FAILED ==="
fi
exit "$fail"
