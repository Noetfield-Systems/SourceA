#!/usr/bin/env bash
# Arm signal-factory-tick-v1 for 24/7 synthetic queue motor (founder-run once).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WF="$ROOT/cloud/workers/signal-factory-tick-v1"
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

echo ""
echo "OK — signal-factory 24/7 armed. Test:"
echo "  curl -s https://sourcea-signal-factory-tick-v1.witness-bc.workers.dev/health"
echo "  curl -s -X POST https://sourcea-signal-factory-tick-v1.witness-bc.workers.dev/tick -H 'Content-Type: application/json' -d '{}'"
