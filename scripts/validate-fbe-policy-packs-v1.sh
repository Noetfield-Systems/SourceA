#!/usr/bin/env bash
# validate-fbe-policy-packs-v1.sh — Policy pack registry + catalog wiring
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== Policy registry ==="
[[ -f data/policy-packs/registry-v1.json ]] || { echo "FAIL: missing registry"; fail=1; }

echo "=== Catalog policy_packs tier + 7 items ==="
python3 - <<'PY' || fail=1
import json
from pathlib import Path
cat = json.loads(Path("data/fbe_catalog_v1.json").read_text())
assert "policy_packs" in (cat.get("tiers") or {}), cat["tiers"]
items = cat.get("items") or []
assert len(items) >= 7, len(items)
packs = [i for i in items if i.get("tier") == "policy_packs"]
assert len(packs) >= 3, packs
for i in items:
    assert i.get("policy_pack_id"), i
    assert i.get("install_label"), i
print("OK: catalog", len(items), "items,", len(packs), "policy packs")
PY

echo "=== Wrapper specs ==="
for f in compliance-kyb-wrapper-v1 compliance-aml-wrapper-v1 ma-diligence-wrapper-v1; do
  [[ -f "data/factory-specs/${f}.json" ]] || { echo "FAIL: missing $f"; fail=1; }
done

echo "=== Execution contract policy_pack ==="
python3 - <<'PY' || fail=1
import sys
sys.path.insert(0, "scripts")
from fbe.lib.execution_contract_v1 import contract_from_hub_body, get_policy_pack

body = {"factory_id": "compliance-kyb-wrapper-v1", "tenant": "trustfield"}
c = contract_from_hub_body("/api/fbe/run-exchange/v1", body)
assert c.get("policy_pack") == "fintrac_kyb_v1", c
assert c.get("policy_hash"), c
assert get_policy_pack("aml_screening_v1"), "aml pack missing"
gate_pack = get_policy_pack("fintrac_kyb_v1")
assert gate_pack.get("extends_engine") == "exchange-factory-v1", gate_pack
print("OK: policy_pack in contract", c["policy_pack"])
PY

echo "=== Full catalog validate ==="
python3 scripts/fbe_factory_spec_v1.py --validate --json >/tmp/policy-spec-val.json
python3 - <<'PY' || fail=1
import json
row = json.load(open("/tmp/policy-spec-val.json"))
assert row.get("ok") is True, row
assert row.get("specs_valid", 0) >= 7, row
print("OK: specs_valid", row.get("specs_valid"))
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-policy-packs-v1"
  exit 0
fi
echo "FAIL: validate-fbe-policy-packs-v1"
exit 1
