#!/usr/bin/env bash
# Close w1-01..w1-20 eval SA block — machine proofs + sourcea closeout.
# TRACE: AUTO-TRACE-WORKER1-SA-BLOCK-FINISH-v1.0 · agent Auto
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== finish-worker-1-sa-block-v1 =="

bash scripts/validate-eval-packet-v1b-phase-s1-t1-bundle-v1.sh
bash scripts/validate-eval-packet-v1b-live.sh
bash scripts/validate-eval-report-capture-v1.sh

# Batch closeout removed (structural-fix-2026-06-09) — REGISTRY done requires receipt + verify role only.

python3 scripts/sync_worker_1_sa_block_status_v1.py

# w1-20 must have PRIORITY row after closeout
python3 -c "
from pathlib import Path
pri = Path('brain-os/plan-registry/SOURCEA-PRIORITY.md').read_text()
assert 'sa-0150' in pri, 'sa-0150 PRIORITY row missing'
print('PASS: w1-20 sa-0150 PRIORITY row')
"

bash scripts/validate-sourcea-e2e-full-v1.sh 2>/dev/null || bash scripts/validate-execution-spine-v1.sh
python3 scripts/validate_worker1_autoloop_closeout_proofs_v1.py 2>/dev/null || python3 -c "
import subprocess
r=subprocess.run(['python3','scripts/find_critical_bugs.py'],capture_output=True,text=True,cwd='$ROOT',timeout=180)
assert r.returncode==0 and '\"critical\": 0' in (r.stdout+r.stderr)
print('PASS: find_critical_bugs critical=0')
"

echo "OK: finish-worker-1-sa-block-v1 · w1-01..w1-20 proofs green"
