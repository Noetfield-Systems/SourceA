#!/usr/bin/env bash
# PLAN WITH NO ASF — pick next sa-* prompt, validate pack, hub verify
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODE="${1:-pick}"
LIMIT="${2:-1}"

case "$MODE" in
  route)
    KW="${2:-implement}"
    LANE="${3:-sourcea}"
    shift 3 2>/dev/null || true
    echo "=== prompt_router — keyword=$KW lane=$LANE ==="
    python3 "$ROOT/scripts/prompt_router.py" --keyword "$KW" --lane "$LANE" "$@"
    ;;
  pick)
    echo "=== PLAN WITH NO ASF — next SourceA prompt ==="
    python3 "$ROOT/scripts/pick-sourcea-no-asf-plan.py" --any-tier --limit "$LIMIT" --prompt
    ;;
  pick-next)
    echo "=== PLAN WITH NO ASF — next portfolio-next plan (sa-next-*) ==="
    python3 "$ROOT/scripts/pick_portfolio_next_plan_v1.py" --repo sourcea --any-phase --limit "$LIMIT" --prompt
    ;;
  pick-agentgo)
    echo "=== PLAN WITH NO ASF — AgentGo SA4 case study 6000 (A→B→C) ==="
    python3 "$ROOT/scripts/pick_agentgo_case_study_plan_v1.py" --all-angles --any-phase --limit "$LIMIT" --prompt
    ;;
  validate-pack)
    bash "$ROOT/scripts/validate-sourcea-1000-pack.sh"
    ;;
  verify-hub)
    cd "$ROOT/scripts"
    SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py
    python3 find_critical_bugs.py
    ;;
  closeout)
    echo "Mark sa-* status done in prompt front matter"
    echo "Append REPO_EXECUTION_LOGS/sourcea/*.yaml with verify_passed"
    echo "Update brain-os/plan-registry/SOURCEA-PRIORITY.md evidence row"
    bash "$ROOT/scripts/validate-sourcea-1000-pack.sh"
    ;;
  l1-cycle)
    KW="${2:-implement}"
    LANE="${3:-sourcea}"
    echo "=== L1 semi-auto cycle — closeout ingest → route → tail reducer (auto-paste OFF) ==="
    python3 "$ROOT/scripts/prompt_router.py" --l1-cycle --keyword "$KW" --lane "$LANE" --json
    ;;
  full)
    bash "$ROOT/scripts/plan-no-asf-run.sh" pick "$LIMIT"
    echo ""
    bash "$ROOT/scripts/plan-no-asf-run.sh" route implement sourcea --dry-run
    echo ""
    echo "Implement task above → then:"
    echo "  bash scripts/plan-no-asf-run.sh verify-hub"
    echo "  bash scripts/plan-no-asf-run.sh closeout"
    ;;
  *)
    echo "Usage: bash scripts/plan-no-asf-run.sh {pick|pick-next|pick-agentgo|route|validate-pack|verify-hub|closeout|l1-cycle|full} [limit|keyword lane]"
    echo "  route implement sourcea [--dry-run|--invoke-loop|--json]"
    exit 1
    ;;
esac
