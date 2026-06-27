#!/usr/bin/env bash
# Forge Terminal public demo — disk + worker + Playwright on live/local landing.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SOURCEA_E2E_BASE:-https://sourcea.app}"
E2E_DIR="${TMPDIR:-/tmp}/sourcea-forge-terminal-demo-e2e-$$"

echo "=== validate-forge-terminal-public-demo-e2e-v1 ==="
bash "$ROOT/scripts/validate-forge-terminal-public-demo-v1.sh"

if ! curl -sf "${BASE}/sourcea/forge/terminal" >/dev/null 2>&1; then
  echo "FAIL: demo not reachable at ${BASE}/sourcea/forge/terminal"
  exit 1
fi

mkdir -p "$E2E_DIR"
trap 'rm -rf "$E2E_DIR"' EXIT
cd "$E2E_DIR"
npm init -y >/dev/null 2>&1
npm install playwright@1.61.0 --silent
npx playwright install chromium >/dev/null 2>&1 || true
cp "$ROOT/scripts/validate-forge-terminal-public-demo-e2e-v1.mjs" .
SOURCEA_E2E_BASE="$BASE" node validate-forge-terminal-public-demo-e2e-v1.mjs
echo "validate-forge-terminal-public-demo-e2e-v1.sh: ALL PASS"
