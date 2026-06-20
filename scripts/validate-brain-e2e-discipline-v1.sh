#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
fail() { echo "FAIL: validate-brain-e2e-discipline-v1 — $*" >&2; exit 1; }

test -f "$ROOT/brain-os/contract/BRAIN_E2E_EXECUTOR_PASTE_LOCKED_v1.md"
test -f "$ROOT/brain-os/incidents/SINA_BRAIN_E2E_RETRY_STORM_INCIDENT_026_LOCKED_v1.md"
test -f "$ROOT/scripts/factory_idle_gate_v1.py"
grep -q -- "--require-idle" "$ROOT/scripts/validate-e2e-fast-ladder-v1.sh" || fail "ladder missing --require-idle"
grep -q "validate-e2e-fast-ladder-v1.sh" "$ROOT/scripts/brain_session_guard_v1.py" || fail "guard must mention ladder"
grep -q "FORBIDDEN" "$ROOT/scripts/brain_session_guard_v1.py" || fail "guard forbidden list"
python3 -c "
from pathlib import Path
import importlib.util
import sys
spec = importlib.util.spec_from_file_location('guard', Path('$ROOT/scripts/brain_session_guard_v1.py'))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
row = mod.build_guard()
forbidden = row.get('forbidden_in_brain_chat') or []
assert 'validate-e2e-fast-ladder-v1.sh' in forbidden, forbidden
allowed = row.get('allowed_brain_shells') or []
assert not any('fast-ladder' in a for a in allowed), allowed
assert row.get('factory_idle') is not None
assert 'preflight' in ' '.join(allowed)
print('PASS: brain_session_guard discipline')
"

grep -q "INCIDENT-026" "$ROOT/.cursor/rules/000-brain-unified.mdc" || fail "brain-unified INCIDENT-026"
grep -q "validate-e2e-fast-ladder" "$ROOT/brain-os/enforcement/BRAIN_NO_FULL_E2E_SHELL_LOCKED_v1.md" || fail "BRAIN_NO_FULL_E2E"
grep -q "BRAIN_E2E_EXECUTOR_PASTE" "$ROOT/brain-os/contract/MANDATORY_BRAIN_CHAT_LOCKED_v1.md" \
  || grep -q "BRAIN_E2E_EXECUTOR_PASTE" "$ROOT/brain-os/entry/MANDATORY_READ_BY_ROLE_LOCKED_v1.md" \
  || fail "MANDATORY_READ missing paste pointer"

echo "OK: validate-brain-e2e-discipline-v1"
