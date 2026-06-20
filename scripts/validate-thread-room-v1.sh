#!/usr/bin/env bash
# validate-thread-room-v1.sh — E2E Thread Room pipeline smoke test
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
CHATS="58148ac9,6245d9dd,e54ddfa8"
python3 scripts/thread_room_run_v1.py --chats "$CHATS" --write-form --json 2>/dev/null | python3 -c "
import json,sys
from pathlib import Path
raw=sys.stdin.read(); j=json.loads(raw[raw.find('{'):])
c=j['curation']
assert c.get('schema')=='thread-room-curator-v1'
assert Path(j['receipt']['paths']['curation']).is_file()
assert Path.home().joinpath('.sina/thread-room/latest-scout-v1.json').is_file()
print('OK: validate-thread-room-v1 · case_id='+c.get('case_id','?'))
print('     arcs='+str(len(json.loads(Path(j[\"receipt\"][\"paths\"][\"map\"]).read_text()).get(\"arcs\",[]))))
"
