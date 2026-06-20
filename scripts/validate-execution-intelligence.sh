#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
export PATH="/opt/homebrew/bin:/usr/local/bin:/Library/Frameworks/Python.framework/Versions/Current/bin:${PATH:-/usr/bin:/bin}"
cd "$ROOT/scripts"

python3 -c "
from execution_intelligence.feedback_loop import run_feedback_loop
from execution_intelligence.planner_influence import planner_context_block, influence_task_priority

r = run_feedback_loop(force=True)
assert r.get('ok'), r
assert r.get('patterns_count', 0) >= 0
ctx = planner_context_block()
assert 'execution_intelligence' in ctx
ranked = influence_task_priority(['pos-status', 'pos-dispatch', 'pos-run'])
assert ranked
print('PASS execution intelligence', 'patterns', r.get('patterns_count'), 'decisions', r.get('decisions_total'))
"
