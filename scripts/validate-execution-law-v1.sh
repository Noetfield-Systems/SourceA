#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

test -f "$ROOT/brain-os/laws/SOURCEA_EXECUTION_LAW_LOCKED_v1.md"
test -f "$ROOT/scripts/execution_law_enforce_v1.py"
grep -q "SOURCEA_EXECUTION_LAW" "$ROOT/scripts/cursor_entry_gate.py"
grep -q "execution_law_enforce" "$ROOT/scripts/claude_code_agent_v1.py"

python3 "$ROOT/scripts/execution_law_enforce_v1.py" --sa sa-0161 --phase phase-s1-eval-dispatch --caller validate --json | python3 -c "
import sys,json; r=json.load(sys.stdin); assert r.get('allowed'), r; print('allow_ok', r.get('validation_passed'))
"

python3 "$ROOT/scripts/execution_law_enforce_v1.py" --sa sa-0501 --phase phase-s5-commercial-lanes --caller validate --json | python3 -c "
import sys,json; r=json.load(sys.stdin); assert not r.get('allowed'), r; print('refuse_ok', r.get('status'))
"

echo "OK: validate-execution-law-v1"
