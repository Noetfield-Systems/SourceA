#!/usr/bin/env bash
# validate-mac-control-dispatch-v1.sh — Mac must proxy deploy, not block dispatch (INCIDENT-042 guard)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-mac-control-dispatch-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/scripts/fbe/lib/mac_control_dispatch_v1.py" ]] \
  || fail "missing mac_control_dispatch_v1.py"
[[ -f "$ROOT/scripts/mac_cloud_deploy_dispatch_v1.py" ]] \
  || fail "missing mac_cloud_deploy_dispatch_v1.py"

SOURCEA_PY="${ROOT}/scripts/sourcea-python-v1.sh"
[[ -x "$SOURCEA_PY" ]] || fail "missing sourcea-python-v1.sh"
"$SOURCEA_PY" "$ROOT/scripts/test_mac_control_dispatch_policy_v1.py" \
  || fail "dispatch policy regression"

grep -q 'mac_control_dispatch_v1' "$ROOT/scripts/fbe/lib/hub_cloud_proxy_v1.py" \
  || fail "hub_cloud_proxy not wired to mac_control_dispatch_v1"

grep -q 'trigger_cf_tick' "$ROOT/scripts/cloud_workers_hub_v1.py" \
  || fail "cloud_workers_hub missing trigger_cf_tick action"

grep -q 'mac_control_dispatch_allowed' "$ROOT/data/cloud-auto-runtime-v1.json" \
  || fail "cloud-auto-runtime missing mac_control_dispatch_allowed"

grep -q '_is_control_panel_pid' "$ROOT/scripts/mac_pipeline_validator_pressure_v1.py" \
  || fail "Mac Health must not SIGKILL control-panel servers — wire _is_control_panel_pid"

grep -q 'control_panel_allowed' "$ROOT/data/mac-pipeline-validator-pressure-registry-v1.json" \
  || fail "registry missing control_panel_allowed allowlist"

grep -q 'upgrade_mac_motor_block' "$ROOT/scripts/fbe/lib/mac_control_dispatch_v1.py" \
  || fail "mac motor block must upgrade to CF tick — not dead-end error"

grep -q 'MAC-CTL-' "$ROOT/scripts/fbe/lib/hub_cloud_proxy_v1.py" \
  || fail "hub_cloud_proxy must resolve MAC-CTL plans locally on Mac"

grep -q 'sourcea-python-v1.sh' "$ROOT/scripts/enter-mac-control-plane-v1.sh" \
  || fail "enter-mac-control-plane must use sourcea-python-v1 (SIGKILL guard)"

echo "PASS: validate-mac-control-dispatch-v1.sh"
