#!/usr/bin/env bash
# Smoke test: enqueue echo task → worker --once → verify execution_memory.jsonl
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"
cd "$ROOT/scripts"

python3 -c "
import json
import sys
from pathlib import Path

from execution_spine.queue import enqueue, init_db
from execution_spine.worker import process_one
from execution_spine.writer import read_memory, memory_stats

init_db()
task = enqueue(
    producer='validate-execution-spine',
    action_id='spine-smoke-echo',
    kind='shell',
    payload={'argv': ['echo', 'spine-ok'], 'cwd': str(Path.home()), 'timeout': 30},
    plan_id='P0-RUNRECEIPT',
)
out = process_one()
if not out or out.get('status') != 'success':
    print('FAIL: worker did not succeed', out)
    sys.exit(1)
rows = read_memory(task_id=task.task_id)
if not rows:
    print('FAIL: no memory row for', task.task_id)
    sys.exit(1)
stats = memory_stats()
print('PASS execution spine', json.dumps({'task_id': task.task_id, 'stats': stats}, indent=2))
"
