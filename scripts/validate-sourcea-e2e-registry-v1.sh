#!/usr/bin/env bash
# Validate SourceA E2E check registry — row count, e2e scripts, overrides schema.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
REG="data/sourcea-e2e-check-registry-v1.json"
OVERRIDES="data/sourcea-e2e-check-registry-overrides-v1.json"
GEN="scripts/sourcea_e2e_registry_generate_v1.py"
FAIL=0

fail() { echo "FAIL: $*"; FAIL=1; }

echo "=== validate-sourcea-e2e-registry-v1 ==="

if [[ ! -f "$REG" ]]; then
  fail "missing $REG — run python3 $GEN"
fi

if [[ ! -f "$OVERRIDES" ]]; then
  fail "missing $OVERRIDES"
fi

python3 -c "
import json, sys
from pathlib import Path
root = Path('$ROOT')
reg = json.loads((root / '$REG').read_text())
checks = reg.get('checks') or []
if len(checks) < 100:
    print('FAIL: registry too small', len(checks))
    sys.exit(1)
e2e = [c for c in checks if 'e2e' in c.get('id','').lower()]
if len(e2e) < 20:
    print('FAIL: e2e_named too few', len(e2e))
    sys.exit(1)
bundles = reg.get('bundles') or {}
for bid in ('mac_daily_smoke', 'hub_e2e_core', 'sourcea_standard'):
    if bid not in bundles:
        print('FAIL: missing bundle', bid)
        sys.exit(1)
print('OK: registry checks=%d e2e=%d bundles=%d' % (len(checks), len(e2e), len(bundles)))
" || fail "registry schema check"

# Drift: regenerate dry-run count
discovered=$(find scripts -maxdepth 1 -name 'validate-*-v1.sh' 2>/dev/null | wc -l | tr -d ' ')
registered=$(python3 -c "import json; print(len(json.load(open('$REG'))['checks']))")
if [[ "$registered" -lt "$discovered" ]]; then
  echo "WARN: registered=$registered discovered_shell=$discovered — run python3 $GEN"
fi

if [[ $FAIL -eq 0 ]]; then
  echo "validate-sourcea-e2e-registry-v1 PASS"
  exit 0
fi
exit 1
