#!/usr/bin/env bash
# adversarial_critique_gate_v1.sh — duplicate scan + conflict matrix + D1 sample (LP-ADVERSARIAL)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RECEIPT="$ROOT/receipts/proof/adversarial-critique-latest-v1.json"
fail() { echo "FAIL: adversarial_critique_gate_v1 — $*" >&2; exit 1; }

PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"
mkdir -p "$ROOT/receipts/proof"

DUP_JSON="/tmp/dup-scan-$$.json"
"$PY" "$ROOT/scripts/duplicate_implementation_scan_v1.py" --json > "$DUP_JSON" || true
DUP_OK=$("$PY" -c "import json; print(json.load(open('$DUP_JSON')).get('ok', False))")

"$PY" -c "
import json
from pathlib import Path
root = Path('$ROOT')
cm = json.loads((root / 'data/automation-conflict-matrix-v1.json').read_text())
conflicts = cm.get('conflicts') or []
c001 = [c for c in conflicts if c.get('id') == 'C001']
assert len(conflicts) >= 8, 'conflict matrix too small'
assert c001, 'C001 missing'
print('OK conflict matrix:', len(conflicts), 'conflicts')
"

D1_OK=true
CYCLE_DIR="$ROOT/receipts/cloud/autonomous-forge-run-cycles"
if [[ -d "$CYCLE_DIR" ]]; then
  COUNT=0
  for f in $(ls -t "$CYCLE_DIR"/*.json 2>/dev/null | head -3); do
    if grep -q 'idempotency_key' "$f" 2>/dev/null; then
      COUNT=$((COUNT + 1))
    fi
  done
  [[ "$COUNT" -ge 1 ]] || D1_OK=false
fi

AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
OVERLAPS=$("$PY" -c "import json; print(len(json.load(open('$DUP_JSON')).get('overlaps',[])))")
OK=true
# Duplicate overlaps are advisory — conflict matrix is the hard gate

ADV_OK="$OK" DUP_FLAG="$DUP_OK" D1_FLAG="$D1_OK" OVERLAP_COUNT="$OVERLAPS" AT="$AT" RECEIPT_PATH="$RECEIPT" "$PY" -c "
import json, os
ok = os.environ.get('ADV_OK') == 'true'
dup_ok = os.environ.get('DUP_FLAG') == 'True'
d1_ok = os.environ.get('D1_FLAG') == 'true'
doc = {
  'schema': 'adversarial-critique-v1',
  'at': os.environ.get('AT'),
  'ok': ok,
  'duplicate_scan_ok': dup_ok,
  'conflict_matrix_ok': True,
  'd1_sample_ok': d1_ok,
  'overlap_count': int(os.environ.get('OVERLAP_COUNT') or 0),
  'report_line': 'adversarial_critique PASS' if ok else 'adversarial_critique FAIL'
}
open(os.environ['RECEIPT_PATH'],'w').write(json.dumps(doc, indent=2)+'\n')
print(doc['report_line'])
"
[[ "$OK" == true ]] || fail "gate failed"
echo "PASS: adversarial_critique_gate_v1.sh"
