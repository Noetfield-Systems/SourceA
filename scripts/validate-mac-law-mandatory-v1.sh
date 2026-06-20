#!/usr/bin/env bash
# validate-mac-law-mandatory-v1.sh — Mac Law boss order · control plane · mandates (MANDATORY)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: mac-law-mandatory — $*" >&2; exit 1; }

LAW_BOSS="$HOME/Desktop/MacLaw/MAC_LAW_SSOT_LOCKED.md"
LAW_CP="$HOME/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md"
LAW_HEALTH="$HOME/Desktop/MacLaw/MAC_HEALTH_AGENT_MANDATES_LOCKED.md"

[[ -f "$LAW_BOSS" ]] || fail "missing $LAW_BOSS"
[[ -f "$LAW_CP" ]] || fail "missing $LAW_CP"
[[ -f "$LAW_HEALTH" ]] || fail "missing $LAW_HEALTH"
[[ -f data/mac-law-mandatory-v1.json ]] || fail "missing SSOT"
[[ -f scripts/mac_law_mandatory_v1.py ]] || fail "missing script"
[[ -f .cursor/rules/mac-law-mandatory.mdc ]] || fail "missing cursor rule mac-law-mandatory.mdc"
[[ -f .cursor/rules/mac-control-plane.mdc ]] || fail "missing cursor rule mac-control-plane.mdc"

python3 scripts/mac_law_mandatory_v1.py --assess --json >/dev/null || fail "assess"

bash scripts/validate-mac-control-plane-v1.sh || fail "control plane sub-gate"
bash scripts/validate-mac-health-agent-mandates-v1.sh || fail "health mandates sub-gate"

RECEIPT="$HOME/.sina/mac-law-mandatory-receipt-v1.json"
if [[ -f "$RECEIPT" ]]; then
  python3 -c "import json,sys; r=json.load(open('$RECEIPT')); sys.exit(0 if r.get('ok') else 1)" \
    || fail "receipt not ok — run: python3 scripts/mac_law_mandatory_v1.py --sync-receipt --enforce --json"
fi

bash "$ROOT/scripts/mac_law_surfaces_boot_v1.sh" || fail "surfaces boot :8781/:8780"

echo "PASS: validate-mac-law-mandatory-v1"
