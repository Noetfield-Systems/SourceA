#!/usr/bin/env bash
# deploy_cf_cron_dispatch_v1.sh — sync dispatch table + deploy loop-specialist CF worker
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WF="$ROOT/cloud/workers/loop-specialist-tick-v1"
SSOT="$ROOT/data/loop-specialist-cron-dispatch-v1.json"
BUNDLE="$WF/src/dispatch-table.json"

[[ -f "$SSOT" ]] || { echo "FAIL: missing $SSOT" >&2; exit 1; }
cp "$SSOT" "$BUNDLE"

bash "$ROOT/scripts/validate-cf-cron-dispatch-v1.sh"

cd "$WF"
export CLOUDFLARE_API_TOKEN="${CF_MAIN_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"
if [[ -z "${CLOUDFLARE_API_TOKEN:-}" ]]; then
  echo "WARN: CF_MAIN_TOKEN / CLOUDFLARE_API_TOKEN not set — wrangler may use OAuth"
fi
npx wrangler deploy

HEALTH="https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
echo "== health =="
curl -sf "$HEALTH" | python3 -m json.tool

echo "PASS: deploy_cf_cron_dispatch_v1"
