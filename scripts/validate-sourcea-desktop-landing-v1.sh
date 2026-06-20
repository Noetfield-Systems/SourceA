#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 scripts/deploy_sourcea_desktop_landing_v1.py

for f in "$HOME/Desktop/SA4/sourcea/index.html" "$HOME/Desktop/agentrun-app/sourcea/index.html"; do
  test -f "$f" || { echo "FAIL: missing $f"; exit 1; }
  grep -q "hello@sourcea.com" "$f" || { echo "FAIL: no hello@ in $f"; exit 1; }
  grep -q "SourceA" "$f" || { echo "FAIL: no SourceA in $f"; exit 1; }
  grep -qi "noetfield.com\|operations@noetfield\|Copilot governance" "$f" && { echo "FAIL: Noetfield leak in $f"; exit 1; }
  echo "PASS: $f"
done

AR_INDEX="$HOME/Desktop/agentrun-app/sourcea/index.html"
grep -q 'sa-buyer-toggle' "$AR_INDEX" || { echo "FAIL: no sa-buyer-toggle in $AR_INDEX"; exit 1; }
grep -q 'sa-chain-beats' "$AR_INDEX" || { echo "FAIL: no sa-chain-beats in $AR_INDEX"; exit 1; }
grep -q 'id="sa-agent-pill-text"' "$AR_INDEX" || { echo "FAIL: no sa-agent-pill-text in $AR_INDEX"; exit 1; }
grep -q 'sa-mock-panel' "$AR_INDEX" || { echo "FAIL: no sa-mock-panel in $AR_INDEX"; exit 1; }
echo "PASS: agentrun index mock selectors"

SUBPAGES=(platform.html team.html growth.html scenario.html proof.html proof/live.html compare.html pricing.html security.html status.html sources.html loops/index.html loops/outreach.html loops/ops-monitor.html loops/research.html loops/eval-booking.html loops/session-gate.html loops/proof-export.html)
for p in "${SUBPAGES[@]}"; do
  f="$HOME/Desktop/agentrun-app/sourcea/$p"
  test -f "$f" || { echo "FAIL: missing subpage $f"; exit 1; }
  grep -q "hello@sourcea.com" "$f" || { echo "FAIL: no hello@ in $f"; exit 1; }
  grep -q "ar-nav-toggle" "$f" || { echo "FAIL: no mobile nav in $f"; exit 1; }
  grep -q 'href="/sourcea/team.html" data-sa-nav' "$f" || { echo "FAIL: no Team nav in $f"; exit 1; }
  grep -q "Book proof demo" "$f" || { echo "FAIL: no unified CTA in $f"; exit 1; }
  grep -q "Get Started" "$f" && { echo "FAIL: legacy Get Started in $f"; exit 1; }
  if [[ "$p" == "platform.html" || "$p" == "proof.html" || "$p" == "proof/live.html" || "$p" == "security.html" || "$p" == "status.html" ]]; then
    grep -q 'data-sa-trust-bar' "$f" || { echo "FAIL: no trust bar in $f"; exit 1; }
  fi
  if [[ "$p" == "proof.html" ]]; then
    grep -q 'sa-chain-beats' "$f" || { echo "FAIL: no sa-chain-beats in $f"; exit 1; }
  fi
  echo "PASS: $f"
done

echo "validate-sourcea-desktop-landing-v1.sh: ALL PASS"
echo "Tip: full E2E (responsive + Playwright) → bash scripts/validate-sourcea-landing-e2e-v1.sh"
