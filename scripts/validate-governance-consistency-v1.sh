#!/usr/bin/env bash
# validate-governance-consistency-v1.sh — governance clarity checks (Step 5)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0
warn() { echo "WARN: $*"; }
err() { echo "FAIL: $*"; FAIL=1; }
ok() { echo "OK: $*"; }

echo "=== SourceA governance consistency v1 ==="

# Check 1: Unified entry exists
for f in \
  docs/SOURCEA_GOVERNANCE_ENTRY_UNIFIED_LOCKED_v1.md \
  docs/SOURCEA_BRAIN_AUTHORITY_UNIFIED_LOCKED_v1.md \
  docs/SOURCEA_WORKER_SCOPE_UNIFIED_LOCKED_v1.md \
  docs/SOURCEA_UNIFIED_RUNTIME_MODEL_LOCKED_v1.md \
  docs/SOURCEA_GOVERNANCE_FRAGMENTATION_AUDIT_v1.md; do
  [[ -f "$f" ]] && ok "exists $f" || err "missing $f"
done

# Check 2: Old indexes marked superseded
for f in docs/CURSOR_CONTEXT_INDEX_LOCKED_v1.md docs/SOURCEA_SSOT_INDEX_LOCKED_v1.md; do
  if [[ -f "$f" ]] && grep -q "SUPERSEDED_BY.*SOURCEA_GOVERNANCE_ENTRY_UNIFIED" "$f" 2>/dev/null; then
    ok "superseded header on $f"
  else
    err "missing superseded header on $f"
  fi
done

# Check 3: Always-apply rules count (expect 9)
AA_COUNT=$(rg -l 'alwaysApply: true' .cursor/rules/*.mdc 2>/dev/null | wc -l | tr -d ' ')
if [[ "$AA_COUNT" -eq 9 ]]; then
  ok "alwaysApply count = 9"
else
  err "alwaysApply count = $AA_COUNT (expected 9)"
fi

# Check 4: Entry gate references unified entry
if rg -q 'SOURCEA_GOVERNANCE_ENTRY_UNIFIED_LOCKED_v1' .cursor/rules/000-entry-gate.mdc 2>/dev/null; then
  ok "000-entry-gate references unified entry"
else
  warn "000-entry-gate does not yet reference unified entry (optional)"
fi

# Check 5: Brain unified says never implement sa
if rg -q 'never.*implement|does not implement' docs/SOURCEA_BRAIN_AUTHORITY_UNIFIED_LOCKED_v1.md 2>/dev/null; then
  ok "Brain authority forbids sa implement"
else
  err "Brain authority missing implement ban"
fi

# Check 6: Archive manifest exists
MANIFEST="data/superseded-law-archive-manifest-v1.json"
if [[ -f "$MANIFEST" ]]; then
  ARCHIVED=$(python3 -c "import json; print(len(json.load(open('$MANIFEST'))['files']))" 2>/dev/null || echo 0)
  if [[ "$ARCHIVED" -ge 30 ]]; then
    ok "archived $ARCHIVED superseded law files"
  else
    err "only $ARCHIVED archived (expected >= 30)"
  fi
else
  err "missing $MANIFEST"
fi

# Check 7: Onboarding guides
for role in BRAIN WORKER MAINTAINER; do
  f="docs/SOURCEA_ONBOARDING_${role}_ROLE_LOCKED_v1.md"
  [[ -f "$f" ]] && ok "exists $f" || err "missing $f"
done

# Check 8: Rule template
[[ -f docs/SOURCEA_RULE_TEMPLATE_LOCKED_v1.md ]] && ok "rule template exists" || err "missing rule template"

# Check 9: Lint script
[[ -x scripts/lint-cursor-rules-format-v1.sh ]] && ok "lint script executable" || err "missing lint script"

echo "=== done (failures: $FAIL) ==="
exit "$FAIL"
