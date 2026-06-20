#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

test -f brain-os/scripts/brain_run_loop_v1.py
test -f brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md

python3 -c "
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location('brl', Path('brain-os/scripts/brain_run_loop_v1.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

sync = {'ok': True, 'json': {'path': '/api/hub-sync', 'built_at': '2026-01-01T00:00:00Z'}}
assert m._compact_sync(sync)['path'] == '/api/hub-sync'

steps = [
    {'id': 'sync', 'what': 'test', 'ok': True},
    {'id': 'activate', 'what': 'spawn', 'ok': True, 'pid': 42},
]
t = m._trace(steps, 'run the loop', activate={'pid': 42, 'log_path': '/tmp/x.log'}, validation={'chain': {'inject': 'PASS'}}, ok=True)
assert t['status'] == 'BRAIN_LOOP_TRACE'
yaml = m._to_yaml(t)
assert 'status: BRAIN_LOOP_TRACE' in yaml
assert len(yaml) < 4000
print('PASS: BRAIN_LOOP_TRACE compact shape')
"

echo "OK: validate-brain-run-loop-v1"
