#!/usr/bin/env bash
# validate-fbe-cloud-phase1-v1.sh — Hub proxy + execution contract + cloud worker skeleton
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

echo "=== Phase 1 data SSOT ==="
for f in \
  data/fbe_execution_contract_v1.json \
  data/fbe_cloud_worker_config_v1.json; do
  [[ -f "$f" ]] || { echo "FAIL: missing $f"; fail=1; }
done

echo "=== Execution contract + policy gate ==="
python3 - <<'PY' || fail=1
import sys
sys.path.insert(0, "scripts")
from fbe.lib.execution_contract_v1 import build_contract, validate_contract, policy_gate, kernel_hash

c = build_contract(factory_id="web-product-factory-v1", tenant_id="wil_ai_design_partner")
v = validate_contract(c)
assert v["ok"], v
g = policy_gate(c, freeze_active=True, cloud_url_configured=False)
assert g["decision"] == "DENY", g
assert "freeze_requires_cloud_worker_url" in g["reasons"], g
assert len(kernel_hash()) == 16
print("OK: execution contract + policy gate")
PY

echo "=== Hub cloud proxy status ==="
python3 - <<'PY' || fail=1
import sys
sys.path.insert(0, "scripts")
from fbe.lib.hub_cloud_proxy_v1 import status_payload, execution_mode

row = status_payload()
assert "execution_mode" in row
assert "cloud_execution_required" in row
print("OK: hub proxy status", execution_mode())
PY

echo "=== Cloud adapter railway mode (dry) ==="
python3 - <<'PY' || fail=1
import sys
sys.path.insert(0, "scripts")
from fbe.lib.cloud_adapter_v1 import skeleton_ready, submit_job

sk = skeleton_ready()
assert sk["dockerfile"] and sk["entrypoint"], sk
row = submit_job(
    template_id="web-product-factory-v1",
    work_order_id="wo-phase1-validate",
    dry_run=True,
    mode="railway_fbe",
)
assert row.get("dry_run") is True
print("OK: cloud adapter skeleton + dry submit")
PY

echo "=== Cloud worker HTTP import ==="
python3 -c "import importlib.util; import pathlib; p=pathlib.Path('scripts/fbe_cloud_worker_http_v1.py'); assert p.is_file(); print('OK: cloud worker module present')"

echo "=== Dockerfile + entrypoint serve-http ==="
grep -q -- '--serve-http' cloud/fbe-worker-entrypoint.sh || { echo "FAIL: entrypoint missing --serve-http"; fail=1; }
grep -q 'fbe_cloud_worker_http_v1.py' cloud/Dockerfile.fbe-runner || { echo "FAIL: dockerfile missing http worker"; fail=1; }
grep -q 'fbe_execution_contract_v1.json' cloud/Dockerfile.fbe-runner || { echo "FAIL: dockerfile missing contract"; fail=1; }

echo "=== Hub server proxy hook ==="
grep -q 'dispatch_fbe_route' scripts/sina-command-server.py || { echo "FAIL: hub missing dispatch_fbe_route"; fail=1; }
grep -q '/api/fbe/cloud-proxy/v1' scripts/sina-command-server.py || { echo "FAIL: hub missing cloud-proxy route"; fail=1; }
grep -q '/api/loop-specialist/tick/v1' scripts/sina-command-server.py || { echo "FAIL: hub missing loop-specialist tick route"; fail=1; }

echo "=== Loop specialist cloud contract ==="
test -f data/loop-specialist-cloud-contract-v1.json || { echo "FAIL: missing loop-specialist cloud contract"; fail=1; }
python3 - <<'PY' || fail=1
import sys
sys.path.insert(0, "scripts")
from fbe.lib.hub_cloud_proxy_v1 import status_payload

row = status_payload()
assert "loop_specialist_cloud_ready" in row
assert row.get("loop_specialist_hub_api")
print("OK: loop_specialist_cloud_ready in hub proxy status")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-cloud-phase1-v1"
  exit 0
fi
echo "FAIL: validate-fbe-cloud-phase1-v1"
exit 1
