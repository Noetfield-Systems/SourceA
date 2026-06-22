#!/usr/bin/env bash
# Arm Cloudflare cloud-drain-tick-v1 for 24/7 auto Proceed (founder-run once).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WF="$ROOT/cloud/workers/cloud-drain-tick-v1"
SECRETS="${HOME}/.sina/secrets.env"

if [[ ! -f "$SECRETS" ]]; then
  echo "FAIL: missing $SECRETS (need FBE_CLOUD_WORKER_URL + FBE_INTERNAL_SECRET)"
  exit 1
fi
set -a
# shellcheck disable=SC1090
source "$SECRETS"
set +a

unset CF_API_TOKEN CLOUDFLARE_API_TOKEN 2>/dev/null || true
cd "$WF"

echo "→ FBE_CLOUD_WORKER_URL"
printf '%s' "${FBE_CLOUD_WORKER_URL}" | npx wrangler secret put FBE_CLOUD_WORKER_URL
echo "→ FBE_INTERNAL_SECRET"
printf '%s' "${FBE_INTERNAL_SECRET}" | npx wrangler secret put FBE_INTERNAL_SECRET
echo "→ CLOUD_DRAIN_AUTO_PROCEED=true"
printf '%s' "true" | npx wrangler secret put CLOUD_DRAIN_AUTO_PROCEED

echo ""
echo "OK — 24/7 armed. Test:"
echo "  curl -s https://sourcea-cloud-drain-tick-v1.witness-bc.workers.dev/health"
echo "  curl -s -X POST https://sourcea-cloud-drain-tick-v1.witness-bc.workers.dev/tick -H 'Content-Type: application/json' -d '{\"proceed\":true}'"
