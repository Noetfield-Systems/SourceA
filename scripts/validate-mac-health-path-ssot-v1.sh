#!/usr/bin/env bash
# validate-mac-health-path-ssot-v1.sh — no stale ~/Desktop/SourceA without resolver fallback
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

check() {
  if "$@"; then echo "PASS: $*"; else echo "FAIL: $*"; fail=1; fi
}

check_no_stale_default() {
  local f="$1"
  [[ -f "$f" ]] || return 0
  if grep -q 'Desktop/SourceA' "$f" && ! grep -q 'resolve_sourcea_root' "$f" && ! grep -q 'Noetfield-Systems/SourceA' "$f"; then
    echo "FAIL: $f uses Desktop/SourceA without resolver"
    fail=1
  else
    echo "PASS: $f path SSOT"
  fi
}

echo "=== Mac Health path SSOT v1 ==="
check test -f "$ROOT/scripts/resolve_sourcea_root_v1.sh"
check grep -q 'resolve_sourcea_root' "$ROOT/scripts/serve-mac-health-guard.sh"
check grep -q 'resolve_sourcea_root' "$ROOT/scripts/install-mac-health-launchagent-v1.sh"
check_no_stale_default "$ROOT/scripts/install-mac-health-launchagent-v1.sh"
check_no_stale_default "$ROOT/scripts/install-mac-health-panic-hotkey-v1.sh"
check_no_stale_default "$ROOT/scripts/install-mac-health-panic-listener-v1.sh"

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-path-ssot-v1: ALL PASS"
  exit 0
fi
echo "validate-mac-health-path-ssot-v1: FAILED"
exit 1
