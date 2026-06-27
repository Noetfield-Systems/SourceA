#!/usr/bin/env bash
# Hub Cloud Forge Run proceed v1 — wiring validator
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0

check() {
  if ! "$@"; then
    echo "FAIL: $*"
    FAIL=1
  fi
}

test -f data/hub-cloud-forge-run-proceed-v1.json || { echo "FAIL: SSOT missing"; exit 1; }
test -f scripts/hub_cloud_forge_run_proceed_v1.py || { echo "FAIL: script missing"; exit 1; }

rg -q 'cloud-forge-run/proceed/v1' scripts/sina-command-server.py || { echo "FAIL: hub route missing in sina-command-server"; FAIL=1; }
rg -q 'cloud-forge-run/proceed/v1' scripts/fbe_cloud_worker_http_v1.py || { echo "FAIL: cloud route missing in fbe_cloud_worker_http"; FAIL=1; }
rg -q 'cloud_forge_run_proceed' scripts/worker_hub_v1.py || { echo "FAIL: worker_hub slice missing"; FAIL=1; }
rg -q 'btn-cloud-proceed' agent-control-panel/worker-hub/index.html || { echo "FAIL: hub UI button missing"; FAIL=1; }
rg -q 'hub_cloud_proceed_forbidden' scripts/agentic_conduct_gate_v1.py || { echo "FAIL: conduct gate missing"; FAIL=1; }
rg -q 'Hub Proceed only' scripts/next_task_trigger_v1.py || { echo "FAIL: next_task recommendation missing"; FAIL=1; }

python3 scripts/hub_cloud_forge_run_proceed_v1.py --inject --json >/dev/null || { echo "FAIL: inject"; FAIL=1; }
python3 scripts/hub_cloud_forge_run_proceed_v1.py --slice --json >/dev/null || { echo "FAIL: hub_slice"; FAIL=1; }

python3 scripts/test_cloud_forge_run_advance_head_guard_v1.py >/dev/null || { echo "FAIL: advance_head_guard"; FAIL=1; }
python3 scripts/test_proceed_on_cloud_head_align_v1.py >/dev/null || { echo "FAIL: proceed_head_align"; FAIL=1; }
python3 scripts/test_mac_post_process_cloud_sync_v1.py >/dev/null || { echo "FAIL: mac_post_process_sync"; FAIL=1; }
python3 scripts/test_cloud_auto_runtime_idle_batch_no_fake_green_v1.py >/dev/null || { echo "FAIL: idle_batch_no_fake_green"; FAIL=1; }

rg -q 'plan_not_queue_head' scripts/fbe/lib/cloud_forge_run_queue_v1.py || { echo "FAIL: advance guard missing"; FAIL=1; }
rg -q 'cloud_receipt_not_local_advance' scripts/hub_cloud_forge_run_proceed_v1.py || { echo "FAIL: mac sync source tag missing"; FAIL=1; }
rg -q 'plan_id != cloud_head' scripts/hub_cloud_forge_run_proceed_v1.py || { echo "FAIL: cloud head align missing"; FAIL=1; }
rg -q 'idle_batch' scripts/cloud_auto_runtime_v1.py || { echo "FAIL: idle_batch guard missing"; FAIL=1; }

if [[ "$FAIL" -ne 0 ]]; then
  echo "validate-hub-cloud-forge-run-proceed-v1: FAIL"
  exit 1
fi
echo "validate-hub-cloud-forge-run-proceed-v1: PASS"
