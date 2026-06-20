#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md
test -f brain-os/contract/BRAIN_HEAL_PROMPT_LOCKED_v1.md
test -f brain-os/INDEX_LOCKED_v1.md
test -f .cursor/rules/000-brain-unified.mdc
test -f scripts/brain_gather_rules_v1.py
test -d brain-os/plan-registry/sourcea-1000

for f in \
  .cursor/rules/000-brain-narrate-only.mdc \
  .cursor/rules/brain-not-worker.mdc \
  .cursor/rules/goal1-loop-activation.mdc \
  os/chat-handoffs/BRAIN_RUN_LOOP_SIMPLE_LOCKED_v1.md \
  os/chat-handoffs/BRAIN_NARRATE_NOT_EXECUTE_LOCKED_v1.md \
  os/chat-handoffs/BRAIN_TIMING_ENFORCEMENT_LOCKED_v1.md
do
  test ! -f "$f" || { echo "FAIL: sick rule still exists: $f"; exit 1; }
done

grep -q 'alwaysApply: true' .cursor/rules/000-brain-unified.mdc
grep -q 'brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md' scripts/cursor_entry_gate.py

python3 scripts/brain_gather_rules_v1.py --json | python3 -c "
import json,sys
g=json.load(sys.stdin)
assert g['healthy'] is True, g.get('deleted_sick_still_on_disk')
assert 'brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md' in g['ssot']
print('PASS: brain_gather healthy')
"

bash scripts/validate-brain-rules-narrate-v1.sh

echo "OK: validate-brain-unified-rules-v1"
