#!/usr/bin/env bash
# validate-h2-weekly-receipt-bundle-cadence-v1.sh — sa-0814 integration-fabric weekly H2 bundle
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FABRIC="${HOME}/.sina/integration-fabric-registry-v1.yaml"

fail() { echo "FAIL: validate-h2-weekly-receipt-bundle-cadence-v1 — $*" >&2; exit 1; }

[[ -f "$FABRIC" ]] || fail "missing integration-fabric-registry-v1.yaml"
[[ -f "$ROOT/scripts/machine_hub_bundle_v1.py" ]] || fail "missing machine_hub_bundle_v1.py"

python3 - <<'PY' || fail "fabric cadence contract"
from pathlib import Path

text = Path.home().joinpath(".sina/integration-fabric-registry-v1.yaml").read_text()
need = [
    "h2-machine-bundle",
    "machine_hub_bundle_v1.py",
    "build_cadence_schedule:",
    "schedule: weekly",
    "forbidden_wheel:",
    "founder_refresh_triggers_full_rebuild",
    "H2_MACHINE_HEAVY",
    "h2-pending-registry-v1.json",
]
for n in need:
    if n not in text:
        raise SystemExit(f"missing fabric marker: {n}")
block = text.split("h2-machine-bundle", 1)[1].split("\n", 20)
joined = "\n".join(block)
if "machine_hub_bundle_v1.py" not in joined:
    raise SystemExit("h2-machine-bundle must reference machine_hub_bundle_v1.py")
if "schedule: weekly" not in joined:
    raise SystemExit("h2-machine-bundle missing schedule: weekly")
print("OK: integration-fabric weekly h2-machine-bundle documented")
PY

python3 "$ROOT/scripts/machine_hub_bundle_v1.py" --json --reason sa-0814-validate >/dev/null || fail "machine_hub_bundle_v1 dry run"
[[ -f "${HOME}/.sina/h2-machine-weekly-bundle-receipt-v1.json" ]] || fail "missing bundle receipt"

echo "OK: validate-h2-weekly-receipt-bundle-cadence-v1 · sa-0814"
