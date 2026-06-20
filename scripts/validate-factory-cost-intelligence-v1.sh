#!/usr/bin/env bash
# validate-factory-cost-intelligence-v1.sh
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-factory-cost-intelligence-v1 — $*" >&2; exit 1; }

test -f data/factory-cost-intelligence-loop-v1.json || fail "missing SSOT"
test -f scripts/factory_cost_intelligence_v1.py || fail "missing script"
grep -q 'factory_cost_intelligence' scripts/agent_memory_mirror_v1.py || fail "memory mirror not wired"
grep -q 'factory_cost_intelligence' scripts/governance_gate_cart_v1.py || fail "gate cart not wired"
grep -q 'cost_intelligence_line' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire not wired"
grep -q 'cost_intelligence_line' scripts/worker_live_context_v1.py || fail "worker live context not wired"
grep -q 'cost_intelligence_line' scripts/brain_live_context_v1.py || fail "brain live context not wired"
grep -q 'factory_cost_intelligence' scripts/agent_nerve_system_v1.py || fail "nerve not wired"
grep -q 'factory_cost_intelligence' scripts/worker_hub_v1.py || fail "worker hub not wired"

python3 - <<'PY' || fail "registry count"
import json
from pathlib import Path
d = json.loads(Path("data/factory-cost-intelligence-loop-v1.json").read_text())
if len(d.get("factories") or []) != 100:
    raise SystemExit(f"expected 100 factories got {len(d.get('factories') or [])}")
print("OK: registry 100")
PY

python3 scripts/agent_memory_mirror_v1.py --sync --json >/dev/null || fail "mirror sync"
python3 scripts/factory_cost_intelligence_v1.py --wire --json >/dev/null || fail "cost intel wire"

test -f "${SINA}/factory-cost-intelligence-receipt-v1.json" || fail "missing receipt"

python3 - <<'PY' || fail "mirror inject"
import json
from pathlib import Path
m = json.loads((Path.home() / ".sina/agent-memory-mirror-v1.json").read_text())
inj = m.get("inject") or {}
if not inj.get("factory_cost_intelligence"):
    raise SystemExit("missing factory_cost_intelligence in inject")
detail = inj.get("factory_cost_intelligence_detail") or {}
if int(detail.get("registry_count") or 0) < 100:
    raise SystemExit("registry_count < 100 in inject detail")
print("OK: mirror inject")
PY

python3 scripts/factory_cost_intelligence_v1.py --validate --json >/dev/null || fail "validate after wire"

echo "PASS: validate-factory-cost-intelligence-v1"
