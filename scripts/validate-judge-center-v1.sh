#!/usr/bin/env bash
# validate-judge-center-v1.sh — E2E Judge Center pipeline smoke test
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

CHATS="6245d9dd,e54ddfa8"
python3 scripts/judge_center_run_v1.py --chats "$CHATS" --write-form --json 2>/dev/null | python3 -c "
import json,sys
raw=sys.stdin.read()
start=raw.find('{')
j=json.loads(raw[start:])
judgment=j['judgment']
from pathlib import Path
assert judgment.get('schema')=='judge-center-bench-v1'
assert Path(j['receipt']['paths']['latest_resolution']).is_file()
print('OK: validate-judge-center-v1 · case_id='+judgment.get('case_id','?'))
ts=judgment['summary'].get('temporal_summary',{})
assert 'past_stale_only' in ts or 'trusted' in ts, 'missing temporal_summary'
print('     temporal trusted='+str(len(ts.get('trusted',[])))+' past_only='+str(len(ts.get('past_stale_only',[])))+' active='+str(len(ts.get('active_stale',[])))+' bad='+str(len(ts.get('bad',[]))))
"
