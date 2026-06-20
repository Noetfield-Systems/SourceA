#!/usr/bin/env bash
# validate-h2-weekly-ship-evidence-row-v1.sh — sa-0824 H2 evidence row after weekly SHIP pass
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-h2-weekly-ship-evidence-row-v1 — $*" >&2; exit 1; }

DOC="$ROOT/archive/attachments/2026-06-15/sa-0824-h2-weekly-ship-evidence-row_LOCKED_v1.md"
LAW="$ROOT/SOURCEA_H2_MACHINE_HUB_PLAN_LOCKED_v1.md"
PRIORITY="$ROOT/brain-os/plan-registry/SOURCEA-PRIORITY.md"
BUNDLE="${HOME}/.sina/h2-machine-weekly-bundle-receipt-v1.json"

[[ -f "$DOC" ]] || fail "missing LOCKED doc"
[[ -f "$LAW" ]] || fail "missing H2 plan"
[[ -f "$ROOT/scripts/h2_machine_hub_evidence_v1.py" ]] || fail "missing h2_machine_hub_evidence_v1.py"
grep -q "Hub 2 evidence row after weekly SHIP pass" "$LAW" || fail "H2 plan missing slot 24 pointer"

bash "$ROOT/scripts/validate-h2-weekly-receipt-bundle-cadence-v1.sh" >/dev/null || fail "weekly bundle cadence"

python3 "$ROOT/scripts/machine_hub_bundle_v1.py" --json --reason sa-0824-validate >/dev/null || fail "weekly bundle run"
[[ -f "$BUNDLE" ]] || fail "missing bundle receipt"

python3 "$ROOT/scripts/h2_machine_hub_evidence_v1.py" --json >/dev/null || fail "evidence append"
[[ -f "$PRIORITY" ]] || fail "missing SOURCEA-PRIORITY.md"
grep -q "sa-0824 Append H2 machine hub evidence row after weekly SHIP pass" "$PRIORITY" || fail "PRIORITY missing sa-0824 evidence row"
grep -q "validate-h2-weekly-ship-evidence-row-v1" "$PRIORITY" || fail "PRIORITY row missing validator proof"

python3 - <<'PY' || fail "receipt contract"
import json
from pathlib import Path

bundle = json.loads(Path.home().joinpath(".sina/h2-machine-weekly-bundle-receipt-v1.json").read_text())
assert bundle.get("schema") == "h2-machine-weekly-bundle-v1"
assert bundle.get("ok") is True
assert bundle.get("cadence") == "weekly"
steps = {s["step"]: s for s in bundle.get("steps") or []}
for need in ("h2_registry_reconcile", "hub_dual_heal", "validate_machine_hub"):
    assert steps.get(need, {}).get("ok"), need
print(f"OK: bundle at={bundle.get('at')} steps={len(steps)}")
PY

echo "OK: validate-h2-weekly-ship-evidence-row-v1 · sa-0824"
