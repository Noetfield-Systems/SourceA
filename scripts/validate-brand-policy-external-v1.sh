#!/usr/bin/env bash
# Fail if forbidden third-party brand tokens appear in customer-facing trees.
# Deny patterns live outside the repo (SOURCEA_BRAND_DENYLIST_PATH or ~/.sina/).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

FORBIDDEN_PATHS=(
  "data/root-machine/C12"
  "data/root-machine/C13"
  "sites/SourceA-landing/green-unified/reference/sourcea-landing-mock-v1.html"
  "archive/internal-research/portfolio-fast-sell-archived-research"
)

fail=0
for p in "${FORBIDDEN_PATHS[@]}"; do
  if [[ -e "$p" ]]; then
    echo "FAIL: forbidden path present: $p" >&2
    fail=1
  fi
done

if ! python3 "$ROOT/witnessbc-site/scripts/check_brand_forbidden_v1.py" \
  sites/SourceA-landing/green-unified \
  sites/SourceA-landing/green-unified/dist/sourcea \
  witnessbc-site/index.html 2>/dev/null; then
  fail=1
fi

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "OK: validate-brand-policy-external-v1"
