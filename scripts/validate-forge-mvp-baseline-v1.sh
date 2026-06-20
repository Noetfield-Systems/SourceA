#!/usr/bin/env bash
# validate-forge-mvp-baseline-v1.sh — Forge MVP baseline gate (5 stacks + schemas)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
pass() { echo "PASS $1"; }
fail_line() { echo "FAIL $1"; fail=1; }

echo "=== Forge MVP baseline v1 ==="

bash "$ROOT/scripts/validate-portfolio-competitor-pick-v1.sh" >/dev/null 2>&1 \
  && pass "competitor pick scripts" \
  || fail_line "competitor pick validate"

python3 -c "import json; assert json.load(open('$ROOT/data/portfolio-competitor-1000-manifest-v1.json')).get('ok')" \
  && pass "competitor manifest ok" \
  || fail_line "competitor manifest"

python3 -c "
import json
from pathlib import Path
ROOT = Path('$ROOT')
json.load(open(ROOT/'data/forge-mvp-router-rules-v0.1.json'))
json.load(open(ROOT/'data/schemas/forge-task-graph-v0.1.json'))
" && pass "forge-mvp JSON schemas" || fail_line "forge-mvp JSON schemas"

bash "$ROOT/scripts/validate-doc-datetime-header-v1.sh" \
  "$ROOT/docs/FORGE_MVP_BLUEPRINT_LOCKED_v1.md" >/dev/null 2>&1 \
  && pass "blueprint doc datetime" \
  || fail_line "blueprint doc datetime"

for stack in sourcea witnessbc noetfield trustfield virlux; do
  if python3 "$ROOT/scripts/pick-portfolio-competitor-plan.py" --stack "$stack" --limit 1 --json >/dev/null 2>&1; then
    pass "pick stack=$stack"
  else
    fail_line "pick stack=$stack"
  fi
done

if python3 "$ROOT/scripts/portfolio_competitor_forge_dispatch_v1.py" --stack sourcea --dry-run --json >/dev/null 2>&1; then
  pass "forge dispatch dry-run"
else
  fail_line "forge dispatch dry-run"
fi

if [[ "$fail" -ne 0 ]]; then
  echo "FAIL forge-mvp-baseline-v1"
  exit 1
fi
echo "PASS forge-mvp-baseline-v1 — all stacks + schemas"
