#!/usr/bin/env bash
# validate-authority-index-coverage-v1.sh — root *_LOCKED_v1.md rows in authority index (AS-10)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=governance-paths-v1.sh
. "$ROOT/scripts/governance-paths-v1.sh"
INDEX="$SINA_AUTHORITY_INDEX"

fail() { echo "FAIL: validate-authority-index-coverage-v1 — $*" >&2; exit 1; }

[[ -f "$INDEX" ]] || fail "missing SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md"
cd "$ROOT"

bash "$ROOT/scripts/validate-law-purity-ssot-v1.sh" || fail "LAW PURITY SSOT latch"

python3 scripts/authority_root_coverage_audit.py --check || {
  python3 scripts/authority_root_coverage_audit.py
  fail "T3 orphans — see SOURCEA_AUTHORITY_REGISTRY_GOV_UNIFY_BATCH_2026-06-11_LOCKED_v1.md"
}

echo "OK: validate-authority-index-coverage-v1"
