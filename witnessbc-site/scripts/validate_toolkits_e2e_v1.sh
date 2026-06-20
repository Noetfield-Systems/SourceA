#!/usr/bin/env bash
# E2E: every toolkits hub + subpage returns 200 and loads v12 CSS from /assets/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BASE="${1:-http://127.0.0.1:8092}"

PATHS=(
  "/toolkits.html"
  "/toolkits/free/sourcing/"
  "/toolkits/free/corrections/"
  "/toolkits/free/privacy/"
  "/toolkits/free/public-record/"
  "/toolkits/free/story-template/"
  "/toolkits/free/action-map/"
  "/toolkits/training/"
  "/toolkits/training/evidence-literacy-101/"
  "/toolkits/training/privacy-first-publishing/"
)

fail=0
for path in "${PATHS[@]}"; do
  url="${BASE%/}${path}"
  code="$(curl -sS -o /tmp/wbc-toolkit-e2e.html -w '%{http_code}' -L "$url" || echo "000")"
  if [[ "$code" != "200" ]]; then
    echo "FAIL: $url → HTTP $code"
    fail=1
    continue
  fi
  if ! grep -q 'layout-ultra-v12' /tmp/wbc-toolkit-e2e.html; then
    echo "FAIL: $url missing layout-ultra-v12"
    fail=1
    continue
  fi
  if ! grep -q 'assets/styles.css' /tmp/wbc-toolkit-e2e.html; then
    echo "FAIL: $url missing assets/styles.css link"
    fail=1
    continue
  fi
  css_code="$(curl -sS -o /dev/null -w '%{http_code}' -L "${BASE%/}/assets/styles.css" || echo "000")"
  if [[ "$css_code" != "200" ]]; then
    echo "FAIL: ${BASE%/}/assets/styles.css → HTTP $css_code"
    fail=1
    continue
  fi
  echo "OK: $path"
done

if [[ "$fail" -ne 0 ]]; then
  exit 1
fi
echo "PASS: toolkits E2E — ${#PATHS[@]} pages · CSS wired"
