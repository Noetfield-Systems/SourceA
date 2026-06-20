#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

test -f brain-os/scripts/brain_narrate_loop_v1.py
test -f brain-os/scripts/brain_timing_enforce_v1.py
test -f brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md

start=$(date +%s)
out=$(python3 brain-os/scripts/brain_narrate_loop_v1.py)
end=$(date +%s)
elapsed=$((end - start))

echo "$out" | grep -q 'status: BRAIN_NARRATE_LOOP'
echo "$out" | grep -q 'final_answer:'
echo "$out" | grep -q 'timing:'
echo "$out" | grep -q 's/[0-9]*s):'
test -f ~/.sina/brain-narrate-loop-v1.json
test "$elapsed" -lt 75

python3 -c "
import json
from pathlib import Path
r = json.loads(Path.home().joinpath('.sina/brain-narrate-loop-v1.json').read_text())
t = r.get('timing_enforcement') or {}
assert 'step_limits_sec' in t, t
assert t.get('total_limit_sec') == 60
for s in json.loads(Path.home().joinpath('.sina/brain-loop-watch-v1.json').read_text()).get('steps', []):
    assert 'limit_sec' in s and 'elapsed_sec' in s, s.get('gate')
print('PASS: per-step timing fields present')
"

echo "OK: validate-brain-narrate-loop-v1 (${elapsed}s)"
