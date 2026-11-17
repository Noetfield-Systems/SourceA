#!/usr/bin/env bash
# Historical mirror synchronization is no longer an authorized Witness publication path.
# The public Web3 site is built from SourceA/witnessbc-site directly in Vercel.
set -euo pipefail
echo "REVOKED: historical Witness static mirror sync must not ship the prior institutional/Stripe site." >&2
echo "Use SourceA canonical Web3 build + Vercel project dpl/prj deployment and public proof." >&2
exit 3
