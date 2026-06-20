#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f scripts/goal1_auto_run_deliver_v1.py
test -f scripts/goal1_auto_run_v1.py

python3 scripts/goal1_auto_run_deliver_v1.py --prepare-only --turns 1 --json | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('ok'), d
assert d.get('step') == 'prepared', d
print('PASS: prepare-only deliver path')
"

echo "OK: validate-goal1-auto-run-v1"
