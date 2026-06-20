#!/usr/bin/env bash
# validate-incident-fix-ownership-v1.sh — wiring + tiered audit (fast default)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=governance-paths-v1.sh
. "$ROOT/scripts/governance-paths-v1.sh"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-incident-fix-ownership-v1 — $*" >&2; exit 1; }

MODE="fast"
for arg in "$@"; do
  case "$arg" in
    --deep) MODE="deep" ;;
    --fast) MODE="fast" ;;
  esac
done

LAW="$ROOT/SOURCEA_INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING_LOCKED_v1.md"
[[ -f "$LAW" ]] || fail "missing LOCKED law"

grep -q 'INCIDENT_FIX_OWNERSHIP' "$SINA_AUTHORITY_INDEX" || fail "authority index missing row"
grep -q 'INCIDENT_FIX_OWNERSHIP_GOVERNANCE_HARDENING' "$SINA_GOVERNANCE_ENTRY" || fail "governance entry missing §0p"
grep -q 'governance_stairlift_sync_v1.py' "$ROOT/scripts/worker_turn_entry_v1.sh" || fail "turn entry missing stairlift"
grep -q 'governance_stairlift_sync_v1.py' "$ROOT/scripts/governance_propagation_cascade_v1.py" || fail "cascade missing stairlift watch"
grep -q 'Balance tiers' "$LAW" || fail "law missing §1.2 balance tiers"

[[ -f "$ROOT/.cursor/rules/incident-fix-ownership.mdc" ]] || fail "missing cursor rule"
[[ -f "$ROOT/.cursor/rules/governance-specialist-in-charge.mdc" ]] || fail "missing governance specialist rule"

if [[ "$MODE" == "fast" ]]; then
  python3 governance_stairlift_sync_v1.py --if-stale --tier hot --json >/dev/null || fail "stairlift hot"
  bash validate-founder-directive-propagation-v1.sh || fail "founder directive propagation"
  python3 - <<'PY' || fail "standing fix matrix (fast)"
import json, sys
sys.path.insert(0, ".")
from incident_fix_ownership_lib_v1 import audit_standing
row = audit_standing(run_validators=False)
if not row.get("ok"):
    print(json.dumps(row, indent=2), file=sys.stderr)
    sys.exit(1)
print(f"OK: fast audit · stairlift payload · {len(row.get('rows') or [])} rows")
PY
  echo "OK: validate-incident-fix-ownership-v1 (fast)"
  exit 0
fi

python3 governance_stairlift_sync_v1.py --force --tier full --json >/dev/null || fail "stairlift full"
python3 - <<'PY' || fail "standing fix matrix (deep)"
import json, sys
sys.path.insert(0, ".")
from incident_fix_ownership_lib_v1 import audit_standing
row = audit_standing(run_validators=True, use_receipt_cache=True)
if not row.get("ok"):
    print(json.dumps(row, indent=2), file=sys.stderr)
    sys.exit(1)
print(f"OK: deep audit · {len(row.get('rows') or [])} rows shipped")
PY

echo "OK: validate-incident-fix-ownership-v1 (deep)"
