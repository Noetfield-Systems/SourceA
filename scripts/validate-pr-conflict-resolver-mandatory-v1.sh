#!/usr/bin/env bash
# validate-pr-conflict-resolver-mandatory-v1.sh — machine wiring gate for PR conflict skill lock.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: $1"; exit 1; }

for f in \
  data/pr-conflict-resolver-mandatory-v1.json \
  scripts/pr_conflict_resolver_first_check_v1.py \
  scripts/verify_pr_conflict_skill_v1.py \
  brain-os/law/enforcement/PR_CONFLICT_RESOLVER_MANDATORY_LOCKED_v1.md \
  docs/PR_CONFLICT_RESOLVER_REPORT_APP_PR_CONFLICT_RESOLVER_SKILL_MANDATORY_MAC_LOCKED_v1.md \
  .cursor/rules/pr-conflict-resolver-mandatory-v1.mdc; do
  [[ -f "$f" ]] || fail "missing $f"
done

grep -q 'pr_conflict_resolver_first_check' scripts/pre_write_guard_v1.py \
  || fail "pre_write_guard missing pr_conflict_resolver_first_check"
grep -q 'pr_conflict_resolver_first_check' scripts/agent_session_gate_run_v1.py \
  || fail "session gate missing pr_conflict_resolver_first_check"

python3 scripts/verify_pr_conflict_skill_v1.py --json >/dev/null \
  || fail "verify_pr_conflict_skill_v1.py"

echo "PASS: validate-pr-conflict-resolver-mandatory-v1.sh"
