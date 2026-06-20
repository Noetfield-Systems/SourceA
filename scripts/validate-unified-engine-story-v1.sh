#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }
for f in \
  "$ROOT/SINA_UNIFIED_ENGINE_STORY_LOCKED_v1.md" \
  "$ROOT/SINA_ENFORCEMENT_PORTFOLIO_DECISION_FORM_LOCKED_v1.md" \
  "$ROOT/SINA_P0_PORTFOLIO_AUTOMATION_AND_EVIDENCE_LAW_LOCKED_v1.md"; do
  [[ -f "$f" ]] || fail "missing $f"
done
grep -q "FounderField" "$ROOT/SINA_P0_PORTFOLIO_AUTOMATION_AND_EVIDENCE_LAW_LOCKED_v1.md" || fail "FounderField not in P0 law"
grep -q "ENG-01" "$ROOT/SINA_ENFORCEMENT_PORTFOLIO_DECISION_FORM_LOCKED_v1.md" || fail "decision form missing locked batch"
bash "$ROOT/scripts/validate-enforcement-preserved-spirit-v1.sh"
echo "OK: unified engine story · decision form · lineage chain"
