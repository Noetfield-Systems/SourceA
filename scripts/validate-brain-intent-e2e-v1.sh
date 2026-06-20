#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
fail() { echo "FAIL: validate-brain-intent-e2e-v1 — $*" >&2; exit 1; }

test -f "$ROOT/brain-os/law/BRAIN_RULE_COLLISION_MATRIX_LOCKED_v1.md"
grep -q "AUDIT_CHEAP_E2E" "$ROOT/brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md" || fail "BRAIN_UNIFIED §0.5"
grep -q "brain_intent_gate" "$ROOT/scripts/brain-session-start.sh" || fail "session-start intent"

python3 -c "
import json, subprocess, sys
from pathlib import Path
root = Path('$ROOT')
msg = 'check everything e2e'
raw = subprocess.check_output(
    [sys.executable, str(root / 'scripts' / 'brain_intent_gate_v1.py'), '--message', msg],
    text=True,
)
row = json.loads(raw)
assert row.get('intent') == 'AUDIT_CHEAP_E2E', row
forbidden = row.get('forbidden_commands') or []
assert any('fast-ladder' in f for f in forbidden), forbidden
allowed = row.get('allowed_commands') or []
assert any('preflight' in a for a in allowed), allowed
assert row.get('max_shell_seconds') == 90, row
print('PASS: AUDIT_CHEAP_E2E intent')
"

python3 "$ROOT/scripts/brain_intent_gate_v1.py" --message "check everything e2e" --write >/dev/null
python3 "$ROOT/scripts/brain_session_guard_v1.py" --json | python3 -c "
import json,sys
g=json.load(sys.stdin)
assert g.get('brain_intent',{}).get('intent')=='AUDIT_CHEAP_E2E', g.get('brain_intent')
print('PASS: guard reads intent receipt')
"

echo "OK: validate-brain-intent-e2e-v1"
