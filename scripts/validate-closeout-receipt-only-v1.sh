#!/usr/bin/env bash
# Gate: closeout scripts must read receipts — never subprocess full validators (INCIDENT-026).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CLOSEOUT="$ROOT/scripts/live-prompt-worker-closeout-v1.py"

if [[ ! -f "$CLOSEOUT" ]]; then
  echo "FAIL: missing $CLOSEOUT"
  exit 1
fi

if grep -qE 'subprocess\.(run|check_output|call)' "$CLOSEOUT"; then
  echo "FAIL: closeout must not subprocess validators — read receipts only"
  exit 1
fi

for bad in \
  live_prompt_lane_audit_v1.py \
  live-prompt-lane-score-v1.py \
  validate-live-prompt-feed-e2e-v1.sh \
  cross-plan-readiness-v1.py
do
  if grep -q "$bad" "$CLOSEOUT" && grep -q subprocess "$CLOSEOUT"; then
    echo "FAIL: closeout references $bad with subprocess"
    exit 1
  fi
done

if ! grep -q 'receipt-based\|_read_json' "$CLOSEOUT"; then
  echo "FAIL: closeout must read JSON receipts"
  exit 1
fi

echo "PASS: validate-closeout-receipt-only-v1"
