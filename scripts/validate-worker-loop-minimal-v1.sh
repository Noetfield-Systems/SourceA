#!/usr/bin/env bash
# validate-worker-loop-minimal-v1.sh — worker loop must not inject full fleet verify
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-worker-loop-minimal-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "normalize"
from worker_verify_normalize_v1 import normalize_worker_verify
out = normalize_worker_verify("cd scripts && python3 find_critical_bugs.py", role="verify")
assert "worker_verify_ultra_v1.sh" in out
assert "find_critical_bugs.py" not in out
out2 = normalize_worker_verify(
    "cd scripts && SINA_AUDIT_STRICT=1 python3 build-sina-command-panel.py && python3 find_critical_bugs.py",
    role="verify",
)
assert "build-sina-command-panel" not in out2
print("OK: worker_verify_normalize_v1")
PY

grep -q "worker_verify_ultra_v1.sh" healthy_prompt_turn_v1.py || fail "healthy_prompt_turn missing ultra verify"
grep -q "WORKER_NO_SLOW_VERIFY" healthy_prompt_turn_v1.py || fail "healthy_prompt_turn missing slow verify ban"

grep -q "worker_verify_ultra_v1.sh" ../brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md || fail "worker mandatory missing ultra verify"
grep -q "worker_turn_entry_v1.sh" ../brain-os/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md || fail "worker mandatory missing turn entry"
grep -q "worker_anti_staleness" worker_turn_entry_v1.sh || fail "turn entry missing AS heal"
grep -q "worker_anti_staleness" worker_verify_ultra_v1.sh || fail "ultra verify missing AS heal"
grep -q '\-\-fast' goal1_lane_broker.py || fail "broker must use cascade --fast"
grep -q 'SINA_WORKER_LOOP' find_critical_bugs.py || fail "find_critical_bugs missing worker redirect"

test -x worker_verify_fast_v1.sh || fail "worker_verify_fast_v1.sh not executable"

echo "OK: validate-worker-loop-minimal-v1"
