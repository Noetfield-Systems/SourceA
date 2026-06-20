#!/usr/bin/env bash
# Master validator — L1→Brain pipeline + L2 Brain wire + unified sync receipt
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
errors=0

fail() { echo "FAIL: $*"; errors=$((errors + 1)); }

echo "== agentic layer wire sync =="
python3 "${ROOT}/scripts/agentic_layer_wire_sync_v1.py" --json --no-sync >/dev/null || fail "agentic_layer_wire_sync_v1.py"

echo "== pipeline v2 =="
bash "${ROOT}/scripts/validate-agentic-layer-pipeline-v2.sh" || fail "validate-agentic-layer-pipeline-v2"

echo "== L1→Brain pipeline =="
bash "${ROOT}/scripts/validate-l1-agent-pipeline-v1.sh" || fail "validate-l1-agent-pipeline-v1"
bash "${ROOT}/scripts/validate-brain-l2-wire-v1.sh" || fail "validate-brain-l2-wire-v1"

echo "== brain wire L1 cross-ref (after standalone refresh) =="
python3 "${ROOT}/scripts/brain_governance_wire_v1.py" --no-sync --json >/dev/null || fail "brain_governance_wire standalone"
python3 - <<'PY' "${SINA}/governance-brain-wire-v1.json" "${SINA}/l1-agent-pipeline-wire-v1.json"
import json, sys
wire = json.load(open(sys.argv[1]))
l1 = json.load(open(sys.argv[2]))
if not wire.get("l1_pipeline"):
    raise SystemExit("brain wire missing l1_pipeline after standalone run")
if not wire.get("l1_wired_to_brain"):
    raise SystemExit("brain wire missing l1_wired_to_brain")
if not wire.get("l1_pipeline", {}).get("present") and not l1.get("at"):
    raise SystemExit("l1 pipeline present flag false but file exists")
print("OK: brain wire preserves L1 cross-ref")
PY

echo "== truth bundle =="
python3 "${ROOT}/scripts/agent_truth_bundle_v1.py" --json | python3 -c "
import json, sys
b = json.load(sys.stdin)
if b.get('schema') != 'agent-truth-bundle-v1':
    raise SystemExit('bad truth bundle schema')
if not (b.get('brain_wire') or {}).get('ok'):
    raise SystemExit('truth bundle brain_wire not ok')
if not (b.get('l1_pipeline') or {}).get('ok'):
    raise SystemExit('truth bundle l1_pipeline not ok')
if not (b.get('agentic_pipeline_v2') or {}).get('ok'):
    raise SystemExit('truth bundle agentic_pipeline_v2 not ok')
print('OK: truth bundle brain_wire + l1_pipeline + pipeline_v2')
"

if [[ $errors -gt 0 ]]; then
  echo "FAIL: validate-agentic-layer-wire-v1 ($errors)"
  exit 1
fi
echo "OK: validate-agentic-layer-wire-v1 — L1 + L2 + cross-ref"
