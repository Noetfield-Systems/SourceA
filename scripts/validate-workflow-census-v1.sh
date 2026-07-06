#!/usr/bin/env bash
# validate-workflow-census-v1 — structure + dry-run census
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }

MIG="$ROOT/infra/supabase/portfolio-spine/migrations/014_workflow_census_v1.sql"
MAP="$ROOT/data/workflow-census-loop-map-v1.json"
SCRIPT="$ROOT/scripts/workflow_census_v1.py"
AUDIT="$ROOT/scripts/workflow_census_audit_v1.py"

[[ -f "$MIG" ]] || fail "missing migration 014"
[[ -f "$MAP" ]] || fail "missing loop map"
[[ -f "$SCRIPT" ]] || fail "missing workflow_census_v1.py"
[[ -f "$AUDIT" ]] || fail "missing workflow_census_audit_v1.py"
grep -q 'workflow_census' "$MIG" || fail "migration missing table"
grep -q 'REVENUE' "$MAP" || fail "map missing REVENUE class"

python3 "$SCRIPT" --dry-run --json >/dev/null || fail "dry-run census failed"
grep -q 'workflow-census/weekly' "$ROOT/data/loop-specialist-cron-dispatch-v1.json" || fail "weekly cron not wired"

echo "PASS validate-workflow-census-v1"
