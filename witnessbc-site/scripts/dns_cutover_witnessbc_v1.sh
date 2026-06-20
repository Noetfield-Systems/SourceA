#!/usr/bin/env bash
# Point witnessbc.com DNS from Vercel → Cloudflare Pages (witnessbc-commercial).
# Run AFTER: wrangler pages deploy.
# Usage:
#   bash witnessbc-site/scripts/dns_cutover_witnessbc_v1.sh          # checklist
#   bash witnessbc-site/scripts/dns_cutover_witnessbc_v1.sh --apply  # API cutover
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APPLY=0
[[ "${1:-}" == "--apply" ]] && APPLY=1

if [[ "$APPLY" -eq 1 ]]; then
  echo "=== witnessbc DNS cutover API (--apply) ==="
  python3 "$ROOT/scripts/dns_cutover_witnessbc_api_v1.py" --apply --json
  echo ""
  echo "Waiting 30s for DNS propagation..."
  sleep 30
  curl -sSI "https://www.witnessbc.com/" | grep -i server || true
  curl -sL "https://www.witnessbc.com/" | grep -q 'brand-disambiguation' && echo "OK: commercial home live" || echo "WARN: commercial markers not yet visible"
  exit 0
fi

echo "=== witnessbc DNS cutover checklist ==="
echo ""
echo "COMMERCIAL SITE IS LIVE ON:"
echo "  https://witnessbc-commercial.pages.dev"
echo ""
echo "CUSTOM DOMAINS ATTACHED (initializing):"
echo "  www.witnessbc.com"
echo "  witnessbc.com"
echo ""
echo "PROBLEM: DNS still points to VERCEL (journalism site)."
echo "  curl -sSI https://www.witnessbc.com/ | grep server"
echo "  → server: Vercel"
echo ""
echo "FIX — Cloudflare dashboard (witness.bc@gmail.com):"
echo "  1. DNS → witnessbc.com zone"
echo "  2. Find www CNAME → likely cname.vercel-dns.com — DELETE or EDIT"
echo "  3. Set www CNAME → witnessbc-commercial.pages.dev (Proxied orange cloud)"
echo "  4. Apex @ — set CNAME flatten to witnessbc-commercial.pages.dev"
echo "     OR use Pages dashboard: Workers & Pages → witnessbc-commercial → Custom domains"
echo "     → click domain → follow 'Activate domain' DNS instructions"
echo "  5. Wait 2–5 min · verify:"
echo ""
echo "     curl -sL https://www.witnessbc.com/ | grep brand-disambiguation"
echo "     curl -sL https://www.witnessbc.com/ | grep proof@witnessbc.com"
echo "     curl -sL https://www.witnessbc.com/proof.html | grep 'Proof Lab'"
echo ""
echo "PAGES PROJECT: witnessbc-commercial"
echo "ACCOUNT: Witness.bc@gmail.com (2c70de9e879a9b41055642ad47205d71)"
echo "DEPLOY: bash witnessbc-site/scripts/deploy_witnessbc_v1.sh --skip-recipe && wrangler pages deploy witnessbc-site/dist/deploy --project-name=witnessbc-commercial --commit-dirty=true"
