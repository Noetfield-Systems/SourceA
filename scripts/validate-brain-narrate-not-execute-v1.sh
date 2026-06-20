#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f scripts/brain_narrate_loop_v1.py
test -f os/chat-handoffs/BRAIN_UNIFIED_RULES_LOCKED_v1.md

MSG='Run the loop step-by-step, narrating each action until we have a final answer.'
python3 scripts/brain_intent_gate_v1.py --message "$MSG" | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r['intent']=='RUN_TRACE', r
assert 'brain_run_loop_trace_v1.py' in r['mandatory_command']
"
python3 scripts/brain_intent_gate_v1.py --message 'narrate only watch' | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r['intent']=='NARRATE_ONLY', r
"

python3 scripts/brain_intent_gate_v1.py --set-narrate-lock >/dev/null
out=$(python3 scripts/goal1_auto_loop_v1.py --turns 1 --json 2>/dev/null || true)
echo "$out" | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('error')=='BRAIN_NARRATE_MODE', r
"
python3 scripts/brain_intent_gate_v1.py --clear-narrate-lock >/dev/null

grep -q 'brain_narrate_loop_v1.py' .cursor/rules/000-brain-unified.mdc
grep -q 'brain_narrate_loop_v1.py' os/chat-handoffs/BRAIN_UNIFIED_RULES_LOCKED_v1.md

echo "OK: validate-brain-narrate-not-execute-v1"
