#!/usr/bin/env bash
# Pick / verify automation-converge-1000 pack (Musk program Worker prompts)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REG="$ROOT/brain-os/plan-registry/automation-converge-1000/REGISTRY.json"
PY="$ROOT/scripts/pick-automation-converge-plan.py"

pick_one() {
  python3 "$PY"
}

case "${1:-pick}" in
  pick)
    echo "=== PLAN WITH NO ASF — AUTOMATION CONVERGE — next prompt ==="
    pick_one
    ;;
  1) pick_one ;;
  verify-hub)
    cd "$ROOT/scripts" && python3 find_critical_bugs.py
    ;;
  *)
    echo "Usage: $0 pick|1|verify-hub" >&2
    exit 1
    ;;
esac
