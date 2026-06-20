#!/usr/bin/env bash
# validate-portfolio-competitor-pick-v1.sh — pick scripts + smoke pick per stack
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail=0
for f in \
  portfolio_competitor_pick_lib.py \
  pick-portfolio-competitor-plan.py \
  portfolio_competitor_forge_dispatch_v1.py \
  pick-sourcea-competitor-mkt-plan.py \
  pick-witnessbc-competitor-mkt-plan.py \
  pick-noetfield-competitor-mkt-plan.py \
  pick-trustfield-competitor-mkt-plan.py \
  pick-virlux-competitor-mkt-plan.py \
  plan-competitor-mkt-run.sh; do
  [[ -f "$ROOT/scripts/$f" ]] || { echo "FAIL missing scripts/$f"; fail=1; }
done

python3 "$ROOT/scripts/pick-portfolio-competitor-plan.py" --stack sourcea --limit 1 --json >/dev/null || fail=1
python3 "$ROOT/scripts/pick-portfolio-competitor-plan.py" --stack virlux --limit 1 --json >/dev/null || fail=1
python3 "$ROOT/scripts/portfolio_competitor_forge_dispatch_v1.py" --stack sourcea --dry-run --json >/dev/null || fail=1

if [[ "$fail" -ne 0 ]]; then
  echo "FAIL portfolio-competitor-pick-v1"
  exit 1
fi
echo "PASS portfolio-competitor-pick-v1 — 5 stacks wired · FORGE dispatch dry-run ok"
