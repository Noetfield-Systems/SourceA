#!/usr/bin/env bash
# validate-mac-health-panic-hotkey-v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
fail=0

check() { "$@" && echo "PASS: $*" || { echo "FAIL: $*"; fail=1; }; }

check test -f scripts/mac_health_emergency_stop_v1.py
check test -f brand/macos-apps/MacHealthPanicHotkey.swift
check test -f scripts/install-mac-health-panic-hotkey-v1.sh

python3 scripts/mac_health_emergency_stop_v1.py --dry-run --trigger validate --json \
  | python3 -c "import json,sys; d=json.load(sys.stdin); assert d.get('dry_run'); assert 'targets_before' in d or d.get('trigger')=='validate'"

grep -q 'emergency_stop' scripts/mac_health_guard.py && echo "PASS: guard action wired" || { echo "FAIL: guard action"; fail=1; }
check grep -q 'btn-panic-header' scripts/mac-health-standalone/index.html && echo "PASS: panic UI" || { echo "FAIL: panic UI"; fail=1; }

if pgrep -f MacHealthPanicHotkey >/dev/null 2>&1; then
  echo "PASS: panic hotkey daemon running"
else
  echo "WARN: panic hotkey daemon not running — run install-mac-health-panic-hotkey-v1.sh"
fi

exit "$fail"
