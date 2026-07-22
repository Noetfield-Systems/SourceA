#!/usr/bin/env bash
# validate-living-brain-master-plan-v1.sh — master plan SSOT wired (light, Mac-safe)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-living-brain-master-plan-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/data/sourcea-living-brain-autorun-master-plan-v1.json" ]] || fail "missing master plan JSON"
[[ -f "$ROOT/docs/SOURCEA_LIVING_BRAIN_AUTORUN_MASTER_PLAN_LOCKED_v1.md" ]] || fail "missing master plan doc"
[[ -f "$ROOT/docs/GOVERNED_AUTORUN_LAWS_v3.md" ]] || fail "missing laws v3"

grep -q 'living_brain_master_plan' "$ROOT/data/sourcea_orient_routing_v1.json" \
  || fail "orient step 15 not wired"
grep -q 'phase-living-brain-v1' "$ROOT/data/sourcea-worker-professional-assignment-v1.json" \
  || fail "worker assignment active phase not wired"

PY="$ROOT/scripts/sourcea-python-v1.sh"
[[ -x "$PY" ]] || PY="/usr/bin/python3"
"$PY" -c "
import json
from pathlib import Path
root = Path('$ROOT')
plan = json.loads((root / 'data/sourcea-living-brain-autorun-master-plan-v1.json').read_text())
assert plan.get('schema') == 'sourcea-living-brain-autorun-master-plan-v1'
assert len(plan.get('planes', [])) >= 8
assert len(plan.get('living_system_definition', {}).get('bridges', [])) >= 8
assert len(plan.get('worker_queue', {}).get('items', [])) >= 10
print(f\"OK plan: {len(plan['planes'])} planes · {len(plan['worker_queue']['items'])} worker items\")
"

echo "PASS: validate-living-brain-master-plan-v1.sh"
