#!/usr/bin/env bash
# validate-commercial-worker-loop-v1.sh — commercial Worker hot path wired
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-commercial-worker-loop-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/SOURCEA_COMMERCIAL_WORKER_LOOP_LOCKED_v1.md" ]] || fail "missing commercial loop law"

grep -q 'SINA_COMMERCIAL_LOOP' worker_turn_entry_v1.sh || fail "turn entry missing SINA_COMMERCIAL_LOOP"
grep -q 'SINA_BROKER_FAST' worker_turn_entry_v1.sh || fail "turn entry missing SINA_BROKER_FAST"
grep -q 'SINA_COMMERCIAL_LOOP' worker_verify_ultra_v1.sh || fail "ultra verify missing commercial env"
grep -q 'SINA_WORKER_LOOP' find_critical_bugs.py || fail "fcb missing worker redirect"
grep -q '\-\-fast' goal1_lane_broker.py || fail "broker missing cascade --fast"
grep -q 'kill_hung_processes' goal1_lane_broker.py || fail "pickup must not use full run_recovery"
grep -q 'run_recovery(redeliver=False)' goal1_lane_broker.py && fail "pickup still calls run_recovery"
grep -q '\-\-fast' advance-healthy-queue-v1.py || fail "advance missing --fast"
grep -q '_commercial_fast' healthy-drain-orchestrator-v1.py || fail "orchestrator missing commercial fast"
grep -q 'fast: bool' worker_inject_lib.py || fail "inject missing fast param"

bash validate-worker-loop-minimal-v1.sh || fail "worker loop minimal"
bash validate-worker-anti-staleness-v1.sh || fail "anti-staleness"
bash validate-worker-factory-heal-v1.sh || fail "factory heal gate"
bash validate-incident-fix-ownership-v1.sh --fast || fail "incident fix ownership + stairlift"
bash validate-founder-directive-propagation-v1.sh || fail "founder directive all layers"
bash validate-founder-input-cascade-v1.sh || fail "founder input cascade proof"

python3 - <<'PY' || fail "advance --fast"
import json, subprocess
out = subprocess.check_output(["python3", "advance-healthy-queue-v1.py", "--fast"], text=True)
row = json.loads(out)
assert row.get("ok") is True
assert (row.get("brain_sync") or {}).get("skipped") == "commercial_fast"
print("OK: advance --fast")
PY

echo "OK: validate-commercial-worker-loop-v1"
