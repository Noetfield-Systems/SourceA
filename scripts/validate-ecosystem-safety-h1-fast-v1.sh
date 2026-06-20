#!/usr/bin/env bash
# L2 Hub Safety — Super Fast Hub founder tap (<30s wall · no anti-staleness recursion)
# Law: SOURCEA_FAST_SYSTEM_LOAD_BUDGET_LOCKED_v1.md · SOURCEA_SUPER_FAST_HUB_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
cd "$ROOT"
errors=0

_fail() { echo "FAIL: $1"; errors=$((errors + 1)); }
_ok() { echo "OK: $1"; }

echo "=== validate-ecosystem-safety-h1-fast-v1 (L2 Hub) ==="

if python3 "$SCRIPTS/factory_validation_lock_v1.py" sweep --json >/dev/null 2>&1; then
  _ok "factory lock sweep"
else
  _fail "factory lock sweep"
fi

if python3 "$SCRIPTS/factory_validation_lock_v1.py" status --json | python3 -c "
import json,sys
st=json.load(sys.stdin)
assert not st.get('locked'), st.get('lock')
"; then
  _ok "factory lock clear"
else
  _fail "factory lock busy"
fi

if curl -sf "http://127.0.0.1:13020/health" >/dev/null 2>&1; then
  _ok "hub :13020/health"
else
  _fail "hub :13020 down"
fi

if PYTHONPATH="$SCRIPTS" python3 "$SCRIPTS/_ecosystem_safety_monitor_check_v1.py"; then
  _ok "monitor honesty"
else
  _fail "monitor honesty"
fi

if PYTHONPATH="$SCRIPTS" python3 "$SCRIPTS/_ecosystem_safety_orchestrator_check_v1.py"; then
  _ok "orchestrator + INBOX"
else
  _fail "orchestrator drift"
fi

if PYTHONPATH="$SCRIPTS" python3 "$SCRIPTS/_ecosystem_safety_dual_pick_check_v1.py"; then
  _ok "dual-pick aligned"
else
  _fail "dual-pick gap"
fi

if bash "$SCRIPTS/validate-super-fast-hub-v1.sh" >/dev/null; then
  _ok "super-fast-hub H1"
else
  _fail "validate-super-fast-hub-v1"
fi

if bash "$SCRIPTS/validate-worker-hub-live-v1.sh" >/dev/null; then
  _ok "worker-hub live"
else
  _fail "validate-worker-hub-live-v1"
fi

if bash "$SCRIPTS/validate-machine-hub-v1.sh" >/dev/null; then
  _ok "machine-hub H2"
else
  _fail "validate-machine-hub-v1"
fi

python3 -c "
import sys
sys.path.insert(0, 'scripts')
from sina_command_lib import hub_light_refresh
hub_light_refresh()
print('OK: hub light refresh')
" || _fail "hub_light_refresh"

if [[ $errors -gt 0 ]]; then
  echo "FAIL: validate-ecosystem-safety-h1-fast-v1 errors=$errors"
  exit 1
fi
echo "PASS: validate-ecosystem-safety-h1-fast-v1"
