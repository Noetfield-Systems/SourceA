#!/usr/bin/env bash
# validate-mac-control-dispatch-v1.sh — Mac must proxy deploy, not block dispatch (INCIDENT-042 guard)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-mac-control-dispatch-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/scripts/fbe/lib/mac_control_dispatch_v1.py" ]] \
  || fail "missing mac_control_dispatch_v1.py"
[[ -f "$ROOT/scripts/mac_cloud_deploy_dispatch_v1.py" ]] \
  || fail "missing mac_cloud_deploy_dispatch_v1.py"

python3 - <<PY || fail "dispatch policy regression"
import sys
from pathlib import Path
sys.path.insert(0, str(Path("${ROOT}") / "scripts"))
from fbe.lib.mac_control_dispatch_v1 import (
    mac_observe_only_block,
    path_is_mac_motor_blocked,
)

allow = [
    "/api/cloud-worker/dispatch/v1",
    "/api/loop-specialist/tick/v1",
    "/api/forge/v02/run/v1",
    "/api/cloud-forge-run/observer/v1",
    "/api/cloud-forge-run/queue/v1",
]
block = [
    "/api/cloud-forge-run/auto-tick/v1",
    "/api/cloud-forge-run/proceed/v1",
    "/api/forge/v02/drain/v1",
]

for path in allow:
    assert not path_is_mac_motor_blocked(path), path
    assert mac_observe_only_block(path=path) is None, path

for path in block:
    assert path_is_mac_motor_blocked(path), path
    blocked = mac_observe_only_block(path=path)
    assert blocked and blocked.get("error") == "mac_observe_only", path

mutate = mac_observe_only_block(
    path="/api/cloud-forge-run/queue/v1",
    body={"action": "skip_head"},
)
assert mutate and mutate.get("motor_blocked") is True
read_only = mac_observe_only_block(path="/api/cloud-forge-run/queue/v1", body={"action": "get_head"})
assert read_only is None
print("ok")
PY

grep -q 'mac_control_dispatch_v1' "$ROOT/scripts/fbe/lib/hub_cloud_proxy_v1.py" \
  || fail "hub_cloud_proxy not wired to mac_control_dispatch_v1"

grep -q 'trigger_cf_tick' "$ROOT/scripts/cloud_workers_hub_v1.py" \
  || fail "cloud_workers_hub missing trigger_cf_tick action"

grep -q 'mac_control_dispatch_allowed' "$ROOT/data/cloud-auto-runtime-v1.json" \
  || fail "cloud-auto-runtime missing mac_control_dispatch_allowed"

echo "PASS: validate-mac-control-dispatch-v1.sh"
