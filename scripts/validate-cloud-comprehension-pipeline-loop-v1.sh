#!/usr/bin/env bash
# validate-cloud-comprehension-pipeline-loop-v1.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

test -f data/cloud-comprehension-pipeline-loop-v1.json || { echo "FAIL missing SSOT"; exit 1; }
test -f scripts/cloud_comprehension_pipeline_loop_v1.py || { echo "FAIL missing script"; exit 1; }
test -f .cursor/rules/030-cloud-comprehension-pipeline-loop-v1.mdc || { echo "FAIL missing rule 030"; exit 1; }

GOOD='You asked why email stays off. WitnessBC public site still shows old journalism copy, so outbound email stays blocked until prod DNS switches. TrustField and Noetfield load fine.'
OUT=$(python3 scripts/cloud_comprehension_pipeline_loop_v1.py --text "$GOOD" --founder-message "why is email deferred" --json)
echo "$OUT" | python3 -c "import json,sys; r=json.load(sys.stdin); assert r.get('output_verdict')=='ACCEPT', r; print('OK: ACCEPT good text')"
test -f "${SINA}/cloud-comprehension-pipeline-loop-receipt-v1.json" || { echo "FAIL missing receipt"; exit 1; }
test -f "${SINA}/agent-output-quality-log-v1.jsonl" || { echo "FAIL missing output log"; exit 1; }

BAD='sites=RED; defer flag ON; gate PASS; wired.'
BAD_VERDICT=$(python3 scripts/cloud_comprehension_pipeline_loop_v1.py --text "$BAD" --founder-message "why defer" --json 2>/dev/null | python3 -c "import json,sys; r=json.load(sys.stdin); print(r.get('output_verdict','')); exit(0 if r.get('output_verdict') in ('RETURN_TO_AGENT','FIX_DISK','FIX_MACHINES') else 1)")
echo "OK: blocked bad parrot text ($BAD_VERDICT)"

grep -q 'cloud_comprehension_pipeline_loop' scripts/agentic_conduct_gate_v1.py || { echo "FAIL conduct gate not wired"; exit 1; }
grep -q 'comprehension_pipeline' scripts/agent_memory_mirror_v1.py || { echo "FAIL mirror not wired"; exit 1; }
grep -q 'comprehension' scripts/agent_session_gate_run_v1.py || { echo "FAIL session gate not wired"; exit 1; }
grep -q 'comprehension_line' scripts/disk_live_wire_sync_v1.py || { echo "FAIL live wire not wired"; exit 1; }

grep -q 'output_analyst' scripts/cloud_comprehension_pipeline_loop_v1.py || { echo "FAIL analyst missing"; exit 1; }
grep -q 'FIX_DISK' scripts/agentic_conduct_gate_v1.py || { echo "FAIL conduct FIX_DISK not wired"; exit 1; }

python3 - <<'PY'
import json
from pathlib import Path
ssot = json.loads(Path("data/cloud-comprehension-pipeline-loop-v1.json").read_text())
assert ssot.get("output_analyst", {}).get("root_causes"), "missing analyst root_causes"
print("OK: analyst SSOT")
PY

python3 - <<'PY'
import json
from pathlib import Path
b = json.loads(Path("data/agent-behavior-settings-v1.json").read_text())
if not b.get("cloud_comprehension_pipeline_loop", {}).get("active"):
    raise SystemExit("behavior settings cloud_comprehension_pipeline_loop not active")
print("OK: behavior settings")
PY

echo "PASS: validate-cloud-comprehension-pipeline-loop-v1"
