#!/usr/bin/env bash
# validate-governance-propagation-live-v1.sh — G0→P4 cascade wired (live governance)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-governance-propagation-live-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md" ]] || fail "missing big picture law"
[[ -f "$ROOT/scripts/governance_propagation_cascade_v1.py" ]] || fail "missing cascade module"

grep -q "governance_propagation_cascade" "$ROOT/scripts/goal1_lane_broker.py" || fail "broker not wired"
grep -q "SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md" "$ROOT/scripts/monitor_live_sync_v1.py" || fail "monitor missing G0 watch"
grep -q "P0–P7" "$ROOT/SOURCEA_LIVE_GOVERNANCE_BIG_PICTURE_LOCKED_v1.md" || fail "missing P0-P7 tiers"

python3 "$ROOT/scripts/governance_propagation_cascade_v1.py" --reason "validator_probe" --json >/dev/null \
  || fail "cascade probe failed"

[[ -f "$HOME/.sina/governance-propagation-receipt-v1.json" ]] || fail "missing propagation receipt"

bash "$ROOT/scripts/validate-governance-event-spine-v1.sh"

echo "OK: validate-governance-propagation-live-v1"
