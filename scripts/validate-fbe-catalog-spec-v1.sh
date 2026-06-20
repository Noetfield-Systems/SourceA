#!/usr/bin/env bash
# validate-fbe-catalog-spec-v1.sh — Factory Spec Language + catalog SSOT
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== Catalog + spec SSOT files ==="
for f in \
  data/fbe_catalog_v1.json \
  data/fbe_factory_spec_schema_v1.json \
  data/factory-specs/web-product-factory-v1.json \
  data/factory-specs/exchange-factory-v1.json \
  data/factory-specs/forge-app-factory-v1.json \
  data/factory-specs/compliance-kyb-wrapper-v1.json \
  data/factory-specs/sandbox-mock-factory-v1.json; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f"; fail=1; }
done

echo "=== Factory spec validate ==="
python3 scripts/fbe_factory_spec_v1.py --validate --json >/tmp/fbe-spec-validate.json || fail=1
python3 - <<'PY' || fail=1
import json
row = json.load(open("/tmp/fbe-spec-validate.json"))
assert row.get("ok") is True, row
assert row.get("item_count", 0) >= 7, row
assert row.get("specs_valid", 0) >= 7, row
print("OK: catalog validate", row.get("item_count"), "items")
PY

echo "=== Resolve hero factory ==="
python3 - <<'PY' || fail=1
import json, sys
sys.path.insert(0, "scripts")
from fbe.lib.factory_spec_v1 import resolve_execution

row = resolve_execution(factory_id="exchange-factory-v1")
assert row["ok"], row
assert row["api_route"] == "/api/fbe/run-exchange/v1", row
assert row["body"]["execution_mode"] == "CLOUD_ONLY", row
print("OK: resolve exchange", row["api_route"])
PY

echo "=== Resolve KYB wrapper ==="
python3 - <<'PY' || fail=1
import sys
sys.path.insert(0, "scripts")
from fbe.lib.factory_spec_v1 import resolve_execution

row = resolve_execution(factory_id="compliance-kyb-wrapper-v1")
assert row["ok"], row
assert row["body"]["wrapper_id"] == "compliance-kyb-wrapper-v1", row
assert row["body"]["template_id"] == "exchange-factory-v1", row
print("OK: resolve KYB wrapper")
PY

echo "=== Hub catalog route wired ==="
grep -q '/api/fbe/catalog/v1' scripts/sina-command-server.py || { echo "FAIL: hub catalog route"; fail=1; }

echo "=== Locked doc datetime ==="
bash scripts/validate-doc-datetime-header-v1.sh docs/SOURCEA_FBE_FACTORY_SPEC_LANGUAGE_LOCKED_v1.md || fail=1

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-catalog-spec-v1"
  exit 0
fi
echo "FAIL: validate-fbe-catalog-spec-v1"
exit 1
