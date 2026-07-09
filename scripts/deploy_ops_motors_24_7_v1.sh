#!/usr/bin/env bash
# deploy_ops_motors_24_7_v1.sh — ops motors CF crons + Railway smoke
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${OPS_MOTORS_PYTHON:-/usr/bin/python3}"
fail() { echo "FAIL: deploy_ops_motors_24_7 — $*" >&2; exit 1; }

echo "== 1/4 Disk validators =="
bash "$ROOT/scripts/validate-ops-motors-v1.sh"
bash "$ROOT/scripts/validate-ops-motors-e2e-v1.sh"

echo "== 2/4 Cloudflare loop-specialist deploy =="
WF="$ROOT/cloud/workers/loop-specialist-tick-v1"
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

echo "== 3/4 CF /health ops_motors =="
HEALTH="https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
curl -sf "$HEALTH" | "$PY" -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
ops=d.get('ops_motors')
assert ops, 'ops_motors missing from health'
crons=d.get('crons') or []
want=['*/15 * * * *','0 * * * *','0 7 * * *','0 3 * * *']
for c in want:
    assert c in crons, f'missing cron {c} in {crons}'
print('health OK · ops_motors=', ops)
"

echo "== 4/4 Railway FBE ops routes (optional) =="
if [[ -n "${FBE_URL:-}" && -n "${FBE_INTERNAL_SECRET:-}" ]]; then
  for path in gmail-sweep signal-factory/triage kaizen/nightly ops/heartbeat; do
    code="$(curl -sS -o /tmp/ops-motor-smoke.json -w '%{http_code}' \
      -X POST "${FBE_URL}/api/fbe/${path}/v1" \
      -H "Authorization: Bearer ${FBE_INTERNAL_SECRET}" \
      -H "Content-Type: application/json" \
      -d '{}' || true)"
    [[ "$code" == "200" || "$code" == "401" ]] || fail "FBE ${path} http ${code}"
    echo "FBE /api/fbe/${path}/v1 → ${code}"
  done
else
  echo "SKIP: FBE_URL/FBE_INTERNAL_SECRET unset — deploy via deploy_fbe_railway_v1.py"
fi

echo ""
echo "PASS: deploy_ops_motors_24_7_v1 — loop-specialist ops crons live"
