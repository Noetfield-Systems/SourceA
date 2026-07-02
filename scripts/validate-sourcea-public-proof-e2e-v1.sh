#!/usr/bin/env bash
# Public proof E2E — live Brain, contract SKUs, SDK/boot; no Mac heavy gates or hub required.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
SCRIPTS="$ROOT/scripts"
errors=0

_run() {
  local label="$1"
  shift
  echo "=== $label ==="
  if "$@"; then
    echo "OK: $label"
  else
    echo "FAIL: $label"
    errors=$((errors + 1))
  fi
  echo ""
}

echo "=== validate-sourcea-public-proof-e2e-v1 start ==="
echo ""

_run "brain knowledge" bash "$SCRIPTS/validate-sourcea-brain-knowledge-v1.sh"
_run "brain live production" bash "$SCRIPTS/validate-sourcea-brain-live-v1.sh"
_run "brain chat" bash "$SCRIPTS/validate-sourcea-brain-chat-v1.sh"
_run "contract SKU pages" env SOURCEA_CONTRACT_E2E_PUBLIC_ONLY=1 bash "$SCRIPTS/validate-sourcea-contract-pages-e2e-v1.sh"
_run "brain landing stack" bash "$SCRIPTS/validate-sourcea-brain-landing-e2e-v1.sh"
_run "sourcea-sdk" bash "$SCRIPTS/validate-sourcea-sdk-v1.sh"
_run "sourcea-boot" bash "$SCRIPTS/validate-sourcea-boot-v1.sh"
_run "brain core boundary tests" python3 -m pytest tests/brain_core_v1/ -q
_run "locked definitions promotion" python3 "$SCRIPTS/promote_locked_definitions_v1.py" --json

if [[ $errors -gt 0 ]]; then
  echo "validate-sourcea-public-proof-e2e-v1: FAIL errors=$errors"
  exit 1
fi
echo "validate-sourcea-public-proof-e2e-v1: ALL PASS"
