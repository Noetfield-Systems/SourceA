#!/usr/bin/env bash
# CIR-E2E exit=143 — worker_stuck_recovery must not SIGTERM factory lock holders.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
SCRIPTS="$ROOT/scripts"

grep -q "protected_validation_pids" "$SCRIPTS/factory_validation_lock_v1.py"
grep -q "PROTECTED_HOLDERS" "$SCRIPTS/factory_validation_lock_v1.py"
grep -q "protected_validation_pids" "$SCRIPTS/worker_stuck_recovery_v1.py"
grep -q "skipped_protected" "$SCRIPTS/worker_stuck_recovery_v1.py"
grep -q "_protected_validation_pids" "$SCRIPTS/cleanup-goal1-leftovers-v1.py"
grep -q "skipped_protected" "$SCRIPTS/cleanup-goal1-leftovers-v1.py"

python3 <<PY
import importlib.util
from pathlib import Path

root = Path("$ROOT")
spec = importlib.util.spec_from_file_location(
    "factory_validation_lock_v1",
    root / "scripts" / "factory_validation_lock_v1.py",
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert hasattr(mod, "protected_validation_pids")
assert "full_e2e" in mod.PROTECTED_HOLDERS
print("OK: factory-e2e-protection helpers import")
PY

echo "VALIDATE-FACTORY-E2E-PROTECTION ok"
