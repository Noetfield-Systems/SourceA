#!/usr/bin/env bash
# P1 E2E recipe bundle — fast ladder script + standard recipe wiring + live fast ladder run.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"

for f in \
  validate-e2e-fast-ladder-v1.sh \
  validate-sourcea-e2e-standard-v1.sh; do
  test -x "$SCRIPTS/$f" || test -f "$SCRIPTS/$f"
done

grep -q "validate-e2e-fast-ladder-v1.sh" "$SCRIPTS/validate-sourcea-e2e-standard-v1.sh"
grep -q "validate-sourcea-e2e-full-v1.sh" "$SCRIPTS/validate-sourcea-e2e-standard-v1.sh"
grep -q "validate-goal1-e2e-v1.sh" "$SCRIPTS/validate-sourcea-e2e-standard-v1.sh"
grep -q "brain_validate_goal1_v1.py" "$SCRIPTS/validate-sourcea-e2e-standard-v1.sh"
grep -q 'tee "\$LOG"' "$SCRIPTS/validate-sourcea-e2e-standard-v1.sh"
grep -q "dual_proof=True" "$SCRIPTS/validate-sourcea-e2e-standard-v1.sh"
grep -q "factory lock preflight" "$SCRIPTS/validate-sourcea-e2e-standard-v1.sh"
grep -q "factory lock busy" "$SCRIPTS/validate-e2e-fast-ladder-v1.sh"
grep -q -- "--require-idle" "$SCRIPTS/validate-e2e-fast-ladder-v1.sh"
grep -q -- "--require-idle" "$SCRIPTS/validate-sourcea-e2e-standard-v1.sh"
grep -q "validate-sourcea-1000-pack.sh" "$SCRIPTS/validate-e2e-fast-ladder-v1.sh"
grep -q "validate-phase-s0-ssot-alignment-v1.sh" "$SCRIPTS/validate-e2e-fast-ladder-v1.sh"
grep -q "audit_hub_source_alignment.py" "$SCRIPTS/validate-e2e-fast-ladder-v1.sh"

bash "$SCRIPTS/validate-e2e-hardening-p0-v1.sh" >/dev/null
bash "$SCRIPTS/validate-sourcea-e2e-playbook-locked-v1.sh" >/dev/null

echo "=== live fast ladder (recipe P1) ==="
bash "$SCRIPTS/validate-e2e-fast-ladder-v1.sh" --require-idle

echo "PASS: validate-e2e-recipe-p1-v1"
