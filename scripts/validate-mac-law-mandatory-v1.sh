#!/usr/bin/env bash
# validate-mac-law-mandatory-v1.sh — LIGHT · assess-only · no surfaces boot · no nested validate chains
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: mac-law-mandatory — $*" >&2; exit 1; }

[[ -f data/mac-law-mandatory-v1.json ]] || fail "missing SSOT"
[[ -f scripts/mac_law_mandatory_v1.py ]] || fail "missing script"
[[ -f .cursor/rules/mac-law-mandatory.mdc ]] || fail "missing cursor rule mac-law-mandatory.mdc"

python3 scripts/mac_law_validator_light_assess_v1.py --module all --json >/dev/null || fail "light assess"

echo "PASS: validate-mac-law-mandatory-v1 (light assess-only — surfaces boot → validate-mac-law-mandatory-ship-v1.sh on cloud CI)"
