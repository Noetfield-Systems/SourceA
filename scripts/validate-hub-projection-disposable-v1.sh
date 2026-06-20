#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-hub-projection-disposable-v1 — $*" >&2; exit 1; }

grep -q "Projection disposable" "$ROOT/HUB_STABILIZATION_v5.1_FINAL.md" || fail "HUB_STABILIZATION Track 2 criterion missing"
grep -q "hub-canonical-projection-v1" "$ROOT/scripts/hub_projection_canonical_v1.py" || fail "canonical/runtime split missing"
python3 "$ROOT/scripts/hub_projection_disposable_test_v1.py" || fail "disposable projection test"

echo "OK: validate-hub-projection-disposable-v1"
