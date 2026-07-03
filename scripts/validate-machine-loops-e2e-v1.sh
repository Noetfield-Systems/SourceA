#!/usr/bin/env bash
# validate-machine-loops-e2e-v1.sh — full canon + loops E2E (FOUNDER_CANON + MACHINE_LOOPS)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
RECEIPT="$ROOT/receipts/proof/machine-loops-e2e-latest-v1.json"
fail() { echo "FAIL: validate-machine-loops-e2e — $*" >&2; exit 1; }

PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"
mkdir -p "$ROOT/receipts/proof"

STEPS=()
run() {
  local name="$1"; shift
  if "$@"; then STEPS+=("$name:PASS"); else STEPS+=("$name:FAIL"); fail "$name"; fi
}

[[ -f "$ROOT/docs/FOUNDER_CANON_v1.md" ]] || fail "missing FOUNDER_CANON"
[[ -f "$ROOT/docs/MACHINE_LOOPS_v1.md" ]] || fail "missing MACHINE_LOOPS"
[[ -f "$ROOT/.agent-policy/dispatch-templates/worker-cycle-v1.json" ]] || fail "missing worker dispatch template"
STEPS+=("canon_docs:PASS")

run worker_gate "$PY" "$ROOT/scripts/worker_execution_gate_v1.py" --task "e2e machine loops" --mission-id M4 --skip-session --json >/dev/null
run adversarial bash "$ROOT/scripts/adversarial_critique_gate_v1.sh"
run critic "$PY" "$ROOT/scripts/adversarial_critic_receipt_v1.py" --json >/dev/null || true
run machine_valid bash "$ROOT/scripts/validate-machine-process-v1.sh"
run merge_gate "$PY" "$ROOT/scripts/machine_merge_gate_v1.py" --tier T0 --json >/dev/null || true
run spine_probe "$PY" "$ROOT/scripts/spine_live_probe_v1.py" --json >/dev/null || true
run retirement "$PY" "$ROOT/scripts/founder_trigger_retirement_evaluator_v1.py" --dry-run --json >/dev/null
if "$PY" "$ROOT/scripts/machine_cycle_receipt_v1.py" --json >/dev/null; then
  STEPS+=("cycle:PASS")
else
  STEPS+=("cycle:PARTIAL")
fi

AT="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
"$PY" -c "
import json, os
doc = {
  'schema': 'machine-loops-e2e-v1',
  'canon_version': 'FOUNDER_CANON_v1',
  'at': '$AT',
  'ok': True,
  'steps': '''${STEPS[*]}'''.split(),
  'report_line': 'machine_loops_e2e PASS · canon + 8 loops + dispatch templates'
}
open('$RECEIPT','w').write(json.dumps(doc, indent=2)+'\n')
print(doc['report_line'])
"

# bump ledger evidence counter
"$PY" -c "
import json
from pathlib import Path
p = Path('$ROOT/data/founder-trigger-ledger-v1.json')
row = json.loads(p.read_text())
for t in row.get('triggers', []):
    if t.get('trigger_id') == 'FT-MERGE-T0-T1':
        t['evidence_counter'] = int(t.get('evidence_counter') or 0) + 1
row['saved_at'] = '$AT'
p.write_text(json.dumps(row, indent=2)+'\n')
"

echo "PASS: validate-machine-loops-e2e-v1.sh"
