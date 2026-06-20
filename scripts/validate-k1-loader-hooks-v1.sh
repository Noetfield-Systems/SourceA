#!/usr/bin/env bash
# validate-k1-loader-hooks-v1.sh — K1 at loaders, not build_payload
set -euo pipefail
cd "$(dirname "$0")/.."

fail() { echo "FAIL: validate-k1-loader-hooks-v1 — $*" >&2; exit 1; }

[[ -f scripts/k1_read_gate_v1.py ]] || fail "missing k1_read_gate_v1.py"
[[ -f demo/governance/K1_LOADER_HOOK_ARCHITECTURE_v1.md ]] || fail "missing architecture doc"

python3 - <<'PY' || fail "k1_read_gate imports"
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location("k1", "scripts/k1_read_gate_v1.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
for name in ("verify_checksum_on_read", "freshness_gate", "k1_after_queue_read", "active_now_file_fresh"):
    assert hasattr(mod, name), name
print("OK: k1_read_gate_v1 exports")
PY

grep -q 'k1_after_queue_read' scripts/healthy_queue_ssot_lib.py || fail "queue loader hook missing"
grep -q 'active_now_file_fresh' scripts/active_now_v1.py || fail "active_now freshness hook missing"
grep -q 'stale' scripts/overnight_one_step_v1.py || fail "overnight stale gate missing"
grep -q 'LOADER_HOOK_ARCHITECTURE' scripts/sina_command_lib.py || fail "kernel_k1 doc pointer missing"

python3 - <<'PY' || fail "overnight stale gate"
import sys
sys.path.insert(0, "scripts")
from overnight_one_step_v1 import is_overnight
# Cannot force stale without mocking — import must succeed
print("OK: is_overnight importable")
PY

echo "PASS: validate-k1-loader-hooks-v1"
