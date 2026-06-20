#!/usr/bin/env bash
# Verify brain-os unified layout — canonical files exist; stubs not used by validators.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
BO="$ROOT/brain-os"

fail=0
need() {
  if [ -f "$1" ]; then echo "OK $1"; else echo "MISSING $1"; fail=1; fi
}

echo "=== brain-os canonical ==="
need "$BO/INDEX_LOCKED_v1.md"
need "$BO/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md"
need "$BO/plan-registry/SOURCEA-PRIORITY.md"
need "$BO/plan-registry/sourcea-1000/REGISTRY.json"
need "$BO/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md"
need "$BO/entry/START_HERE_LOCKED_v1.md"

echo "=== stubs (must not contain law body) ==="
if grep -q '^# MOVED' "$ROOT/os/chat-handoffs/BRAIN_UNIFIED_RULES_LOCKED_v1.md" 2>/dev/null; then
  echo "OK stub os/chat-handoffs/BRAIN_UNIFIED_RULES_LOCKED_v1.md"
else
  echo "FAIL stub missing or overwritten"; fail=1
fi

echo "=== validators use canonical ==="
grep -q 'brain-os/law/enforcement/REGISTRY_DRAIN_RAIL' scripts/validate-registry-drain-rail-v1.sh
grep -q 'brain-os/law/BRAIN_UNIFIED_RULES' scripts/cursor_entry_gate.py

bash scripts/validate-registry-drain-rail-v1.sh
python3 scripts/brain_gather_rules_v1.py --json | python3 -c "import json,sys; g=json.load(sys.stdin); assert g['healthy']"

test "$fail" -eq 0
echo "OK: validate-brain-os-complete-v1"
