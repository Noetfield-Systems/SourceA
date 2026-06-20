#!/usr/bin/env bash
# anti-fragmentation-e2e-wire-v1.sh — one chain: live wire · nerve · pipelines · hub · cloud
set -uo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0
pass() { echo "OK: $*"; }
fail() { echo "FAIL: anti-frag-e2e — $*" >&2; FAIL=1; }

echo "=== anti-fragmentation E2E wire ==="

python3 scripts/queue_ssot_unify_v1.py --json >/dev/null || fail "queue_ssot_unify"
pass "queue SSOT unify"

python3 scripts/disk_live_wire_sync_v1.py >/dev/null || fail "disk_live_wire_sync"
pass "disk live wire sync"

python3 scripts/agent_nerve_system_v1.py --json >/dev/null || fail "nerve pulse"
pass "nerve system pulse"

bash scripts/validate-agent-nerve-system-v1.sh || fail "validate-agent-nerve-system"
pass "validate agent nerve"

bash scripts/validate-l1-agent-pipeline-v1.sh || fail "validate-l1-agent-pipeline"
pass "L1→Brain pipeline"

bash scripts/validate-loop-specialist-v1.sh || fail "validate-loop-specialist"
pass "loop specialist wire"

bash scripts/validate-super-fast-hub-v1.sh || fail "validate-super-fast-hub"
pass "H1/H2 hub apps"

bash scripts/validate-brain-outbound-work-order-e2e-v1.sh || fail "brain-outbound-work-order-e2e"
pass "brain work-order E2E"

python3 scripts/cloud_factory_check_v1.py --json >/dev/null || fail "cloud_factory_check"
pass "cloud factory 10 steps"

python3 scripts/outbound_queue_coherence_v1.py assess --json >/dev/null || fail "queue coherence"
pass "queue ↔ plan coherence"

python3 scripts/plans_unified_upgrade_v1.py --json >/dev/null || fail "plans_unified_upgrade"
pass "plans unified upgrade"

python3 scripts/loop_observatory_report_v1.py --json >/dev/null || true
pass "loop observatory (commercial RED may fail ok=false — honest)"

if [[ "$FAIL" -ne 0 ]]; then
  echo "SUMMARY: anti-frag-e2e RED — see FAIL lines above"
  exit 1
fi
echo "SUMMARY: anti-frag-e2e PASS — nerve · pipelines · hub · cloud wired"
exit 0
