#!/usr/bin/env bash
# validate-fast-system-load-v1.sh — fast system load budget wired
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-fast-system-load-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/SOURCEA_FAST_SYSTEM_LOAD_BUDGET_LOCKED_v1.md" ]] || fail "missing load budget law"
test -x worker_verify_ultra_v1.sh || fail "worker_verify_ultra_v1 not executable"
test -x worker_turn_entry_v1.sh || fail "worker_turn_entry_v1 not executable"

bash validate-worker-loop-minimal-v1.sh || fail "worker loop minimal"
bash validate-worker-anti-staleness-v1.sh || fail "worker anti-staleness"
bash validate-commercial-worker-loop-v1.sh || fail "commercial worker loop"

python3 - <<'PY' || fail "healthy_prompt_turn sync=False"
from pathlib import Path
t = Path("healthy_prompt_turn_v1.py").read_text()
assert "write_truth(sync=False)" in t
print("OK: healthy_prompt_turn uses cached disk truth")
PY

grep -q "\-\-quick" hub_self_refresh_v1.py || fail "hub_self_refresh missing --quick"

echo "OK: validate-fast-system-load-v1"
