#!/usr/bin/env bash
# validate-mac-health-ship-fast-v1.sh — Mac founder session gate (≤90s · read-only · NO marathon)
# Law: INCIDENT-039/040 · MAC_PIPELINE_VALIDATOR_PRESSURE_LAW — light tier ONLY on Mac body
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_mac_health_validator_common_v1.sh
source "$ROOT/scripts/_mac_health_validator_common_v1.sh"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
PORT="$(_mh_port)"
BASE="$(_mh_base)"
STEPS_FILE="$(mktemp)"
fail=0
started=$(date +%s)

_run() {
  local name="$1"
  shift
  if "$@"; then
    echo "OK: $name"
    python3 -c "import json,sys; print(json.dumps({'name': sys.argv[1], 'ok': True}))" "$name" >>"$STEPS_FILE"
  else
    echo "FAIL: $name"
    python3 -c "import json,sys; print(json.dumps({'name': sys.argv[1], 'ok': False}))" "$name" >>"$STEPS_FILE"
    fail=1
  fi
}

_cleanup() {
  _mh_write_ship_receipt "$fail" "ship-fast" "$STEPS_FILE" || true
  rm -f "$STEPS_FILE"
}
trap '_cleanup' EXIT

echo "=== Mac Health ship-fast (read-only · no marathon) ==="

_mh_ensure_heart || { echo "FAIL: heart not up"; fail=1; exit 1; }

curl -sf "${BASE}/health" | python3 -c "
import json,sys
from mac_health_version_v1 import MAC_HEALTH_VERSION
d=json.load(sys.stdin)
assert d.get('ok'), d
assert str(d.get('version','')) == MAC_HEALTH_VERSION, d
ui=d.get('ui_contract') or {}
assert ui.get('ui_mode')=='founder_glance', ui
assert ui.get('tab_count')==0, ui
cg=ui.get('cloud_glance') or {}
assert 'founder_line' in cg or ui.get('cloud_glance_strip_id')=='cloud-glance-strip', ui
print(f'heart v{d.get(\"version\")} founder_glance · cloud wired')
" || fail=1

_run "cloud glance API" bash "$ROOT/scripts/validate-mac-health-cloud-glance-v1.sh"

curl -sf "${BASE}/api/mac-health/live" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
assert d.get('live_status')=='LIVE', d.get('live_status')
mp=d.get('machine_pressure') or {}
for k in ('ram_used_pct','cpu_pct','ram_truth','hub_health_ok','sina_log_bomb'):
    assert k in mp, f'missing {k}'
rt=mp.get('ram_truth') or {}
assert rt.get('explain_line') or rt.get('total_line'), 'ram_truth line'
print('PASS: live pulse read-only schema')
" || fail=1

_run "founder glance SSOT" bash "$ROOT/scripts/validate-mac-health-founder-glance-v1.sh"
_run "UI theme grep" bash "$ROOT/scripts/validate-mac-health-ui-v1.sh"

VER=$(python3 -c "from mac_health_version_v1 import CSS_CACHE_BUSTER; print(CSS_CACHE_BUSTER)")
html=$(curl -sf "${BASE}/")
for n in "app.css?v=${VER}" "Relieve pressure" "cloud-glance-strip" "panel-more"; do
  grep -q "$n" <<<"$html" || { echo "FAIL: served HTML missing $n"; fail=1; }
done
[[ $fail -eq 0 ]] && echo "PASS: served HTML v${VER}"

curl -sf -X POST "${BASE}/api/mac-health" \
  -H "Content-Type: application/json" \
  -d '{"action":"settings","standalone":true}' | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
print('PASS: settings read (no relief invoke)')
" || fail=1

elapsed=$(( $(date +%s) - started ))
if [[ "$elapsed" -gt 90 ]]; then
  echo "WARN: ship-fast took ${elapsed}s (>90s budget)"
fi

echo ""
if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-ship-fast-v1: ALL PASS (${elapsed}s)"
  exit 0
fi
echo "validate-mac-health-ship-fast-v1: FAILED (${elapsed}s)"
exit 1
