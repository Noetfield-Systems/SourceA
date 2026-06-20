#!/usr/bin/env bash
# validate-mac-health-ui-v1.sh — Founder-glance UI gate (v4.0+)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
PORT="${MAC_HEALTH_PORT:-13024}"
BASE="http://127.0.0.1:${PORT}"
VER="$(python3 -c "from mac_health_version_v1 import CSS_CACHE_BUSTER; print(CSS_CACHE_BUSTER)")"
fail=0

html=$(curl -sf "${BASE}/" 2>/dev/null || true)

for needle in "app.css?v=${VER}" "app.js?v=${VER}" "mhg-founder-glance" "mhg-founder-card" "Relieve pressure" "id=\"panel-more\"" "id=\"cloud-glance-strip\"" "playwright-banner" "log-shield" "hub-truth-badge"; do
  if grep -q "$needle" <<<"$html"; then
    echo "PASS: HTML has $needle"
  else
    echo "FAIL: HTML missing $needle"
    fail=1
  fi
done

for bad in "mhg-seg-nav" "founder-poem" "tab-settings-btn" "tab-cooldown-btn" "Brain heal"; do
  if grep -q "$bad" <<<"$html"; then
    echo "FAIL: HTML has old $bad"
    fail=1
  else
    echo "PASS: HTML no $bad"
  fi
done

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-ui-v1: PASS"
  exit 0
fi
echo "validate-mac-health-ui-v1: FAIL"
exit 1
