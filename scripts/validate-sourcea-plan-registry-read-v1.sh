#!/usr/bin/env bash
# Validate SourceA Supabase plan registry read chain (Mac-safe).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "=== sourcea plan registry read ==="

SOURCEA_ROOT="$ROOT" python3 - <<'PY'
import importlib.util
import json
import os
from pathlib import Path

root = Path(os.environ["SOURCEA_ROOT"])
client_path = root / "scripts/sourcea_plan_registry_client_v1.py"
fbe_path = root / "scripts/fbe_cloud_worker_http_v1.py"
cf_path = root / "cloud/workers/cloud-auto-runtime-tick-v1/src/index.js"
contract_path = root / "docs/SOURCEA_PLAN_REGISTRY_READ_CONTRACT_LOCKED_v1.md"
chain_path = root / "data/sourcea-supabase-plan-registry-chain-v1.json"

assert contract_path.is_file(), contract_path
chain = json.loads(chain_path.read_text(encoding="utf-8"))
assert chain["status"] == "connected_imported", chain.get("status")
assert int(chain["last_verified"]["imported_rows"]) >= 23485

spec = importlib.util.spec_from_file_location("plan_client", client_path)
client = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(client)

count = client.count_rows()
assert count["ok"], count
assert int(count.get("total") or 0) >= 23485, count
assert count.get("auth_mode") == "anon", count
assert not count.get("secret_leak"), count

rows = client.query_rows(limit=1)
assert rows["ok"], rows
assert rows["count"] == 1, rows
assert not rows.get("secret_leak"), rows
sample_id = rows["rows"][0]["plan_id"]

detail = client.get_plan(sample_id)
assert detail["ok"], detail
assert detail["found"], detail
assert detail["rows"][0]["plan_id"] == sample_id, detail
assert not detail.get("secret_leak"), detail

contract = client.contract_summary()
assert contract["default_auth_mode"] == "anon", contract
assert "plan_id" in contract["filters"], contract

fbe = fbe_path.read_text(encoding="utf-8")
assert "/api/sourcea/plan-registry/v1" in fbe
assert "secret_like_response_blocked" in fbe
assert "sourcea-plan-registry-read-v1" in fbe

cf = cf_path.read_text(encoding="utf-8")
assert 'url.pathname === "/plan-registry"' in cf
assert "proxyPlanRegistry" in cf
assert "FBE_INTERNAL_SECRET" in cf
assert "Cache-Control" in cf

for payload in (count, rows, detail):
    blob = json.dumps(payload)
    forbidden = ["SUPABASE_SERVICE_ROLE_KEY", "SUPABASE_DB_PASSWORD", "DATABASE_URL", "POSTGRES_URL", "sb_secret_"]
    assert not any(term in blob for term in forbidden), forbidden

print("OK total", count.get("total"))
print("OK sample_plan", sample_id)
print("OK fbe_route", "/api/sourcea/plan-registry/v1")
print("OK cf_proxy", "/plan-registry")
PY

echo "validate-sourcea-plan-registry-read-v1.sh: ALL PASS"
