#!/usr/bin/env bash
# deploy_cf_all_motors_v1.sh — deploy all 24/7 Cloudflare cron motors (GHA schedules forbidden)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "== CF-only 24/7 law =="
bash "$ROOT/scripts/validate-cf-only-24-7-v1.sh"

echo "== loop-specialist (*/15 dispatch) =="
bash "$ROOT/scripts/deploy_cf_cron_dispatch_v1.sh"

echo "== cloud-auto-runtime (*/10 Cloud Forge Run) =="
WF="$ROOT/cloud/workers/cloud-auto-runtime-tick-v1"
cd "$WF"
unset CF_API_TOKEN CLOUDFLARE_API_TOKEN 2>/dev/null || true
if [[ -f "${HOME}/.sourcea-secrets/cloudflare-tokens.env" ]]; then
  set -a
  # shellcheck disable=SC1091
  source "${HOME}/.sourcea-secrets/cloudflare-tokens.env"
  set +a
fi
export CLOUDFLARE_API_TOKEN="${CF_MAIN_TOKEN:-${CLOUDFLARE_API_TOKEN:-}}"
npx wrangler deploy
HEALTH_AUTO="https://sourcea-cloud-auto-runtime-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
curl -sf "$HEALTH_AUTO" | python3 -m json.tool

echo "== deadman (*/30 loop_registry watcher) =="
cp "$ROOT/data/loop-registry-v1.json" "$ROOT/cloud/workers/sourcea-deadman-v1/src/loop-registry.json"
WF="$ROOT/cloud/workers/sourcea-deadman-v1"
cd "$WF"
npx wrangler deploy
curl -sf "https://sourcea-deadman-v1.sina-kazemnezhad-ca.workers.dev/health" | python3 -m json.tool

echo "PASS: deploy_cf_all_motors_v1 — 24/7 on Cloudflare only"
