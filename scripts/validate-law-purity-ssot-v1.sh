#!/usr/bin/env bash
# validate-law-purity-ssot-v1.sh — LAW PURITY POLICY alive in authority index SSOT
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
INDEX="$ROOT/SINA_AUTHORITY_INDEX_MAP_LOCKED_v1.md"
ENTRY="$ROOT/SINA_GOVERNANCE_ENTRY_LOCKED_v1.md"
SSOT="$ROOT/SINA_OS_SSOT_LOCKED.md"

fail() { echo "FAIL: validate-law-purity-ssot-v1 — $*" >&2; exit 1; }

[[ -f "$INDEX" ]] || fail "missing authority index"
[[ -f "$ENTRY" ]] || fail "missing governance entry"
[[ -f "$SSOT" ]] || fail "missing SINA_OS_SSOT"

grep -q "LAW PURITY POLICY (SSOT" "$INDEX" || fail "authority index missing LAW PURITY POLICY section"
grep -q "Law = law (100%)" "$INDEX" || fail "missing rule 1 Law = law"
grep -q "No fragmentation" "$INDEX" || fail "missing rule 2 no fragmentation"
grep -q "No duplication" "$INDEX" || fail "missing rule 3 no duplication"
grep -q "No mixing unrelated subjects" "$INDEX" || fail "missing rule 4 no mixing"
grep -q "Ask if you don't know" "$INDEX" || fail "missing rule 5 ask if unknown"
grep -q "LAW PURITY (SSOT)" "$ENTRY" || fail "governance entry §11 missing LAW PURITY pointer"
grep -q "LAW PURITY POLICY" "$SSOT" || fail "SINA_OS_SSOT missing LAW PURITY pointer"

echo "OK: validate-law-purity-ssot-v1"
