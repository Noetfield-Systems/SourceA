#!/usr/bin/env bash
# validate-enforcement-preserved-spirit-v1.sh — lineage doc present + weekly Annex A wired
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LINEAGE="$ROOT/SINA_ENFORCEMENT_6MO_PRESERVED_SPIRIT_AND_LINEAGE_LOCKED_v1.md"
WEEKLY="$ROOT/brain-os/law/enforcement/ENFORCEMENT_6MO_WEEKLY_OPERATING_PLAN_LOCKED_v1.md"
MASTER="$ROOT/ENFORCEMENT-6MO-MASTER-PLAN-v1.md"

fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f "$LINEAGE" ]] || fail "missing PRESERVED_SPIRIT lineage law"
grep -q "Annex A" "$WEEKLY" || fail "weekly plan missing Annex A preserved spirit"
grep -q "PRESERVED_SPIRIT" "$MASTER" || fail "MASTER-PLAN missing preserved spirit pointer"
grep -q "FM1" "$LINEAGE" || fail "lineage missing failure modes transfer"
grep -q "Layered advisory" "$LINEAGE" || fail "lineage missing advisory transfer"

bash "$ROOT/scripts/validate-p0-portfolio-automation-law-v1.sh"

echo "OK: enforcement preserved spirit · lineage · annex wired"
