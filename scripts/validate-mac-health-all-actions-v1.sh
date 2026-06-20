#!/usr/bin/env bash
# validate-mac-health-all-actions-v1.sh — every UI action wired to live API (honest gate)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
PORT="${MAC_HEALTH_PORT:-13024}"
BASE="http://127.0.0.1:${PORT}"
fail=0

pass() {
  if "$@"; then echo "PASS: $*"; else echo "FAIL: $*"; fail=1; fi
}

post() {
  local action="$1"
  local extra="${2:-}"
  EXTRA_JSON="$extra" python3 -c "
import json, os, sys, urllib.request
action = sys.argv[1]
raw = os.environ.get('EXTRA_JSON', '')
extra = json.loads(raw) if raw else {}
body = {'action': action, 'standalone': True, **extra}
req = urllib.request.Request(
    '${BASE}/api/mac-health',
    data=json.dumps(body).encode(),
    headers={'Content-Type': 'application/json'},
    method='POST',
)
with urllib.request.urlopen(req, timeout=120) as resp:
    print(resp.read().decode())
" "$action" 2>/dev/null || echo '{"ok":false}'
}

check_action() {
  local name="$1"
  local action="$2"
  local extra="${3:-}"
  local body ok
  if [[ -n "$extra" ]]; then
    body=$(post "$action" "$extra")
  else
    body=$(post "$action")
  fi
  ok=$(python3 -c "
import json,sys
d=json.load(sys.stdin)
act='${action}'
ok = d.get('ok') is not False
if act in ('heal','scan','report','settings','settings_save','pipeline'):
    ok = ok and d.get('ok') is True
elif act.startswith('cpu_'):
    ok = ok or bool(d.get('cpu_relief'))
print('yes' if ok else 'no')
" <<<"$body")
  if [[ "$ok" == "yes" ]]; then
    echo "PASS: action $name ($action)"
  else
    echo "FAIL: action $name ($action)"
    fail=1
  fi
}

curl -sf "${BASE}/health" >/dev/null || { echo "FAIL: heart down — run serve-mac-health-guard.sh"; exit 1; }
pass node --check "$ROOT/scripts/mac-health-standalone/app.js"

echo "=== UI element wiring (grep SSOT) ==="
for pair in \
  "btn-heal:heal:load" \
  "btn-rescan:scan:load" \
  "btn-pipeline:pipeline:load" \
  "btn-panic-header:runPanicStop:" \
  "btn-full-stop:runFullStop:" \
  "btn-cool-down:cpu_cool_down:runCpuRelief" \
  "btn-settings-save:saveSettings:" \
  "btn-ram-purge:runRamPurge:"; do
  IFS=: read -r id action fn <<<"$pair"
  ok=1
  grep -q "$id" "$ROOT/scripts/mac-health-standalone/index.html" || ok=0
  if [[ -n "$fn" ]]; then
    grep -q "$fn" "$ROOT/scripts/mac-health-standalone/app.js" || ok=0
  fi
  if [[ "$ok" -eq 1 ]]; then echo "PASS: UI $id wired"; else echo "FAIL: UI $id"; fail=1; fi
done
for action in cpu_clear_pipeline cpu_clear_ghosts cpu_kill_scripts cpu_quit_chrome cpu_pause_n8n cpu_restart_cursor; do
  if grep -q "data-action=\"${action}\"" "$ROOT/scripts/mac-health-standalone/index.html" && grep -q "runCpuRelief" "$ROOT/scripts/mac-health-standalone/app.js"; then
    echo "PASS: Cool Down $action wired"
  else
    echo "FAIL: Cool Down $action"
    fail=1
  fi
done

echo ""
echo "=== Live API actions ==="
check_action "report" "report"
check_action "scan" "scan"
check_action "heal" "heal"
check_action "pipeline" "pipeline"
check_action "settings" "settings"
check_action "settings_save" "settings_save" '{"settings":{"chrome":{"quit_on_cool_down_mode":"when_mac_hot"}}}'
check_action "cool_down" "cpu_cool_down"
check_action "clear_pipeline" "cpu_clear_pipeline"
check_action "clear_ghosts" "cpu_clear_ghosts"
check_action "kill_scripts" "cpu_kill_scripts"
check_action "pause_n8n" "cpu_pause_n8n"

curl -sf "${BASE}/api/mac-health/live" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
assert d.get('live_status')=='LIVE', d.get('live_status')
p=d.get('prevention') or {}
assert 'health' in p, p
assert 'queue_zombies' in p, p
print('PASS: live pulse + prevention queue_zombies=', p.get('queue_zombies'))
" || fail=1

grep -q 'auto_sweep_queue_zombies' "$ROOT/scripts/mac_health_prevention_v1.py" && echo "PASS: auto_sweep_queue_zombies wired" || { echo "FAIL: auto_sweep missing"; fail=1; }
grep -q 'QUEUE_ZOMBIE_PATTERNS' "$ROOT/scripts/mac_health_guard.py" && echo "PASS: multi-pattern zombie detect" || { echo "FAIL: QUEUE_ZOMBIE_PATTERNS missing"; fail=1; }

python3 -c "
import json
from pathlib import Path
p=Path.home()/'.sina/mac-health/live-pulse-v1.json'
assert p.is_file(), 'live-pulse-v1.json missing — heart pulse thread not running'
d=json.loads(p.read_text())
from datetime import datetime, timezone
at=d.get('at','')
dt=datetime.fromisoformat(at.replace('Z','+00:00'))
age=(datetime.now(timezone.utc)-dt).total_seconds()
assert age < 30, f'pulse stale {age:.0f}s — restart heart'
print(f'PASS: background pulse fresh ({age:.0f}s ago)')
" || fail=1

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-all-actions-v1: ALL PASS"
  exit 0
fi
echo "validate-mac-health-all-actions-v1: FAILED"
exit 1
