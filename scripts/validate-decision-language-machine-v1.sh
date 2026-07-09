#!/usr/bin/env bash
# Light check — decision language machine v1 consume-only (Mac founder session safe)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/decision_language_machine_v1.py --fixture form_official_80 --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('ok'), r
assert r.get('mode')=='consume_only', r
assert r['mapped_count']+r['excluded_count']==r['raw_count']
assert r['cluster_count']==12
assert r['mapped_count']==22
assert r['excluded_count']==58
assert r.get('sg_canon_authority')=='SG'
assert r.get('apply_map_written') is False
print('PASS decision-language-machine-v1 consume-only')
"
python3 -c "
import sys
sys.path.insert(0,'scripts')
from live_founder_decision_form_v1 import all_open_questions
n=len(all_open_questions())
assert n==58, f'open_remaining expected 58 got {n}'
print('PASS open_remaining=58')
"
