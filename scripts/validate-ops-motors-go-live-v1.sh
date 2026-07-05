#!/usr/bin/env bash
# validate-ops-motors-go-live-v1.sh — aggregate Steps 1–10 disk + optional live probes
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: go-live — $*" >&2; exit 1; }

echo "== Step 1 Dockerfile bake =="
grep -q 'gmail_inbox_sweep_v1.py' "${ROOT}/cloud/Dockerfile.fbe-runner" || fail "Dockerfile missing gmail sweep"
grep -q 'PyJWT cryptography' "${ROOT}/cloud/Dockerfile.fbe-runner" || fail "Dockerfile missing PyJWT"

echo "== Step 2 Gmail SSOT =="
python3 -c "
import json
from pathlib import Path
ssot=json.loads(Path('${ROOT}/data/gmail-sweep-ssot-v1.json').read_text())
assert ssot.get('service_account'), 'service_account block required'
"

echo "== Steps 3–4 wiring =="
bash "${ROOT}/scripts/validate-ops-motors-v1.sh"

echo "== Step 5 e2e =="
bash "${ROOT}/scripts/validate-ops-motors-e2e-v1.sh"

echo "== Step 6 kaizen handlers =="
python3 -c "
import json
from pathlib import Path
h=json.loads(Path('${ROOT}/data/kaizen-fix-handlers-v1.json').read_text())
ids={x['id'] for x in h.get('handlers',[])}
for need in ('pgrst-reload','github-workflow-lint','repo-policy'):
    assert need in ids, need
"

echo "== Step 7 heartbeat format =="
grep -q 'deduped' "${ROOT}/scripts/daily_ops_heartbeat_v1.py" || fail "heartbeat dedupe missing"
grep -q 'ops_motors_glance' "${ROOT}/scripts/cloud_workers_hub_v1.py" || fail "hub glance missing"

echo "== Step 9 status script =="
python3 "${ROOT}/scripts/ops_motors_status_v1.py" --json >/dev/null

echo "== Step 10 SSOT lock =="
python3 -c "
import json
from pathlib import Path
c=json.loads(Path('${ROOT}/data/copilot-scheduled-automations-v1.json').read_text())
assert c.get('enabled') is False
ssot=json.loads(Path('${ROOT}/data/gmail-sweep-ssot-v1.json').read_text())
assert ssot.get('status') in ('go_live','live_verified'), ssot.get('status')
"

echo "== Step 8 GHA readiness =="
bash "${ROOT}/scripts/validate-ops-motors-gha-v1.sh" || true

if [[ "${OPS_MOTORS_GO_LIVE_LIVE:-}" == "1" ]]; then
  HEALTH="https://sourcea-loop-specialist-tick-v1.sina-kazemnezhad-ca.workers.dev/health"
  curl -sf "$HEALTH" | python3 -c "
import json,sys
d=json.load(sys.stdin)
assert d.get('ops_motors'), d
"
fi

echo "OK: validate-ops-motors-go-live-v1"
