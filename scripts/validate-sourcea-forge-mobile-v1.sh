#!/usr/bin/env bash
# Forge page mobile E2E — Brain header readable + execution-first copy (live/local).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SOURCEA_E2E_BASE:-https://sourcea.app}"
E2E_DIR="${TMPDIR:-/tmp}/sourcea-forge-mobile-e2e-$$"

echo "=== validate-sourcea-forge-mobile-v1 ==="
echo "BASE=$BASE"

if ! curl -sf "${BASE}/sourcea/forge/" >/dev/null 2>&1; then
  echo "FAIL: Forge page not reachable at ${BASE}/sourcea/forge/"
  exit 1
fi

mkdir -p "$E2E_DIR"
trap 'rm -rf "$E2E_DIR"' EXIT
cd "$E2E_DIR"
npm init -y >/dev/null 2>&1
npm install playwright@1.61.0 --silent
npx playwright install chromium >/dev/null 2>&1 || true
cp "$ROOT/scripts/validate-sourcea-forge-mobile-v1.mjs" .
SOURCEA_E2E_BASE="$BASE" node validate-sourcea-forge-mobile-v1.mjs
echo "validate-sourcea-forge-mobile-v1.sh: ALL PASS"
