#!/usr/bin/env bash
# Light check — factory runtime spike dry-run (Mac founder session safe)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SPIKE="$ROOT/apps/factory-runtime-spike"
PY="$SPIKE/factory_runtime_spike/dry_run_v1.py"

if ! python3 -c "import langgraph" 2>/dev/null; then
  echo "SKIP: langgraph not installed — pip install -r apps/factory-runtime-spike/requirements.txt"
  exit 0
fi

python3 "$PY" --fixture pureflow --json --no-write | python3 -c "
import json, sys
row = json.load(sys.stdin)
if not row.get('ok'):
    print('FAIL: pureflow fixture', row.get('verdict'), row.get('status'))
    sys.exit(1)
print('OK: factory-runtime-spike dry-run PASS', row.get('job_id'))
"

python3 "$PY" --fixture bad --json --no-write > /tmp/factory-spike-bad.json || true
python3 -c "
import json
row = json.load(open('/tmp/factory-spike-bad.json'))
if row.get('ok'):
    print('FAIL: bad fixture should BLOCK')
    raise SystemExit(1)
print('OK: bad fixture BLOCK as expected')
"

python3 "$PY" --fixture pureflow --embed maf --json --no-write 2>/dev/null | python3 -c "
import json, sys
row = json.load(sys.stdin)
if not row.get('ok') or row.get('runtime_embed') != 'maf-hybrid-v1':
    print('FAIL: maf embed', row.get('verdict'), row.get('runtime_embed'))
    sys.exit(1)
rec = row.get('receipt') or {}
if rec.get('maf_pattern') != 'factory-job-fanout-gate-v1':
    print('FAIL: maf_pattern', rec.get('maf_pattern'))
    sys.exit(1)
print('OK: maf-hybrid embed PASS', row.get('job_id'))
"

echo "validate-factory-runtime-spike-v1.sh: ALL PASS"
