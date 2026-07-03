#!/usr/bin/env bash
# validate-machine-process-v1.sh — unified L14 + L16 + machine-process SSOT gate (LP-MACHINE-VALID)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RECEIPT="$ROOT/receipts/proof/machine-validation-latest-v1.json"
fail() { echo "FAIL: validate-machine-process-v1 — $*" >&2; exit 1; }

PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"
mkdir -p "$ROOT/receipts/proof"

STEPS=()
run_step() {
  local name="$1"; shift
  if "$@"; then
    STEPS+=("$name:PASS")
  else
    STEPS+=("$name:FAIL")
    fail "$name failed"
  fi
}

run_step L14_trigger_sweep bash "$ROOT/scripts/validate-trigger-registry-v1.sh"
run_step L16_governance bash "$ROOT/scripts/validate-github-automation-governance-v1.sh"

"$PY" -c "
import json
from pathlib import Path
root = Path('$ROOT')
loops = json.loads((root / 'data/machine-process-loops-v1.json').read_text())
retire = json.loads((root / 'data/founder-trigger-retirement-registry-v1.json').read_text())
assert loops.get('schema') == 'machine-process-loops-v1'
assert len(loops.get('loops', [])) >= 10
assert (root / 'docs/FOUNDER_CANON_v1.md').is_file()
assert (root / 'docs/MACHINE_LOOPS_v1.md').is_file()
assert (root / 'data/founder-trigger-ledger-v1.json').is_file()
assert retire.get('schema') == 'founder-trigger-retirement-registry-v1'
for loop in loops['loops']:
    for key in ('loop_id', 'entry_script', 'receipt_path'):
        assert loop.get(key), f'missing {key} in {loop.get(\"loop_id\")}'
    p = root / loop['entry_script']
    assert p.is_file(), f'missing script {loop[\"entry_script\"]}'
print('OK machine-process SSOT:', len(loops['loops']), 'loops ·', len(retire.get('triggers', [])), 'retirement rows')
" || fail "SSOT schema check"

AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
"$PY" -c "
import json
doc = {
  'schema': 'machine-validation-v1',
  'at': '$AT',
  'ok': True,
  'steps': [s for s in '''${STEPS[*]}'''.split()],
  'report_line': 'machine_validation PASS · L14 + L16 + SSOT green'
}
open('$RECEIPT','w').write(json.dumps(doc, indent=2)+'\n')
print(doc['report_line'])
"
echo "PASS: validate-machine-process-v1.sh"
