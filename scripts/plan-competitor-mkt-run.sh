#!/usr/bin/env bash
# Portfolio competitor-1000 — pick · validate · FORGE cloud dispatch (Mac observes only)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODE="${1:-pick}"
STACK="${2:-sourcea}"
LIMIT="${3:-1}"

pick_stack() {
  local stack="$1"
  local limit="$2"
  shift 2 || true
  python3 "$ROOT/scripts/pick-portfolio-competitor-plan.py" \
    --stack "$stack" --any-tier --limit "$limit" --prompt "$@"
}

case "$MODE" in
  pick)
    pick_stack "$STACK" "$LIMIT"
    ;;
  pick-all)
    for s in sourcea witnessbc noetfield trustfield virlux; do
      echo "--- $s ---"
      pick_stack "$s" 1 || true
      echo ""
    done
    ;;
  json)
    python3 "$ROOT/scripts/pick-portfolio-competitor-plan.py" \
      --stack "$STACK" --any-tier --limit "$LIMIT" --json --forge
    ;;
  validate)
    bash "$ROOT/scripts/validate-portfolio-competitor-1000-v1.sh"
    bash "$ROOT/scripts/validate-portfolio-competitor-pick-v1.sh"
    bash "$ROOT/scripts/validate-forge-mvp-baseline-v1.sh"
    ;;
  dispatch-forge)
    DRY=""
    [[ "${4:-}" == "--dry-run" ]] && DRY="--dry-run"
    python3 "$ROOT/scripts/portfolio_competitor_forge_dispatch_v1.py" \
      --stack "$STACK" $DRY --json
    ;;
  route)
    echo "=== competitor-1000 route — stack=$STACK lane=FORGE cloud ==="
    pick_stack "$STACK" 1
    echo ""
    echo "Cloud dispatch (dry-run receipt):"
    python3 "$ROOT/scripts/portfolio_competitor_forge_dispatch_v1.py" --stack "$STACK" --dry-run --json
    ;;
  full)
    bash "$ROOT/scripts/plan-competitor-mkt-run.sh" validate
    echo ""
    bash "$ROOT/scripts/plan-competitor-mkt-run.sh" route "$STACK"
    ;;
  *)
    echo "Usage: bash scripts/plan-competitor-mkt-run.sh {pick|pick-all|json|validate|dispatch-forge|route|full} [stack] [limit] [--dry-run]"
    echo "  Stacks: sourcea | witnessbc | noetfield | trustfield | virlux"
    echo "  Law: build on cloud FORGE only — Mac control panel observes"
    exit 1
    ;;
esac
