#!/usr/bin/env bash
# run-mac-health-recipe-v1.sh — Mac Health ship (NO marathon on Mac control plane)
#
# Mac founder session: sync bundles + ship-fast only (≤90s read-only)
# Full E2E: cloud CI only (SOURCEA_CI=1 or ASF fresh ship window + --full)
#
# Usage:
#   bash scripts/run-mac-health-recipe-v1.sh           # sync + ship-fast
#   bash scripts/run-mac-health-recipe-v1.sh --full    # cloud CI / fresh ship window only
#   bash scripts/run-mac-health-recipe-v1.sh --build   # ship-fast + rebuild .app (ship window)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_mac_health_validator_common_v1.sh
source "$ROOT/scripts/_mac_health_validator_common_v1.sh"

FULL=0
BUILD=0
for arg in "$@"; do
  case "$arg" in
    --full) FULL=1 ;;
    --build) BUILD=1 ;;
  esac
done

if [[ "$BUILD" -eq 1 ]]; then
  # shellcheck source=_founder_session_gate_entry_v1.sh
  source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
  _founder_session_gate_or_exit "run-mac-health-recipe-v1.sh" "$ROOT"
fi

echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Mac Health Guard RECIPE v1 — no manual cp · no marathon   ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
echo "SSOT: scripts/mac-health-standalone/ + scripts/mac_health_*.py"
echo "Mac gate: validate-mac-health-ship-fast-v1.sh (≤90s read-only)"
echo ""

bash "$ROOT/scripts/sync-standalone-apps-to-bundles-v1.sh"

if [[ "$FULL" -eq 1 ]] && { [[ -n "${SOURCEA_CI:-}${GITHUB_ACTIONS:-}" ]] || _mh_ship_window; }; then
  echo "=== Full tier (CI / fresh ship window) ==="
  MH_FORCE_E2E_MARATHON=1 bash "$ROOT/scripts/validate-mac-health-e2e-v1.sh" --tier full
elif [[ -f "${HOME}/.sina/mac-control-plane-v1.flag" ]]; then
  bash "$ROOT/scripts/validate-mac-health-ship-fast-v1.sh"
else
  bash "$ROOT/scripts/validate-mac-health-ship-fast-v1.sh"
fi

if [[ "$BUILD" -eq 1 ]]; then
  echo ""
  echo "=== Rebuilding Mac Health Guard.app (Desktop + Applications) ==="
  bash "$ROOT/scripts/build-mac-health-standalone-app-v1.sh"
fi

echo ""
echo "✓ Mac Health Guard recipe PASS"
echo "  UI: http://127.0.0.1:13024/"
