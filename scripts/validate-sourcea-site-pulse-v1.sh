#!/usr/bin/env bash
# Site Pulse smoke — public stats + founder dashboard auth gate.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WORKER="${SOURCEA_PULSE_WORKER:-https://sourcea-site-pulse-v1.sina-kazemnezhad-ca.workers.dev}"
BASE="${SOURCEA_E2E_BASE:-https://sourcea.app}"
RECEIPT="${HOME}/.sina/enforcement/sourcea-site-pulse-gate-receipt-v1.json"
mkdir -p "$(dirname "$RECEIPT")"

echo "=== site pulse smoke (${WORKER}) ==="

echo "=== pulse worker discovery ==="
DISC="$(curl -fsS "${WORKER}/api/site/pulse/v1")"
echo "$DISC" | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('ok'), row
eps = row.get('endpoints') or {}
for k in ('stats', 'dashboard', 'feedback', 'event'):
    assert eps.get(k), f'missing endpoint {k}'
print('OK endpoints', list(eps.keys()))
"

echo "=== public stats GET ==="
STATS="$(curl -fsS "${WORKER}/api/site/stats/v1")"
echo "$STATS" | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('ok'), row
assert row.get('schema') == 'sourcea-site-stats-public-v1', row.get('schema')
s = row.get('stats') or {}
assert 'pageviews' in s and 'feedback_count' in s, s
print('OK stats day=', s.get('day'), 'pv=', s.get('pageviews'), 'fb=', s.get('feedback_count'))
"

echo "=== founder dashboard without key (expect 401) ==="
CODE="$(curl -sS -o /tmp/sa-pulse-dash.json -w '%{http_code}' "${WORKER}/api/site/dashboard/v1")"
[[ "$CODE" == "401" ]] || { echo "FAIL dashboard unauth expected 401 got $CODE"; cat /tmp/sa-pulse-dash.json; exit 1; }
echo "OK dashboard 401 without key"

if [[ -n "${SOURCEA_PULSE_FOUNDER_KEY:-}" ]]; then
  echo "=== founder dashboard with key ==="
  curl -fsS "${WORKER}/api/site/dashboard/v1" \
    -H "X-SourceA-Pulse-Key: ${SOURCEA_PULSE_FOUNDER_KEY}" | python3 -c "
import json, sys
row = json.load(sys.stdin)
assert row.get('ok'), row
assert row.get('schema') == 'sourcea-site-dashboard-v1', row.get('schema')
assert 'inbox' in row and 'today' in row, row.keys()
print('OK inbox', len(row.get('inbox') or []), 'items')
"
fi

echo "=== landing assets (warn if not published yet) ==="
for path in \
  "/sourcea/data/sourcea-site-pulse-config-v1.json" \
  "/sourcea/sourcea-pulse-public-v1.js" \
  "/sourcea/sourcea-pulse-founder-v1.js" \
  "/sourcea/pulse-founder"; do
  code="$(curl -sS -o /dev/null -w '%{http_code}' "${BASE}${path}" 2>/dev/null || echo 000)"
  if [[ "$code" == "200" || "$code" == "302" ]]; then
    echo "OK $code ${path}"
  else
    echo "WARN ${BASE}${path} -> $code (run landing publish)"
  fi
done

for f in \
  SourceA-landing/green-unified/pulse-founder.html \
  SourceA-landing/green-unified/sourcea-pulse-public-v1.js \
  SourceA-landing/green-unified/sourcea-pulse-founder-v1.js \
  SourceA-landing/green-unified/data/sourcea-site-pulse-config-v1.json; do
  test -f "$ROOT/$f" || { echo "FAIL: missing disk $f"; exit 1; }
done
echo "OK pulse dashboard files logged"

python3 - <<PY
import json, time
from pathlib import Path
row = {
    "schema": "sourcea-site-pulse-gate-receipt-v1",
    "at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    "ok": True,
    "verdict": "PASS",
    "worker": "${WORKER}",
    "founder_key_tested": bool("${SOURCEA_PULSE_FOUNDER_KEY:-}"),
}
Path("${RECEIPT}").write_text(json.dumps(row, indent=2) + "\\n", encoding="utf-8")
print("OK receipt", "${RECEIPT}")
PY

echo "validate-sourcea-site-pulse-v1.sh: ALL PASS"
