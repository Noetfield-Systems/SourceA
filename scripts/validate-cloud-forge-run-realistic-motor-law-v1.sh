#!/usr/bin/env bash
# validate-cloud-forge-run-realistic-motor-law-v1.sh — INCIDENT-045 law in repository
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }

LAW="$ROOT/brain-os/law/enforcement/SOURCEA_CLOUD_FORGE_RUN_REALISTIC_MOTOR_LOCKED_v1.md"
INC="$ROOT/brain-os/incidents/SINA_CLOUD_FORGE_RUN_REALISTIC_MOTOR_SUPERSESSION_INCIDENT_045_LOCKED_v1.md"
SSOT="$ROOT/data/cloud-forge-run-realistic-motor-law-v1.json"
RUNTIME="$ROOT/data/cloud-auto-runtime-v1.json"
RULE="$ROOT/.cursor/rules/037-cloud-forge-run-hundred-rows-per-turn-v1.mdc"

[[ -f "$LAW" ]] || fail "missing law $LAW"
[[ -f "$INC" ]] || fail "missing incident $INC"
[[ -f "$SSOT" ]] || fail "missing SSOT $SSOT"
[[ -f "$RUNTIME" ]] || fail "missing runtime $RUNTIME"
[[ -f "$RULE" ]] || fail "missing cursor rule $RULE"

python3 -c "
import json
from pathlib import Path

ssot = json.loads(Path('$SSOT').read_text())
rt = json.loads(Path('$RUNTIME').read_text())
assert ssot.get('schema') == 'cloud-forge-run-realistic-motor-law-v1'
cap = int(ssot.get('motor', {}).get('rows_per_turn_cap') or 0)
assert cap == 10, cap
assert ssot.get('proof', {}).get('proof_gate_required') is True
assert int(rt.get('max_advance_per_tick') or 0) == 10
assert rt.get('mandatory_shipped_per_turn') is None
old = json.loads(Path('$ROOT/data/cloud-forge-run-hundred-rows-per-turn-vocabulary-v1.json').read_text())
assert old.get('superseded') is True
print('SSOT ok')
" || fail "SSOT schema check"

grep -q 'INCIDENT-045' "$LAW" || fail "law missing INCIDENT-045"
grep -q 'proof gate' "$LAW" || fail "law missing proof gate language"

MOTOR="$ROOT/data/cloud-motor-founder-vocabulary-v1.json"
python3 -c "
import json
from pathlib import Path
m = json.loads(Path('$MOTOR').read_text())
assert m['terms']['drain']['display_name'] == 'Cloud Forge Run'
assert m['terms']['loop']['display_name'] == 'Auto Runtime'
" || fail "cloud-motor-founder-vocabulary pairing"

FP="$ROOT/data/cloud-forge-run-full-pack-pattern-v1.json"
python3 -c "
import json
from pathlib import Path
fp = json.loads(Path('$FP').read_text())
assert int(fp.get('pattern', {}).get('max_advance_per_tick') or 0) == 10
" || fail "full-pack pattern cap"

echo "OK: validate-cloud-forge-run-realistic-motor-law-v1"
