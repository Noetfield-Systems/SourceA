#!/usr/bin/env bash
# validate-mac-health-never-again-v1.sh — permanent incident guards
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
fail() { echo "FAIL: validate-mac-health-never-again-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/scripts/mac_health_never_again_v1.py" ]] || fail "missing never-again module"
[[ -f "$ROOT/scripts/autorun_worker_guard_v1.sh" ]] || fail "missing autorun guard script"
[[ -x "$ROOT/scripts/autorun_worker_guard_v1.sh" ]] || fail "autorun guard not executable"

python3 "$ROOT/scripts/mac_health_never_again_v1.py" --dry-run --json >/dev/null \
  || fail "never-again dry-run failed"

grep -q 'fbe_motor_delegate_v1' "$ROOT/scripts/mac_health_emergency_stop_v1.py" \
  || fail "emergency stop missing fbe_motor kill pattern"
grep -q 'agent_rules_loop_orchestrator' "$ROOT/scripts/mac_health_emergency_stop_v1.py" \
  || fail "emergency stop missing rules_loop kill pattern"
grep -q 'motor >= 8' "$ROOT/scripts/mac_health_log_shield_v1.py" \
  || fail "motor surge threshold not hardened"

python3 -c "
from mac_health_version_v1 import MAC_HEALTH_VERSION
assert MAC_HEALTH_VERSION.startswith('3.3'), MAC_HEALTH_VERSION
"

echo "PASS: validate-mac-health-never-again-v1.sh"
