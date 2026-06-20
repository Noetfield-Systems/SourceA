#!/usr/bin/env bash
# validate-law-supersession-surfaces-v1.sh — CRITICAL: no stale forbidden phrases logged
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
python3 scripts/agent_memory_mirror_v1.py --validate --json | python3 -c "
import json,sys
v=json.load(sys.stdin)
if not v.get('ok'):
    print('FAIL: validate-law-supersession-surfaces-v1', file=sys.stderr)
    for x in v.get('violations') or []:
        print(f\"  {x['file']}: {x['label']}\", file=sys.stderr)
    for m in v.get('missing_always_rules') or []:
        print(f\"  missing rule: {m}\", file=sys.stderr)
    sys.exit(1)
print('OK: validate-law-supersession-surfaces-v1 · violations=0')
"
