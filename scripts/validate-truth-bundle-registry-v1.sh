#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-truth-bundle-registry-v1 — $*" >&2; exit 1; }

REG="$ROOT/brain-os/plan-registry/sourcea-1000/REGISTRY.json"
[[ -f "$REG" ]] || fail "missing REGISTRY.json"
[[ -f "$ROOT/scripts/repair_sourcea_registry_v1.py" ]] || fail "missing repair script"

python3 -c "
import json
from pathlib import Path
p=Path('$REG')
d=json.loads(p.read_text(encoding='utf-8'))
assert len(d.get('plans') or [])==1000, len(d.get('plans') or [])
" || fail "REGISTRY.json invalid or not 1000 plans"

python3 "$ROOT/scripts/agent_truth_bundle_v1.py" --json >/dev/null || fail "agent_truth_bundle_v1"

python3 -c "
import sys
sys.path.insert(0,'$ROOT/scripts')
from governance_projection_g3_v1 import run_materializer
r=run_materializer('truth_bundle', reason='validate')
assert r.get('ok'), r
" || fail "truth_bundle materializer"

echo "OK: validate-truth-bundle-registry-v1"
