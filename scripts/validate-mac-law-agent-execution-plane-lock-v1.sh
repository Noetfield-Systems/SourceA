#!/usr/bin/env bash
# validate-mac-law-agent-execution-plane-lock-v1.sh — LIGHT · assess-only · no nested validators
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/mac-law-agent-execution-plane-lock-v1.json || { echo "FAIL missing lock SSOT"; exit 1; }
test -f scripts/mac_law_agent_execution_plane_lock_v1.py || { echo "FAIL missing lock script"; exit 1; }
test -f docs/MAC_LAW_AGENT_EXECUTION_PLANE_LOCK_LOCKED_v1.md || { echo "FAIL missing LOCKED doc"; exit 1; }

python3 scripts/mac_law_validator_light_assess_v1.py --module lock --json >/dev/null
test -f "${SINA}/mac-law-agent-no-factory-on-mac-locked-v1.flag" || { echo "FAIL lock flag"; exit 1; }

echo "PASS: validate-mac-law-agent-execution-plane-lock-v1 (light assess-only)"
