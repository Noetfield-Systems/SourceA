#!/usr/bin/env bash
# validate-hub-judge-alarm-strip-v1.sh — Hub alarm strip P0–P3 smoke test
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

python3 scripts/hub_judge_alarm_strip_v1.py --json 2>/dev/null | python3 -c "
import json,sys
from pathlib import Path
raw=sys.stdin.read(); j=json.loads(raw[raw.find('{'):])
assert j.get('schema')=='hub-judge-alarm-strip-v1'
assert j.get('ok') is True
levels={x['level']:x for x in j.get('levels',[])}
for lv in ('P0','P1','P2','P3'):
    assert lv in levels, f'missing {lv}'
p=Path.home()/'.sina/judge-center/latest-alarm-strip-v1.json'
assert p.is_file(), 'missing latest-alarm-strip-v1.json'
print('OK: validate-hub-judge-alarm-strip-v1 · headline='+j.get('headline','?'))
print('     P0='+str(levels['P0']['count'])+' P1='+str(levels['P1']['count'])+' P2='+str(levels['P2']['count'])+' P3='+str(levels['P3']['count']))
"

python3 -c "
import sys
sys.path.insert(0,'scripts')
from hub_home_founder_view_v1 import hub_home_founder_payload
p=hub_home_founder_payload()
strip=p.get('judge_alarm_strip') or {}
assert strip.get('schema')=='hub-judge-alarm-strip-v1', 'hub_home missing judge_alarm_strip'
print('OK: hub_home_founder_view wires judge_alarm_strip')
"
