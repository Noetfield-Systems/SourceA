#!/usr/bin/env bash
# Full WitnessBC activate: stripe inject · rebuild · CF Pages deploy · DNS checklist
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$(dirname "$ROOT")"

echo "=== activate_witnessbc_full_v1 ==="
python3 witnessbc-site/scripts/inject_stripe_links_v1.py
bash witnessbc-site/scripts/run-recipe.sh
bash witnessbc-site/scripts/deploy_witnessbc_cf_v1.sh
bash witnessbc-site/scripts/dns_cutover_witnessbc_v1.sh

echo ""
echo "VERIFY pages.dev:"
curl -sL https://witnessbc-commercial.pages.dev/ | rg -q 'brand-disambiguation' && echo "OK home brand-disambiguation" || echo "FAIL home"
curl -sL https://witnessbc-commercial.pages.dev/pricing | rg -q 'stripe-packs-strip|Buy Pro pack' && echo "OK pricing stripe strip" || echo "FAIL pricing stripe"
