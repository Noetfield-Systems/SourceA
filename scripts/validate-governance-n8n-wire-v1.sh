#!/usr/bin/env bash
# validate-governance-n8n-wire-v1.sh — n8n governance + OpenRouter wire receipt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
FAIL=0

check() {
  if "$@"; then
    echo "PASS: $*"
  else
    echo "FAIL: $*"
    FAIL=1
  fi
}

check test -f "${ROOT}/n8n/workflows/wf-governance-fast-15m.stub.json"
check test -f "${ROOT}/n8n/workflows/wf-judge-audit-batch.stub.json"
check test -f "${ROOT}/n8n/workflows/wf-thread-scout-weekly.stub.json"
check test -f "${ROOT}/n8n/workflows/wf-openrouter-governance-hook.stub.json"
check test -f "${ROOT}/scripts/governance_n8n_openrouter_wire_v1.py"
check test -f "${SINA}/canvas-form-picks-applied-v1.json"
check python3 -c "
import json,sys
from pathlib import Path
p=Path.home()/'.sina/canvas-form-picks-applied-v1.json'
d=json.loads(p.read_text())
assert d.get('picks',{}).get('Q-GOV-FAST-WIRE-v1')=='A'
assert d.get('picks',{}).get('Q-CHANGE-QUORUM-v1')=='A'
"

if [[ -f "${SINA}/governance-n8n-openrouter-wire-v1.json" ]]; then
  check python3 -c "
import json
from pathlib import Path
d=json.loads(Path.home().joinpath('.sina/governance-n8n-openrouter-wire-v1.json').read_text())
assert d.get('ok') is True
assert 'wf-governance-fast-15m' in (d.get('n8n_workflows') or [])
"
else
  echo "WARN: governance-n8n-openrouter-wire-v1.json missing — run governance_n8n_openrouter_wire_v1.py"
fi

exit "$FAIL"
