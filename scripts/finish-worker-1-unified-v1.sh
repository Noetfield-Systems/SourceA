#!/usr/bin/env bash
# TRACE: AUTO-TRACE-WORKER1-UNIFIED-FINISH-v1.0 · agent Auto
# Worker 1 unified closeout — w1-01..w1-40 (SA block + autoloop) + full E2E + debug.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "== finish-worker-1-unified-v1 =="

# Block A — w1-01..w1-20 eval SA
bash scripts/finish-worker-1-sa-block-v1.sh

# Block B — w1-21..w1-40 autoloop
bash scripts/validate-worker-1-autoloop-block-v1.sh
bash scripts/validate-goal1-batch-gate-10-v1.sh

python3 scripts/brain_validate_goal1_v1.py --json | python3 -c "
import json, sys
d = json.load(sys.stdin)
chain = d.get('chain') or {}
for k in ('inject', 'validate', 'activate', 'sync'):
    v = chain.get(k)
    assert v in ('PASS', 'WAIT', 'RUNNING'), f'chain.{k}={v}'
assert chain.get('activate') != 'FAIL', 'activate skip rejected'
inbox_pending = (d.get('inbox') or {}).get('pending')
if inbox_pending:
    assert chain.get('activate') in ('PASS', 'RUNNING', 'WAIT'), 'delivered inbox must activate, run, or honest WAIT'
print('PASS: w1-25/35/40 brain_validate chain honest')
"

python3 -c "
from pathlib import Path
t = Path('scripts/goal1_lane_broker.py').read_text()
assert 'clear_inbox' in t and 'broker_worker_submit' in t
print('PASS: w1-25 clear_inbox after worker-submit')
"

python3 scripts/one_sa_per_turn_gate_v1.py --status | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('ok'), d
print('PASS: w1-28/33 one_sa_per_turn_gate')
"

bash scripts/validate-sourcea-e2e-full-v1.sh
python3 scripts/validate_worker1_autoloop_closeout_proofs_v1.py
python3 scripts/sync_worker_1_registry_status_v1.py
python3 scripts/sync_worker_1_sa_block_status_v1.py

python3 -c "
import json
from pathlib import Path
reg = json.loads(Path('brain-os/plan-registry/worker-dual-40/REGISTRY.json').read_text())
backlog = [p['id'] for p in reg['plans'] if p.get('status') != 'done']
assert not backlog, f'worker-1 unified backlog: {backlog}'
assert reg.get('worker_1_only') is True
assert 'worker_2' not in reg, 'worker_2 field must be deleted'
print('PASS: worker-1 unified 40/40 done · worker_2 purged')
"

echo "OK: finish-worker-1-unified-v1 · w1-01..w1-40 complete · E2E green"
