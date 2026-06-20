#!/usr/bin/env bash
# run-mac-health-recipe-v1.sh — MANDATORY Mac Health Guard ship gate.
# Never ad-hoc cp scripts/app into bundles — always run this recipe (or validate-mac-health-e2e-v1.sh).
#
# Usage:
#   bash scripts/run-mac-health-recipe-v1.sh           # sync + validators + restart heart
#   bash scripts/run-mac-health-recipe-v1.sh --build   # above + rebuild Desktop .app
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
if [[ "${1:-}" == "--build" ]]; then
  # shellcheck source=_founder_session_gate_entry_v1.sh
  source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
  _founder_session_gate_or_exit "run-mac-health-recipe-v1.sh" "$ROOT"
fi

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Mac Health Guard RECIPE v1 — no manual cp allowed       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "SSOT:  scripts/mac-health-standalone/ + scripts/mac_health_*.py"
echo "Sync:  scripts/sync-standalone-apps-to-bundles-v1.sh"
echo "Gate:  scripts/validate-mac-health-e2e-v1.sh"
echo ""

bash "$ROOT/scripts/validate-mac-health-e2e-v1.sh"

if [[ "${1:-}" == "--build" ]]; then
  echo ""
  echo "=== Rebuilding Mac Health Guard.app (Desktop + Applications) ==="
  bash "$ROOT/scripts/build-mac-health-standalone-app-v1.sh"
fi

echo ""
echo "✓ Mac Health Guard recipe PASS"
echo "  UI: http://127.0.0.1:13024/  → Auto guard tab"
