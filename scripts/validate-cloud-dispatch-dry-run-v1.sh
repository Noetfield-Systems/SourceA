#!/usr/bin/env bash
# validate-cloud-dispatch-dry-run-v1.sh — offline dry-run contract for CLOUD-LD-001
set -euo pipefail
cd "$(dirname "$0")/.."

python3 scripts/cloud_worker_dispatch_v1.py --plan-id CLOUD-LD-001 --dry-run --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('ok') is True, r
assert r.get('dry_run') is True, r
assert r.get('schema')=='cloud-worker-dispatch-v1', r
assert r.get('plan_id')=='CLOUD-LD-001', r
print('OK: CLOUD-LD-001 dry-run schema')
"

echo "PASS: validate-cloud-dispatch-dry-run-v1"
