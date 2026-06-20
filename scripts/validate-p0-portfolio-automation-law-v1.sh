#!/usr/bin/env bash
# validate-p0-portfolio-automation-law-v1.sh — stub: P0 portfolio law presence + outreach agentic check
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAW="$ROOT/SINA_P0_PORTFOLIO_AUTOMATION_AND_EVIDENCE_LAW_LOCKED_v1.md"
SUPER="$ROOT/SINA_ENFORCEMENT_6MO_LAW_SUPERSESSION_LOCKED_v1.md"
WEEKLY="$ROOT/brain-os/law/enforcement/ENFORCEMENT_6MO_WEEKLY_OPERATING_PLAN_LOCKED_v1.md"

fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f "$LAW" ]] || fail "missing P0 portfolio LOCKED law"
[[ -f "$SUPER" ]] || fail "missing ENFORCEMENT supersession law"
grep -q "1.1" "$WEEKLY" 2>/dev/null || fail "weekly plan not v1.1 (agentic patch)"
grep -q "agentic commercial" "$WEEKLY" 2>/dev/null || fail "weekly plan missing agentic commercial section"

if grep -q "schedule 3 discovery calls" "$WEEKLY" 2>/dev/null; then
  fail "weekly plan still has manual discovery calls clause"
fi

echo "OK: P0 portfolio automation law stack present · weekly v1.1 agentic"
