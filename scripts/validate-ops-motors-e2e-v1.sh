#!/usr/bin/env bash
# validate-ops-motors-e2e-v1.sh — gmail sweep → triage PASS (dry-run safe on Mac)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f "${ROOT}/scripts/gmail_triage_e2e_v1.py" ]] || fail "missing gmail_triage_e2e_v1.py"

if [[ "${OPS_MOTORS_E2E_LIVE:-}" == "1" ]]; then
  python3 "${ROOT}/scripts/gmail_triage_e2e_v1.py" --json
else
  python3 "${ROOT}/scripts/gmail_triage_e2e_v1.py" --dry-run --json
fi

echo "OK: validate-ops-motors-e2e-v1"
