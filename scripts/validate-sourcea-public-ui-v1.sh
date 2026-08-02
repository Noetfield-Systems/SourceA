#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SOURCEA_E2E_BASE:-https://sourcea.app}"
E2E_DIR="${TMPDIR:-/tmp}/sourcea-public-ui-e2e-$$"

echo "=== validate-sourcea-public-ui-v1 ==="
echo "BASE=$BASE"

if ! curl -sf "${BASE}/" >/dev/null 2>&1; then
  echo "FAIL: landing not reachable at ${BASE}"
  exit 1
fi

mkdir -p "$E2E_DIR"
trap 'rm -rf "$E2E_DIR"' EXIT
cd "$E2E_DIR"
npm init -y >/dev/null 2>&1
npm install playwright@1.61.0 --silent
npx playwright install chromium >/dev/null 2>&1 || true
cp "$ROOT/scripts/validate-sourcea-public-ui-v1.mjs" .
SOURCEA_E2E_BASE="$BASE" node validate-sourcea-public-ui-v1.mjs
echo "validate-sourcea-public-ui-v1.sh: ALL PASS"
