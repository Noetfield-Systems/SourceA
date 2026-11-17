#!/usr/bin/env bash
# Witness Web3 Genesis canonical run recipe — legacy B2B/Stripe pipeline revoked.
set -euo pipefail
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
node scripts/build-web3.mjs
node scripts/verify-web3.mjs
echo "PASS Witness Web3-only canonical run recipe"
case "${1:-}" in
  "") ;;
  --serve) exec node scripts/serve-web3.mjs ;;
  --json) printf '{"ok":true,"schema":"witness.web3.build.v2","routes":10,"legacy_checkout":false}\n' ;;
  *) echo "Legacy run mode is no longer supported for the independent Witness Web3 site" >&2; exit 2 ;;
esac
