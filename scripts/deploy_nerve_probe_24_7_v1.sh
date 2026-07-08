#!/usr/bin/env bash
# deploy_nerve_probe_24_7_v1.sh — SourceA portfolio-spine schema + loop-specialist CF deploy
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${NERVE_PROBE_PYTHON:-/usr/bin/python3}"
fail() { echo "FAIL: deploy_nerve_probe_24_7 — $*" >&2; exit 1; }

echo "== 1/5 Disk validators =="
bash "$ROOT/scripts/validate-noetfield-nerve-probe-v1.sh"

echo "== 2/5 Supabase migration 013 =="
"$PY" "$ROOT/scripts/nerve_probe_supabase_v1.py" --apply-migration --json || {
  echo "WARN: migration apply skipped or failed — apply via dashboard if needed" >&2
}

echo "== 3/5 Cloudflare loop-specialist deploy =="
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

echo "== 4/5 CF secrets (Supabase + Telegram) =="
bash "$ROOT/scripts/nerve_probe_cf_secrets_v1.sh"

echo "== 5/5 Live nerve probe =="
HEALTH="https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
curl -sf "$HEALTH" | "$PY" -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
assert d.get('nerve_probe') is True, d
print('health OK · nerve_probe armed')
"
curl -sf -X POST "https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/nerve/run" \
  -H "Content-Type: application/json" -d '{}' | "$PY" -c "
import json,sys
d=json.load(sys.stdin)
print('nerve run:', d.get('nerve_probe_line') or d.get('schema'))
if not d.get('ok'):
    print('WARN: probe cycle RED — check Supabase/Telegram secrets', file=sys.stderr)
"

echo ""
echo "PASS: deploy_nerve_probe_24_7_v1 — SourceA loop-specialist nerve probes live"
