#!/usr/bin/env bash
# deploy_signal_factory_24_7_v1.sh — Railway body + CF cron + secrets + live verify
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${SIGNAL_FACTORY_PYTHON:-/usr/bin/python3}"
fail() { echo "FAIL: deploy_signal_factory_24_7_v1 — $*" >&2; exit 1; }

echo "== 1/6 E2E validators =="
bash "$ROOT/scripts/validate-signal-factory-e2e-v1.sh"

echo "== 2/6 Railway deploy (FBE body includes signal_factory) =="
cd "$ROOT"
"$PY" scripts/deploy_fbe_railway_v1.py --json | tee /tmp/sf-railway-deploy.json
"$PY" -c "
import json, sys
row = json.loads(open('/tmp/sf-railway-deploy.json').read())
if not row.get('ok'):
    print('railway deploy failed:', row.get('error'), file=sys.stderr)
    sys.exit(1)
print('railway ok:', row.get('worker_url'))
"

echo "== 3/6 Cloudflare worker deploy =="
WF="$ROOT/cloud/workers/signal-factory-tick-v1"
[[ -f "$WF/wrangler.toml" ]] || fail "missing wrangler.toml"
cd "$WF"
unset CF_API_TOKEN CLOUDFLARE_API_TOKEN 2>/dev/null || true
if [[ -f "${HOME}/.sourcea-secrets/cloudflare-tokens.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${HOME}/.sourcea-secrets/cloudflare-tokens.env"
  set +a
fi
npx wrangler deploy

echo "== 4/6 CF secrets =="
bash "$ROOT/scripts/signal_factory_cf_secrets_v1.sh"

echo "== 5/6 Live Railway tick probe =="
set -a
# shellcheck disable=SC1090
source "${HOME}/.sina/secrets.env"
set +a
TARGET="${FBE_CLOUD_WORKER_URL%/}/api/fbe/signal-factory/tick/v1"
HTTP_CODE=$(curl -sf -o /tmp/sf-live-tick.json -w "%{http_code}" \
  -X POST "$TARGET" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ${FBE_INTERNAL_SECRET}" \
  -d '{"max_batch":2,"trigger_source":"deploy_verify"}' ) || true
if [[ "$HTTP_CODE" != "200" ]]; then
  echo "FAIL: live railway tick HTTP $HTTP_CODE" >&2
  cat /tmp/sf-live-tick.json 2>/dev/null || true
  exit 1
fi
"$PY" -c "
import json
row = json.loads(open('/tmp/sf-live-tick.json').read())
assert row.get('ok'), row
assert row.get('schema') == 'signal-factory-tick-receipt-v1', row
assert int(row.get('processed') or 0) >= 1, row
print('live railway tick OK:', row.get('signal_factory_line'))
"

echo "== 6/6 CF worker health + manual tick =="
CF_HEALTH="https://sourcea-signal-factory-tick-v1.witness-bc.workers.dev/health"
curl -sf "$CF_HEALTH" | "$PY" -c "import json,sys; d=json.load(sys.stdin); assert d.get('ok'); print('cf health OK')"
curl -sf -X POST "https://sourcea-signal-factory-tick-v1.witness-bc.workers.dev/tick" \
  -H "Content-Type: application/json" -d '{}' | "$PY" -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
print('cf tick proxy OK:', d.get('signal_factory_line') or d.get('decision'))
"

echo ""
echo "PASS: deploy_signal_factory_24_7_v1 — Railway + CF cron live · synthetic queue motor armed"
