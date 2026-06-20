#!/usr/bin/env bash
# One-shot deploy to founder Cloudflare Pages (witness.bc@gmail.com account).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT="${WRANGLER_PAGES_PROJECT:-witnessbc-commercial}"
cd "$ROOT/.."
bash witnessbc-site/scripts/deploy_witnessbc_v1.sh --skip-recipe
wrangler pages deploy witnessbc-site/dist/deploy \
  --project-name="$PROJECT" \
  --commit-dirty=true \
  --commit-message="witnessbc v12 $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""
echo "LIVE PREVIEW: https://${PROJECT}.pages.dev"
echo "CUSTOM DOMAIN: run bash witnessbc-site/scripts/dns_cutover_witnessbc_v1.sh if www still on Vercel"
