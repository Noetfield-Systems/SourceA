#!/usr/bin/env bash
# Hub cloud drain proceed v1 — wiring validator
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

test -f data/hub-cloud-drain-proceed-v1.json || { echo "FAIL: SSOT missing"; exit 1; }
test -f scripts/hub_cloud_drain_proceed_v1.py || { echo "FAIL: script missing"; exit 1; }

rg -q 'cloud-drain/proceed/v1' scripts/sina-command-server.py || { echo "FAIL: hub route missing in sina-command-server"; FAIL=1; }
rg -q 'cloud-drain/proceed/v1' scripts/fbe_cloud_worker_http_v1.py || { echo "FAIL: cloud route missing in fbe_cloud_worker_http"; FAIL=1; }
rg -q 'cloud_drain_proceed' scripts/worker_hub_v1.py || { echo "FAIL: worker_hub slice missing"; FAIL=1; }
rg -q 'btn-cloud-proceed' agent-control-panel/worker-hub/index.html || { echo "FAIL: hub UI button missing"; FAIL=1; }
rg -q 'hub_cloud_proceed_forbidden' scripts/agentic_conduct_gate_v1.py || { echo "FAIL: conduct gate missing"; FAIL=1; }
rg -q 'Hub Proceed only' scripts/next_task_trigger_v1.py || { echo "FAIL: next_task recommendation missing"; FAIL=1; }

python3 scripts/hub_cloud_drain_proceed_v1.py --inject --json >/dev/null || { echo "FAIL: inject"; FAIL=1; }
python3 scripts/hub_cloud_drain_proceed_v1.py --slice --json >/dev/null || { echo "FAIL: hub_slice"; FAIL=1; }

if [[ "$FAIL" -ne 0 ]]; then
  echo "validate-hub-cloud-drain-proceed-v1: FAIL"
  exit 1
fi
echo "validate-hub-cloud-drain-proceed-v1: PASS"
