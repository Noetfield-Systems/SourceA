#!/usr/bin/env bash
# validate-mac-health-prevention-v1.sh — prevention module wired into live pulse
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"

fail=0
check() {
  if "$@"; then
    echo "PASS: $*"
  else
    echo "FAIL: $*"
    fail=1
  fi
}

check test -f scripts/mac_health_prevention_v1.py
check test -f "$HOME/.sina/config/mac-health-prevention-v1.json"

row="$(python3 scripts/mac_health_prevention_v1.py --analyze --json)"
echo "$row" | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('schema')=='mac-health-prevention-v1'; assert 'health' in d; assert 'founder_line' in d"

live="$(python3 scripts/mac_health_live_v1.py --json)"
echo "$live" | python3 -c "import json,sys; d=json.load(sys.stdin); p=d.get('prevention') or {}; assert 'health' in p, p"

if grep -q 'auto_sweep_queue_zombies' scripts/mac_health_prevention_v1.py; then
  echo "PASS: auto_sweep_queue_zombies on live pulse"
else
  echo "FAIL: auto_sweep_queue_zombies missing"
  fail=1
fi

if grep -q 'maybe_auto_prevent' scripts/mac_health_live_v1.py; then
  echo "PASS: live pulse calls maybe_auto_prevent"
else
  echo "FAIL: live pulse missing maybe_auto_prevent"
  fail=1
fi

if grep -q 'prevention-banner' scripts/mac-health-standalone/index.html; then
  echo "PASS: UI prevention banner"
else
  echo "FAIL: UI prevention banner missing"
  fail=1
fi

if grep -q 'run_wake_cool_down' scripts/mac_health_cpu_relief_v1.py; then
  echo "PASS: wake cool down relief"
else
  echo "FAIL: wake cool down relief missing"
  fail=1
fi

if grep -q 'cpu_wake_cool_down' scripts/mac-health-standalone/index.html; then
  echo "PASS: wake cool down UI button"
else
  echo "FAIL: wake cool down UI button missing"
  fail=1
fi

exit "$fail"
