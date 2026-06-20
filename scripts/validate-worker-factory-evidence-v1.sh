#!/usr/bin/env bash
# Worker factory evidence gate validator
# Law: WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"
LAW="$ROOT/brain-os/law/enforcement/WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md"
PTR="$ROOT/WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md"
RULE="$ROOT/.cursor/rules/098-worker-full-round-evidence.mdc"
GATE="worker_factory_evidence_gate_v1.py"

for f in "$LAW" "$PTR" "$GATE"; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f"; exit 1; }
done
[[ -f "$RULE" ]] || { echo "FAIL: missing cursor rule 098-worker-full-round-evidence.mdc"; exit 1; }

python3 -c "
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('g', Path('worker_factory_evidence_gate_v1.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
# turn-open without inbox should still be detectable
r = m.run_factory_gate(caller='validate', require_inbox=False)
assert 'reasons' in r
tpl = m.check_reply_template('status: WORKER_ROUND_REPORT\nround_type: verify\nRECIPE: x\nVALIDATION: y\nEVIDENCE: z\nBUILT: no')
assert tpl.get('ok') is True
bad = m.check_reply_template('status: WORKER_ROUND_REPORT\nround_type: verify\nsummary: only yaml')
assert bad.get('ok') is False
print('OK: worker_factory_evidence_gate_v1 unit checks')
"

# Gatekeeper must import factory gate (wired)
grep -q 'worker_factory_evidence_gate_v1' gatekeeper_v1.py || {
  echo "FAIL: gatekeeper_v1.py not wired to factory gate"
  exit 1
}
grep -q 'worker_factory_evidence_gate_v1' start_goal1_worker_turn_v1.py || {
  echo "FAIL: start_goal1_worker_turn_v1.py not wired"
  exit 1
}
grep -q 'WORKER_FULL_ROUND_EVIDENCE_ENFORCEMENT_LOCKED_v1.md' cursor_entry_gate.py || {
  echo "FAIL: cursor_entry_gate worker chain missing law"
  exit 1
}

echo "OK: validate-worker-factory-evidence-v1"
