#!/usr/bin/env bash
# validate-worker-factory-heal-v1.sh — honest registry + queue sync wired on every turn
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-worker-factory-heal-v1 — $*" >&2; exit 1; }

[[ -f worker_factory_heal_v1.py ]] || fail "missing worker_factory_heal_v1.py"
grep -q 'worker_factory_heal_v1.py' worker_turn_entry_v1.sh || fail "turn entry missing factory heal"
grep -q 'CLOSEOUT_WITHOUT_BROKER_VERIFY' goal1_lane_broker.py || fail "broker missing verify-only closeout gate"
grep -q 'VERIFY_CLOSEOUT_FAILED\|closeout_result' goal1_lane_broker.py || fail "broker missing verify fail return"
grep -q 'enforce_honest_registry' goal1_lane_broker.py || fail "broker missing honest registry preflight"

python3 worker_factory_heal_v1.py --no-deliver --json >/dev/null || fail "factory heal dry run"

echo "OK: validate-worker-factory-heal-v1"
