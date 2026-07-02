#!/usr/bin/env bash
# Run SG brain-loop scripts from SourceA (scripts live in sina-governance-ssot repo).
set -euo pipefail
SG_ROOT="${SG_ROOT:-$HOME/Projects/sina-governance-ssot}"
SOURCEA_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export SOURCEA_ROOT

if [[ ! -d "$SG_ROOT/scripts" ]]; then
  echo "FAIL: SG repo not found at $SG_ROOT" >&2
  echo "Set SG_ROOT to your sina-governance-ssot checkout." >&2
  exit 1
fi

cmd="${1:-help}"
shift || true

case "$cmd" in
  self-heal)
    export BRAIN_SELF_HEAL_TRIGGER="${BRAIN_SELF_HEAL_TRIGGER:-1}"
    bash "$SG_ROOT/scripts/brain_loop_self_heal_v1.sh" "$@"
    ;;
  parallel)
    bash "$SG_ROOT/scripts/run_parallel_brain_candidates_v1.sh" "$@"
    ;;
  matrix)
    bash "$SG_ROOT/scripts/validate_brain_domain_e2e_matrix_v1.sh" "$@"
    ;;
  independence)
    bash "$SG_ROOT/scripts/prove_verifier_independence_v1.sh" "$@"
    ;;
  autorun)
    bash "$SG_ROOT/scripts/brain_loop_autorun_v1.sh" "$@"
    ;;
  rollback)
    bash "$SOURCEA_ROOT/scripts/brain_rollback_drill_v1.sh" "$@"
    ;;
  help|*)
    cat <<EOF
SourceA → SG brain loop wrapper

  bash $SOURCEA_ROOT/scripts/sg_brain_loop_v1.sh self-heal
  bash $SOURCEA_ROOT/scripts/sg_brain_loop_v1.sh parallel --all
  bash $SOURCEA_ROOT/scripts/sg_brain_loop_v1.sh matrix
  bash $SOURCEA_ROOT/scripts/sg_brain_loop_v1.sh independence
  bash $SOURCEA_ROOT/scripts/sg_brain_loop_v1.sh autorun
  bash $SOURCEA_ROOT/scripts/sg_brain_loop_v1.sh rollback [dry-run|execute]

SG_ROOT=$SG_ROOT
SOURCEA_ROOT=$SOURCEA_ROOT
EOF
    ;;
esac
