#!/usr/bin/env bash
# validate-mac-health-unattended-v1.sh — dry-run streak + Cursor auto-quit OFF
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
export PYTHONPATH="$ROOT/scripts:${PYTHONPATH:-}"
SINA="${HOME}/.sina"
CONFIG="${SINA}/config/mac-health-panic-v1.json"
fail=0

python3 -c "
import json
from pathlib import Path
p=Path('${CONFIG}')
if p.is_file():
    d=json.loads(p.read_text())
else:
    d={}
cur=(d.get('cursor') or {})
assert cur.get('auto_restart_on_unattended_panic') is not True, 'Cursor auto-quit must be false'
cpu=d.get('cpu_warn') or {}
if cpu.get('enabled') is False:
    print('WARN: cpu_warn disabled in panic config — enable in Mac Health Settings for CPU ladder')
else:
    print('PASS: cpu_warn enabled')
print('PASS: panic config — Cursor auto-quit off')
" || fail=1

python3 "$ROOT/scripts/test_mac_health_unattended_v1.py" --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ok'), d
if d.get('skipped'):
    print('PASS: unattended sim skipped (auto_panic off)')
else:
    assert d.get('dry_run') or d.get('receipt'), d
    print('PASS: unattended dry-run streak')
" || fail=1

if [[ "$fail" -eq 0 ]]; then
  echo "validate-mac-health-unattended-v1: PASS"
  exit 0
fi
echo "validate-mac-health-unattended-v1: FAIL"
exit 1
