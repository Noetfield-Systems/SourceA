#!/usr/bin/env bash
# validate-cloud-forge-run-hundred-rows-vocabulary-v1.sh — INCIDENT-043 law in repository
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }

LAW="$ROOT/brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_HUNDRED_ROWS_PER_TURN_TERMINOLOGY_LOCKED_v1.md"
INC="$ROOT/brain-os/incidents/SINA_CLOUD_FORGE_RUN_HUNDRED_ROWS_VOCABULARY_INCIDENT_043_LOCKED_v1.md"
SSOT="$ROOT/data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json"
RULE="$ROOT/.cursor/rules/037-cloud-forge-run-hundred-rows-per-turn-v1.mdc"
REG="$ROOT/brain-os/incidents/AGENT_INCIDENTS_REGISTRY_LOCKED_v1.md"

[[ -f "$LAW" ]] || fail "missing law $LAW"
[[ -f "$INC" ]] || fail "missing incident $INC"
[[ -f "$SSOT" ]] || fail "missing SSOT $SSOT"
[[ -f "$RULE" ]] || fail "missing cursor rule $RULE"

python3 -c "
import json, sys
from pathlib import Path
p = Path('$SSOT')
d = json.loads(p.read_text())
assert d.get('schema') == 'cloud-drain-hundred-rows-per-turn-vocabulary-v1' or d.get('schema') == 'cloud-forge-run-hundred-rows-per-turn-vocabulary-v1'
assert d.get('asf_order', {}).get('rows_per_turn_minimum') == 100
forbidden = d.get('forbidden_phrases') or []
assert 'up to 100' in forbidden
print('SSOT ok')
" || fail "SSOT schema check"

grep -q '\*\*043\*\*' "$REG" || fail "registry missing INCIDENT-043"
grep -q 'mandatory' "$LAW" || fail "law missing mandatory quota language"

MOTOR="$ROOT/data/cloud-motor-founder-vocabulary-v1.json"
python3 -c "
import json
from pathlib import Path
m = json.loads(Path('$MOTOR').read_text())
assert m['terms']['drain']['display_name'] == 'Cloud Forge Run'
assert m['terms']['loop']['display_name'] == 'Auto Runtime'
" || fail "cloud-motor-founder-vocabulary pairing"

FP="$ROOT/data/cloud-forge-run-full-pack-pattern-v1.json"
[[ -f "$FP" ]] || fail "missing $FP"

echo "OK: validate-cloud-forge-run-hundred-rows-vocabulary-v1"
