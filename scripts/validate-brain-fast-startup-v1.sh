#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
test -f scripts/brain_fast_startup_v1.py
grep -q 'brain_fast_startup_v1.py' scripts/brain-session-start.sh
export SINA_BRAIN_FAST=1 SINA_COMMERCIAL_LOOP=1
python3 scripts/brain_fast_startup_v1.py --caller validate_test --json | python3 -c "
import json,sys
row=json.load(sys.stdin)
assert row.get('schema')=='brain-fast-startup-v1', row
assert row.get('ok') is True, row
# Warm receipt — second tick must stay fast (<3s)
row2=json.loads(__import__('subprocess').check_output(
    ['python3','scripts/brain_fast_startup_v1.py','--caller','validate_warm','--json'],
    text=True))
assert row2.get('ok') is True, row2
assert int(row2.get('elapsed_ms') or 0) < 3000, row2
h=row2.get('health') or {}
assert h.get('healthy') is True, row2
assert (h.get('wise') or {}).get('do_now'), row2
print('OK: validate-brain-fast-startup-v1 · warm', row2.get('elapsed_ms'), 'ms · health', h.get('score'))
"
