#!/usr/bin/env bash
# validate-noetfield-freemium-bay-v1.sh — Phase 0 Noetfield freemium cloud bay gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-noetfield-freemium-bay-v1 — $*" >&2; exit 1; }

test -f data/factory-specs/noetfield-freemium-factory-v1.json || fail "factory spec missing"
test -f scripts/fbe/noetfield_freemium_bay_v1.py || fail "bay script missing"
test -f scripts/brain_phase0_work_order_v1.py || fail "brain phase0 compiler missing"

python3 - <<'PY' || fail "catalog row"
import json
from pathlib import Path
cat = json.loads(Path("data/fbe_catalog_v1.json").read_text())
row = next((x for x in cat.get("items") or [] if x.get("catalog_id") == "cat-noetfield-freemium"), None)
assert row, "cat-noetfield-freemium missing"
assert row.get("factory_id") == "noetfield-freemium-factory-v1"
assert row.get("status") == "mock_only"
assert row.get("demo_seconds")
print("OK: catalog cat-noetfield-freemium")
PY

python3 scripts/fbe/noetfield_freemium_bay_v1.py --json >/dev/null || fail "bay run failed"

python3 - <<'PY' || fail "verify.json"
import json
from pathlib import Path
v = json.loads(Path("receipts/bays/noetfield-freemium-bay/verify.json").read_text())
assert v.get("ok") is True, v
assert v.get("bay_slug") == "noetfield-freemium-bay"
print("OK: bay verify PASS")
PY

if [[ "${1:-}" == "--check-bay" ]]; then
  echo "OK: validate-noetfield-freemium-bay-v1 · --check-bay PASS"
  exit 0
fi

echo "OK: validate-noetfield-freemium-bay-v1 · Noetfield freemium cloud bay wired"
