#!/usr/bin/env bash
# validate-mac-health-settings-v1.sh — Auto guard settings API + UI wired (recipe gate)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
PORT="${MAC_HEALTH_PORT:-13024}"
BASE="http://127.0.0.1:${PORT}"
fail=0

check() {
  if "$@"; then
    echo "PASS: $*"
  else
    echo "FAIL: $*"
    fail=1
  fi
}

check test -f scripts/mac_health_settings_v1.py
check grep -q 'handle_settings_action' scripts/mac_health_settings_v1.py
check grep -q 'build_auto_guard_explainer' scripts/mac_health_settings_v1.py
check grep -q 'settings_save' scripts/mac_health_guard.py
check grep -q 'paintSettings' scripts/mac-health-standalone/app.js
check grep -q 'settings-explainer' scripts/mac-health-standalone/index.html

curl -sf "${BASE}/health" >/dev/null || { echo "FAIL: heart down on :${PORT}"; exit 1; }

body=$(curl -sf -X POST "${BASE}/api/mac-health" \
  -H "Content-Type: application/json" \
  -d '{"action":"settings","standalone":true}' || echo '{"ok":false}')

python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok') is True, d
assert d.get('values',{}).get('cursor') is not None, 'missing cursor settings'
assert d.get('explainer',{}).get('steps'), 'missing explainer steps'
assert len(d.get('schema') or []) >= 4, 'schema groups'
cur=d['values']['cursor']
assert cur.get('auto_restart_on_unattended_panic') is False, 'default must not auto-quit Cursor'
ch=d['values'].get('chrome') or {}
assert ch.get('quit_on_cool_down_mode') == 'when_mac_hot', 'default smart Chrome on Cool Down'
print('PASS: settings API action')
" <<<"$body" || fail=1

if [[ -f "${HOME}/.sina/config/mac-health-panic-v1.json" ]]; then
  python3 -c "
import json
from pathlib import Path
p=Path('${HOME}/.sina/config/mac-health-panic-v1.json')
d=json.loads(p.read_text())
cw=d.get('cpu_warn') or {}
assert 'system_cpu_pct' in cw or cw.get('enabled') is not False, 'cpu_warn block missing'
print('PASS: cpu_warn block on disk in panic JSON')
" || fail=1
else
  echo "WARN: mac-health-panic-v1.json absent — cpu_warn disk check skipped"
fi

report=$(curl -sf -X POST "${BASE}/api/mac-health" \
  -H "Content-Type: application/json" \
  -d '{"action":"report","standalone":true}' || echo '{"ok":false}')

python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('settings'), 'report missing settings'
assert d.get('auto_guard_explainer'), 'report missing auto_guard_explainer'
assert d.get('settings_schema'), 'report missing settings_schema'
print('PASS: report embeds settings + explainer')
" <<<"$report" || fail=1

for base in \
  "$ROOT/brand/macos-apps/Mac Health Guard.app/Contents/Resources/mac-health-bundle/scripts" \
  "$HOME/Desktop/Mac Health Guard.app/Contents/Resources/mac-health-bundle/scripts"; do
  if [[ -d "$base" ]]; then
    if [[ -f "$base/mac_health_settings_v1.py" ]]; then
      echo "PASS: settings module in bundle $base"
    else
      echo "FAIL: mac_health_settings_v1.py missing in $base — run sync-standalone-apps-to-bundles-v1.sh"
      fail=1
    fi
  fi
done

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-settings-v1: PASS"
else
  echo "validate-mac-health-settings-v1: FAIL"
fi
exit "$fail"
