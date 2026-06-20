#!/usr/bin/env bash
# validate-commercial-email-send-defer-v1.sh — nerve + send gate defer law
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/commercial-email-send-defer-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/commercial_email_send_defer_v1.py || { echo "FAIL missing script"; exit 1; }

python3 scripts/commercial_email_send_defer_v1.py --json >/dev/null
test -f "${SINA}/commercial-email-send-defer-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }
test -f "${SINA}/commercial-email-send-deferred-v1.flag" || { echo "FAIL defer flag should exist while active"; exit 1; }

python3 scripts/commercial_email_send_defer_v1.py --validate-wire --json >/dev/null

echo "PASS: validate-commercial-email-send-defer-v1"
