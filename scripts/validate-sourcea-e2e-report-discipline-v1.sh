#!/usr/bin/env bash
# Validate E2E report discipline — last report schema, log dir, weekly law in repository.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
LAST="${HOME}/.sina/sourcea-e2e-last-report-v1.json"
LOG_DIR="${HOME}/.sina/e2e-logs"
LAW="brain-os/law/enforcement/SOURCEA_E2E_WEEKLY_CHECKLIST_LOCKED_v1.md"
RUNNER="scripts/sourcea_e2e_run_v1.py"
FAIL=0

fail() { echo "FAIL: $*"; FAIL=1; }

echo "=== validate-sourcea-e2e-report-discipline-v1 ==="

[[ -f "$LAW" ]] || fail "missing $LAW"
[[ -f "$RUNNER" ]] || fail "missing $RUNNER"

python3 "$RUNNER" --read-last --json >/dev/null 2>&1 || fail "read-last failed"

if [[ -f "$LAST" ]]; then
  python3 -c "
import json, sys
from pathlib import Path
p = Path('$LAST')
row = json.loads(p.read_text())
if row.get('schema') != 'sourcea-e2e-last-report-v1':
    print('FAIL: bad schema', row.get('schema'))
    sys.exit(1)
if not row.get('next_agent_read'):
    print('FAIL: missing next_agent_read')
    sys.exit(1)
print('OK: last report', row.get('run_id'))
" || fail "last report schema"
else
  echo "OK: no last report yet (first run pending)"
fi

mkdir -p "$LOG_DIR"
[[ -d "$LOG_DIR" ]] || fail "cannot create $LOG_DIR"

if [[ $FAIL -eq 0 ]]; then
  echo "validate-sourcea-e2e-report-discipline-v1 PASS"
  exit 0
fi
exit 1
