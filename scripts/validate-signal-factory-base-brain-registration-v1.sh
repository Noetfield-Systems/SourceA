#!/usr/bin/env bash
# validate-signal-factory-base-brain-registration-v1.sh — Base Brain registration guard (light)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${SIGNAL_FACTORY_PYTHON:-/usr/bin/python3}"
fail() { echo "FAIL: validate-signal-factory-base-brain-registration-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/data/sourcea-base-brain-skills-v1.json" ]] || fail "missing base brain skills registry"
[[ -f "$ROOT/receipts/brain/signal-factory-v1-base-brain-registration-v1.json" ]] \
  || fail "missing registration receipt"

grep -q '"skill_id": "signal-factory-v1"' "$ROOT/data/sourcea-base-brain-skills-v1.json" \
  || fail "signal-factory not in base brain registry"
grep -q '"status": "verified_registered"' "$ROOT/data/sourcea-base-brain-skills-v1.json" \
  || fail "registration status not verified_registered"
grep -q 'signal-factory-v1' "$ROOT/data/sourcea-brain-registry-inventory-v1.json" \
  || fail "brain inventory missing signal-factory-v1 asset"

"$PY" "$ROOT/scripts/validate-signal-factory-locked-definitions-collision-v1.py" --json >/dev/null \
  || fail "locked-definitions collision check failed"

bash "$ROOT/scripts/validate-signal-factory-v1.sh" >/dev/null || fail "structural verifier failed"

echo "PASS: validate-signal-factory-base-brain-registration-v1.sh"
