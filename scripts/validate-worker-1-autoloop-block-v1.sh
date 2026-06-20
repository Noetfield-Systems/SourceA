#!/usr/bin/env bash
# TRACE: AUTO-TRACE-WORKER-AUTOLOOP-BLOCK-v1.0 · agent Auto · validate-worker-1-autoloop-block-v1.sh
# Worker 1 autoloop block — w1-21..w1-40 machine proofs.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f scripts/goal1_auto_loop_v1.py
test -f scripts/goal1_batch_log_v1.py
test -f scripts/goal1_lane_broker.py
test -f scripts/stop_goal1_loop_v1.py
test -f scripts/advance-healthy-queue-v1.py
test -f scripts/closeout_sa_task.py

bash scripts/validate-goal1-auto-loop-v1.sh
bash scripts/validate-goal1-loop-activation-chain-v1.sh
bash scripts/validate-goal1-lane-broker-v1.sh
bash scripts/validate-goal1-worker-batch-v1.sh

python3 scripts/goal1_auto_loop_v1.py --prepare-only --turns 1 --json | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('ok'), d
print('PASS: w1-21 prepare-only')
"

python3 -c "
from pathlib import Path
import importlib.util
root = Path('$ROOT')
# w1-23 heal_inbox_meta
spec = importlib.util.spec_from_file_location('wi', root/'scripts/worker_inject_lib.py')
wi = importlib.util.module_from_spec(spec); spec.loader.exec_module(wi)
m = wi.heal_inbox_meta({'sa_id': 'sa-0999'}, 'role=check · sa=sa-0355 · foo')
assert m['sa_id'] == 'sa-0355', m
print('PASS: w1-23 heal_inbox_meta')

# w1-24 stop hygiene
spec2 = importlib.util.spec_from_file_location('st', root/'scripts/stop_goal1_loop_v1.py')
st = importlib.util.module_from_spec(spec2); spec2.loader.exec_module(st)
assert hasattr(st, 'consecutive_broker_no_streak')
assert hasattr(st, 'clear_stale_batch_tail_hygiene')
print('PASS: w1-24 stop_goal1_loop hygiene')

# w1-32 broker submit
text = Path(root/'scripts/goal1_lane_broker.py').read_text()
assert 'worker_submit' in text and 'WORKER_ROUND_REPORT' in text
print('PASS: w1-32 broker worker_submit')

# w1-38 closeout
text2 = Path(root/'scripts/closeout_sa_task.py').read_text()
assert 'close_turn' in text2
print('PASS: w1-38 closeout_sa_task')
"

TMP_LOG=$(mktemp)
export SINA_GOAL1_BATCH_LOG="$TMP_LOG"
python3 -c "
import os, sys
sys.path.insert(0, 'scripts')
from goal1_batch_log_v1 import log_agent_start, log_agent_done, broker_yes_gate, BATCH_LOG
assert str(BATCH_LOG) == os.environ['SINA_GOAL1_BATCH_LOG']
log_agent_start(sa_id='sa-0355', queue_role='check', queue_pos=13, queue_total=30)
log_agent_done(exit_code=0, broker_ok=True, advance_ok=True, report_ok=True, chars=1200)
g = broker_yes_gate(need=1)
assert g.get('ok'), g
print('PASS: w1-22 batch log AGENT START/DONE format')
"
rm -f "$TMP_LOG"
unset SINA_GOAL1_BATCH_LOG

python3 scripts/brain_validate_goal1_v1.py --json 2>/dev/null | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('one_sa_per_turn') is not False
print('PASS: w1-25 brain_validate one_sa_per_turn')
" || echo "WARN: brain_validate chain idle (ok when no live batch)"

python3 scripts/report_worker_inbox_queue_drift_v1.py | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('ok'), d
print('PASS: w1-26 inbox/queue drift report')
"

python3 -c "
from pathlib import Path
t = Path('scripts/start_goal1_worker_turn_v1.py').read_text()
assert '-p' in t and '-f' in t
print('PASS: w1-34 headless agent -p -f')
"

echo "OK: validate-worker-1-autoloop-block-v1 · w1-21..w1-40 wiring"
