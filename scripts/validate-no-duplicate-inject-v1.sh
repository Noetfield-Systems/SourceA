#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

test -f "$ROOT/brain-os/laws/NO_DUPLICATE_INJECT_LOCKED_v1.md"
test -f "$ROOT/scripts/duplicate_inject_guard_v1.py"
test -f "$ROOT/scripts/goal1_stuck_watchdog_v1.py"
grep -q "preflight_inject" "$ROOT/scripts/worker_inject_lib.py"
grep -q "run_stuck_watchdog" "$ROOT/scripts/auto_run_worker_batch_v1.py"
grep -q "INBOX_PENDING" "$ROOT/scripts/auto_run_worker_batch_v1.py"
grep -q "AWAITING_WORKER" "$ROOT/scripts/auto_run_worker_batch_v1.py"
grep -q "COOLDOWN_SEC = 90" "$ROOT/scripts/duplicate_inject_guard_v1.py"
grep -q "COOLDOWN_SAME_SA_ID" "$ROOT/scripts/duplicate_inject_guard_v1.py"
grep -q "SA_ALREADY_IN_CURSOR_QUEUE_TURN_BIND" "$ROOT/scripts/duplicate_inject_guard_v1.py"
grep -q "acquire_inject_lock" "$ROOT/scripts/duplicate_inject_guard_v1.py"
grep -q "check_skip_inject" "$ROOT/scripts/start_goal1_worker_turn_v1.py"

python3 -c "
import json, sys, tempfile
from pathlib import Path
sys.path.insert(0, '$ROOT/scripts')
from duplicate_inject_guard_v1 import check_skip_inject, acquire_inject_lock, COOLDOWN_SEC, TURN_BIND_JSON

meta = {'sa_id': 'sa-TEST', 'queue_role': 'check', 'queue_pos': 99, 'queue_total': 30}
acquire_inject_lock(meta=meta, source='validator')
skip = check_skip_inject(meta=meta, source='validator')
assert skip.get('skip'), skip
assert skip.get('reason') in ('COOLDOWN_SAME_SA_ID', 'COOLDOWN_SAME_TURN', 'SA_ALREADY_IN_CURSOR_QUEUE_TURN_BIND'), skip
assert COOLDOWN_SEC == 90
# turn-bind block when same turn still pending
TURN_BIND_JSON.write_text(json.dumps({'sa_id': 'sa-BIND', 'queue_role': 'act', 'queue_pos': 2}) + '\n')
from duplicate_inject_guard_v1 import INBOX_JSON
INBOX_JSON.write_text(json.dumps({'pending': True, 'meta': {'sa_id': 'sa-BIND', 'queue_role': 'act', 'queue_pos': 2}}) + '\n')
skip2 = check_skip_inject(meta={'sa_id': 'sa-BIND', 'queue_role': 'act', 'queue_pos': 2}, source='v2')
assert skip2.get('skip'), skip2
assert skip2.get('reason') == 'SA_ALREADY_IN_CURSOR_QUEUE_TURN_BIND', skip2
print('guard_ok skip=', skip.get('reason'), 'bind=', skip2.get('reason'))
# Cleanup validator artifacts — must not pollute live INBOX/pointer
from pathlib import Path
import json
home = Path.home() / '.sina'
for name in ('goal1-inject-lock-v1.json', 'goal1-worker-turn-bind-v1.json'):
    p = home / name
    if p.is_file():
        row = json.loads(p.read_text())
        if str(row.get('sa_id','')).lower() in ('sa-test', 'sa-bind'):
            p.unlink(missing_ok=True)
inbox = home / 'worker-prompt-inbox-v1.json'
if inbox.is_file():
    row = json.loads(inbox.read_text())
    meta = row.get('meta') or {}
    if str(meta.get('sa_id','')).lower() in ('sa-test', 'sa-bind') or row.get('pending') and 'sa-TEST' in str(row.get('prompt','')):
        row['pending'] = False
        row.pop('prompt', None)
        inbox.write_text(json.dumps(row, indent=2) + chr(10))
"

python3 "$ROOT/scripts/goal1_stuck_watchdog_v1.py" --caller validate --json >/dev/null

echo "OK: validate-no-duplicate-inject-v1 (sa-0720)"
