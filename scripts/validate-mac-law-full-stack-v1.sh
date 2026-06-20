#!/usr/bin/env bash
# validate-mac-law-full-stack-v1.sh — LIGHT · one python assess · grep wiring only
set -euo pipefail
cd "$(dirname "$0")/.."

fail() { echo "FAIL: validate-mac-law-full-stack-v1 — $*" >&2; exit 1; }

python3 scripts/mac_law_validator_light_assess_v1.py --module all --json >/dev/null || fail "light assess all"

grep -q 'mac_law_agent_execution_plane_lock' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire lock step"
grep -q 'mac_law_agent_execution_plane_lock' scripts/governance_zero_drift_live_wire_v1.py || fail "governance mac law step"
grep -q 'mac_law_universal_wire_sync' scripts/agent_rule_live_wire_v1.py || fail "rule live wire mac law steps"
grep -q 'mac_law_validator_light_assess_v1.py' scripts/validate-mac-law-universal-wire-v1.sh || fail "universal validator not light"

echo "PASS: validate-mac-law-full-stack-v1 (light — no bash validator chains)"
