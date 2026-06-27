#!/usr/bin/env bash
# Brain landing E2E — API smoke + Playwright widget reply on live/local.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${SOURCEA_E2E_BASE:-https://sourcea.app}"
E2E_DIR="${TMPDIR:-/tmp}/sourcea-brain-landing-e2e-$$"

echo "=== validate-sourcea-brain-landing-e2e-v1 ==="
bash "$ROOT/scripts/validate-sourcea-brain-chat-v1.sh"
bash "$ROOT/scripts/validate-forge-terminal-public-demo-v1.sh"

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
cp "$ROOT/scripts/validate-sourcea-brain-landing-e2e-v1.mjs" .
SOURCEA_E2E_BASE="$BASE" node validate-sourcea-brain-landing-e2e-v1.mjs
bash "$ROOT/scripts/validate-sourcea-modern-stack-e2e-v1.sh"
echo "validate-sourcea-brain-landing-e2e-v1.sh: ALL PASS"
