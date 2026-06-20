#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

test -f "$ROOT/brain-os/laws/BRAIN_SELF_HEAL_STARTUP_LOCKED_v1.md"
test -f "$ROOT/brain-os/laws/BRAIN_FAST_STARTUP_LOCKED_v1.md"
test -f "$ROOT/scripts/brain_self_heal_startup_v1.py"
test -f "$ROOT/scripts/brain_fast_startup_v1.py"
grep -q "run_self_heal_startup" "$ROOT/scripts/brain_run_loop_v1.py"
grep -q "brain_fast_startup_v1.py" "$ROOT/scripts/brain-session-start.sh"

export SINA_BRAIN_FAST=1
python3 "$ROOT/scripts/brain_self_heal_startup_v1.py" --caller validate_test --json-only | python3 -c "
import json,sys
row=json.load(sys.stdin)
assert row.get('schema')=='brain-self-heal-startup-v1', row
assert row.get('fast_brain') is True, row
assert 'steps' in row and len(row['steps'])>=4, row
print('fast_brain_steps:', len(row['steps']))
"

echo "OK: validate-brain-self-heal-startup-v1"
