#!/usr/bin/env bash
# validate-ecosystem-mac-health-111-plan-v1.sh
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
PLAN="$ROOT/data/ecosystem-mac-health-111-upgrade-plan-v1.json"
DOC="$ROOT/docs/SOURCEA_ECOSYSTEM_MAC_HEALTH_111_UPGRADE_PLAN_LOCKED_v1.md"

[[ -f "$PLAN" ]] || { echo "FAIL: missing plan — run gen_ecosystem_mac_health_111_plan_v1.py --write"; exit 1; }
[[ -f "$DOC" ]] || { echo "FAIL: missing locked doc"; exit 1; }

python3 -c "
import json, sys
p = json.loads(open('$PLAN').read())
ups = p.get('upgrades') or []
assert len(ups) == 111, len(ups)
assert p.get('schema') == 'ecosystem-mac-health-111-upgrade-plan-v1'
ids = [u['id'] for u in ups]
assert len(set(ids)) == 111
assert ids[0] == 'M111-001' and ids[-1] == 'M111-111'
print('OK: 111 upgrades · tiers', p.get('tier_counts'))
"

python3 "$ROOT/scripts/ecosystem_mac_health_111_plan_pulse_v1.py" --json >/dev/null
echo "PASS validate-ecosystem-mac-health-111-plan-v1"
