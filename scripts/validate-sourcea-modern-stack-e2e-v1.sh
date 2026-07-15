#!/usr/bin/env bash
# Modern stack E2E — pulse · interact · Cal overlay · feedback · commercial paths.
# Default live: https://sourcea.app · Mac-light (single Playwright pass).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SOURCEA_E2E_BASE:-https://sourcea.app}"
E2E_DIR="${TMPDIR:-/tmp}/sourcea-modern-stack-e2e-$$"

echo "=== validate-sourcea-modern-stack-e2e-v1 ==="
if ! curl -sf "${BASE}/" >/dev/null 2>&1; then
  echo "FAIL: not reachable at ${BASE}"
  exit 1
fi
echo "OK: base ${BASE}"

# Config + assets logged (repo)
for f in \
  SourceA-landing/green-unified/sourcea-site-pulse-v1.js \
  SourceA-landing/green-unified/sourcea-site-interact-v1.js \
  SourceA-landing/green-unified/data/sourcea-site-interact-v1.json \
  SourceA-landing/green-unified/data/sourcea-site-pulse-config-v1.json; do
  test -f "$ROOT/$f" || { echo "FAIL: missing $f"; exit 1; }
done
echo "OK: modern stack files logged"

mkdir -p "$E2E_DIR"
trap 'rm -rf "$E2E_DIR"' EXIT
cd "$E2E_DIR"
npm init -y >/dev/null 2>&1
npm install playwright@1.61.0 --silent
npx playwright install chromium >/dev/null 2>&1 || true
cp "$ROOT/scripts/sourcea-modern-stack-e2e-v1.mjs" .
SOURCEA_E2E_BASE="$BASE" node sourcea-modern-stack-e2e-v1.mjs
echo "validate-sourcea-modern-stack-e2e-v1.sh: ALL PASS"
