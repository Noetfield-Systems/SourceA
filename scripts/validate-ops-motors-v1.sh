#!/usr/bin/env bash
# validate-ops-motors-v1.sh — Gmail sweep + triage + Kaizen + heartbeat wiring
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: $*" >&2; exit 1; }

[[ -f "${ROOT}/infra/supabase/portfolio-spine/migrations/012_gmail_inbox_signals_v1.sql" ]] || fail "missing migration 012"
[[ -f "${ROOT}/data/gmail-sweep-ssot-v1.json" ]] || fail "missing gmail SSOT"
[[ -f "${ROOT}/data/kaizen-fix-handlers-v1.json" ]] || fail "missing kaizen handlers"
[[ -f "${ROOT}/data/copilot-scheduled-automations-v1.json" ]] || fail "missing copilot SSOT"

for s in gmail_inbox_sweep_v1.py signal_factory_triage_v1.py kaizen_nightly_tick_v1.py daily_ops_heartbeat_v1.py fbe_cloud_ops_motors_v1.py; do
  [[ -f "${ROOT}/scripts/${s}" ]] || fail "missing script ${s}"
done

grep -q 'gmail-sweep/v1' "${ROOT}/scripts/fbe_cloud_worker_http_v1.py" || fail "FBE missing gmail-sweep route"
grep -q 'signal-factory/triage/v1' "${ROOT}/scripts/fbe_cloud_worker_http_v1.py" || fail "FBE missing triage route"
grep -q 'kaizen/nightly/v1' "${ROOT}/scripts/fbe_cloud_worker_http_v1.py" || fail "FBE missing kaizen route"
grep -q 'ops/heartbeat/v1' "${ROOT}/scripts/fbe_cloud_worker_http_v1.py" || fail "FBE missing heartbeat route"
grep -q 'gmail-sweep' "${ROOT}/cloud/workers/loop-specialist-tick-v1/src/index.js" || fail "loop-specialist missing gmail sweep"
grep -q 'SOURCEA_OPS_HEARTBEAT_v1' "${ROOT}/scripts/daily_ops_heartbeat_v1.py" || fail "heartbeat format"

python3 -c "
import json
from pathlib import Path
c = json.loads(Path('${ROOT}/data/copilot-scheduled-automations-v1.json').read_text())
assert c.get('enabled') is False
" || fail "copilot automations must be disabled"

echo "OK: validate-ops-motors-v1"
