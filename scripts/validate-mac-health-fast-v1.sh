#!/usr/bin/env bash
# validate-mac-health-fast-v1.sh — ~15s daily dev gate (founder-glance v3.3)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
PORT="${MAC_HEALTH_PORT:-13024}"
BASE="http://127.0.0.1:${PORT}"
fail=0

_run() {
  local name="$1"
  shift
  if "$@"; then
    echo "OK: $name"
  else
    echo "FAIL: $name"
    fail=1
  fi
}

curl -sf "${BASE}/health" >/dev/null || bash "$ROOT/scripts/serve-mac-health-guard.sh" >/dev/null

curl -sf "${BASE}/health" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
assert str(d.get('version','')).startswith('3.3'), d
ui=d.get('ui_contract') or {}
assert ui.get('ui_mode')=='founder_glance', ui
assert ui.get('tab_count')==0, ui
print(f'heart v{d.get(\"version\")} founder_glance')
" || { echo "FAIL: health"; exit 1; }

VER=$(python3 -c "from mac_health_version_v1 import CSS_CACHE_BUSTER; print(CSS_CACHE_BUSTER)")
html=$(curl -sf "${BASE}/")
for n in "app.css?v=${VER}" "mhg-founder-glance" "Relieve pressure" "panel-more" "btn-cool-down"; do
  grep -q "$n" <<<"$html" || { echo "FAIL: HTML missing $n"; fail=1; }
done
for bad in "mhg-seg-nav" "founder-poem" "Brain heal"; do
  grep -q "$bad" <<<"$html" && { echo "FAIL: HTML has old $bad"; fail=1; }
done
[[ $fail -eq 0 ]] && echo "PASS: HTML founder-glance"

curl -sf -X POST "${BASE}/api/mac-health" \
  -H "Content-Type: application/json" \
  -d '{"action":"settings","standalone":true}' | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
assert d.get('values',{}).get('chrome'), d
print('PASS: settings API')
" || fail=1

_run "UI theme grep" bash "$ROOT/scripts/validate-mac-health-ui-v1.sh"

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-fast-v1: PASS"
  exit 0
fi
echo "validate-mac-health-fast-v1: FAIL"
exit 1
