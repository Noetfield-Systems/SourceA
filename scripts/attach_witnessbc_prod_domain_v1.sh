#!/usr/bin/env bash
# Attach www.witnessbc.com to main Vercel deploy-witnessbc-agentic-governance.
# Fixes old journalism page (wrong Vercel project still owns the domain).
#
# Auth: ~/.sina/sourcea-vercel-token-v1.json OR Terminal OAuth on the-777-foundation
# Law: data/vercel-portfolio-map-v1.json
set -euo pipefail

SCOPE="${WITNESSBC_VERCEL_SCOPE:-the-777-foundation}"
PROJECT="${WITNESSBC_VERCEL_PROJECT:-deploy-witnessbc-agentic-governance}"
DOMAIN="${WITNESSBC_PROD_DOMAIN:-www.witnessbc.com}"
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
TOKEN_FILE="${HOME}/.sina/sourcea-vercel-token-v1.json"

NPX="/usr/local/bin/npx"
if [[ ! -x "${NPX}" ]]; then NPX="$(command -v npx || echo npx)"; fi
VC=("${NPX}" --yes vercel@latest)

if [[ -f "${TOKEN_FILE}" ]]; then
  TOK="$(python3 -c "import json; print(json.load(open('${TOKEN_FILE}'))['token'])")"
  VC+=(--token="${TOK}")
fi

echo "=== Attach ${DOMAIN} → ${PROJECT} (${SCOPE}) ==="
"${VC[@]}" domains add "${DOMAIN}" --scope="${SCOPE}" --project="${PROJECT}" 2>&1 || true
echo ""
echo "Verify:"
curl -sL "https://${DOMAIN}/" | rg -o '<title>[^<]+' | head -1 || true
echo ""
echo "Expected title contains: Witness AI | Agentic Governance"
echo "If still journalism → remove ${DOMAIN} from OLD Vercel project on dashboard first."
