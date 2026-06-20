#!/usr/bin/env bash
# CRITICAL — state machine + scheduler + kernel bind
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

python3 -c "
from execution_state_machine import apply_transition, contract_export
c = contract_export()
assert c['schema'] == 'execution-state-machine-v1'
assert 'queued' in c['states']
bad = apply_transition(from_state='done', to_state='running', task_id='test')
assert not bad.ok, bad
good = apply_transition(from_state='queued', to_state='scheduled', task_id='test')
assert good.ok
print('OK: state machine contract')
"

python3 -c "
import json
from pathlib import Path
p = Path.home() / '.sina' / 'execution_state_hub.json'
if p.is_file():
    h = json.loads(p.read_text())
    h['running'] = {}
    for row in (h.get('tasks') or {}).values():
        if row.get('state') in ('running', 'scheduled', 'verifying'):
            row['state'] = 'queued'
    p.write_text(json.dumps(h, indent=2) + '\n')
"

out=$(python3 execution_scheduler.py --next --lane sourcea 2>&1)
python3 -c "
import json, sys
d=json.loads(sys.argv[1])
assert d.get('ok'), d
assert d.get('task_id'), d
print('OK: scheduler next', d['task_id'])
" "$out"

kout=$(python3 execution_kernel_v0.py --tick --lane sourcea --dry-run 2>&1)
python3 -c "
import json, sys
d=json.loads(sys.argv[1])
assert d.get('ok'), d
assert d.get('next_task_id'), d
assert d.get('scheduled'), d
assert d.get('schema') == 'execution-kernel-v1'
print('OK: kernel v1 tick', d['next_task_id'])
" "$kout"

python3 -c "
import json, subprocess, sys
from pathlib import Path
sys.path.insert(0, '.')
from execution_state_hub import mark_running, mark_verifying, mark_failed

tid = 'spine-v1-verify-test'
lane = 'sourcea'
hub_path = Path.home() / '.sina' / 'execution_state_hub.json'
hub = json.loads(hub_path.read_text()) if hub_path.is_file() else {'tasks': {}, 'running': {}}
hub.setdefault('tasks', {})[tid] = {'state': 'scheduled', 'lane': lane}
hub['running'] = {}
hub_path.parent.mkdir(parents=True, exist_ok=True)
hub_path.write_text(json.dumps(hub, indent=2) + '\n')

r = mark_running(lane=lane, task_id=tid)
assert r.get('ok'), r
v = mark_verifying(lane=lane, task_id=tid)
assert v.get('ok'), v
assert v.get('status') == 'verifying'
f = mark_failed(lane=lane, task_id=tid, reason='validator mock')
assert f.get('ok'), f
hub = json.loads(hub_path.read_text())
assert hub['tasks'][tid]['state'] == 'failed'
hub['tasks'].pop(tid, None)
hub_path.write_text(json.dumps(hub, indent=2) + '\n')
print('OK: verifying transition path')
"

echo "OK: validate-execution-spine-v1 · SM + scheduler + kernel bound"
