#!/usr/bin/env bash
# validate-sourcea-deep-research-10-v1.sh — UP-DR-01..10 wave SSOT checks
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: $*" >&2; exit 1; }

python3 -c "
import json, sys
from pathlib import Path
root = Path('$ROOT')
plan = json.loads((root / 'data/sourcea-deep-research-10-upgrade-plan-v1.json').read_text())
ups = plan.get('upgrade_plans') or []
if len(ups) != 10:
    sys.exit(f'upgrade_plans count {len(ups)} != 10')
ids = [p['id'] for p in ups]
for i in range(1, 11):
    want = f'UP-DR-{i:02d}'
    if want not in ids:
        sys.exit(f'missing {want}')
reg = json.loads((root / 'brain-os/plan-registry/sourcea-deep-research-v1/REGISTRY.json').read_text())
if not reg.get('w1_execution'):
    sys.exit('REGISTRY missing w1_execution')
queue = json.loads((root / 'data/client-proof-recipe-queue-v1.json').read_text())
items = queue.get('items') or []
if not items:
    sys.exit('empty client-proof queue')
first = items[0].get('plan_id', '')
if not str(first).startswith('UP-DR-'):
    sys.exit(f'queue head not UP-DR: {first}')
runtime = json.loads((root / 'data/cloud-auto-runtime-v1.json').read_text())
cap = int(runtime.get('max_advance_per_tick') or 0)
if cap != 1:
    sys.exit(f'max_advance_per_tick={cap} want 1')
print('OK deep-research-10 structure')
"

python3 scripts/sourcea_deep_research_10_pulse_v1.py --json >/dev/null
test -f docs/SOURCEA_DEEP_RESEARCH_10_UPGRADE_PLANS_LOCKED_v1.md || fail "missing locked doc"
test -f data/secondary-cloud-forge-run-batch-83-locked-v1.json || fail "missing batch 83"

echo "PASS validate-sourcea-deep-research-10-v1"
