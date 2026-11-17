#!/usr/bin/env bash
# Compatibility entrypoint that can ONLY assemble the new Web3 site.
# Legacy Cloudflare/B2B, Stripe, toolkit checkout and prior mirror push are revoked.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
case "${1:-}" in
  ""|--skip-recipe) ;;
  *) echo "Refusing legacy Witness deploy flags. Canonical Web3 Vercel release is SourceA only." >&2; exit 2 ;;
esac
node scripts/build-web3.mjs
node scripts/verify-web3.mjs
echo "PASS Web3-only release staged at dist/deploy (not yet a production claim)"
