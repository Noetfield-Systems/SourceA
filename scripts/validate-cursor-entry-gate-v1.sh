#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
errors=0

need() { [[ -f "$1" ]] || { echo "FAIL: missing $1"; errors=$((errors + 1)); }; }

need "$ROOT/scripts/cursor_entry_gate.py"
need "$ROOT/.cursor/rules/000-entry-gate.mdc"
need "$ROOT/.cursor/rules/000-workspace-lock.mdc"
[[ -x "$ROOT/scripts/cursor_entry_gate.py" ]] || chmod +x "$ROOT/scripts/cursor_entry_gate.py"

python3 "$ROOT/scripts/cursor_entry_gate.py" --role brain >/dev/null
python3 "$ROOT/scripts/_worker_turn_validate_restore.py" >/dev/null

grep -q "cursor_entry_gate" "$ROOT/scripts/brain-session-start.sh" || {
  echo "FAIL: brain-session-start.sh must call cursor_entry_gate.py"
  errors=$((errors + 1))
}

for f in ARCHITECT_REPORT.yaml GLOBAL_BLOCKERS.json; do
  need "$ROOT/$f"
done
grep -q "ARCHITECT_REPORT.yaml" "$ROOT/scripts/cursor_entry_gate.py" || {
  echo "FAIL: cursor_entry_gate must hash ARCHITECT_REPORT.yaml"
  errors=$((errors + 1))
}

if [[ $errors -gt 0 ]]; then
  echo "FAIL: validate-cursor-entry-gate-v1 ($errors)"
  exit 1
fi
echo "OK: validate-cursor-entry-gate-v1"
