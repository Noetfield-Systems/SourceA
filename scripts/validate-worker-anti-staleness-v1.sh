#!/usr/bin/env bash
# validate-worker-anti-staleness-v1.sh — fast AS probe+heal <8s, no full bundle
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT/scripts"

fail() { echo "FAIL: validate-worker-anti-staleness-v1 — $*" >&2; exit 1; }

test -f worker_anti_staleness_heal_v1.py || fail "missing worker_anti_staleness_heal_v1.py"
test -x worker_verify_ultra_v1.sh || fail "worker_verify_ultra_v1 not executable"
test -x worker_turn_entry_v1.sh || fail "worker_turn_entry_v1 not executable"

if ! grep -q "anti_staleness_auto_wire_v1.py" worker_turn_entry_v1.sh && ! grep -q "worker_anti_staleness_heal_v1.py" worker_turn_entry_v1.sh; then
  fail "turn entry missing AS heal (auto_wire or direct heal)"
fi
grep -q "worker_anti_staleness_heal_v1.py" worker_verify_ultra_v1.sh || fail "ultra verify missing AS heal"
grep -q "find_critical_bugs" worker_turn_entry_v1.sh && fail "turn entry must not call find_critical_bugs"
grep -q "validate-anti-staleness-bundle" worker_turn_entry_v1.sh && fail "turn entry must not call AS bundle"

python3 - <<'PY' || fail "probe schema"
import json, subprocess
out = subprocess.check_output(["python3", "worker_anti_staleness_heal_v1.py", "--probe", "--json"], text=True)
row = json.loads(out)
assert row.get("schema") == "worker-hub-staleness-v1"
assert "auto_heal_recommended" in row
print("OK: probe schema")
PY

t0=$(python3 - <<'PY'
import time; print(time.time())
PY
)
python3 worker_anti_staleness_heal_v1.py --json >/dev/null || fail "AS heal failed"
t1=$(python3 - <<'PY'
import time; print(time.time())
PY
)
ms=$(python3 - <<PY
print(int((${t1} - ${t0}) * 1000))
PY
)
if [ "$ms" -gt 8000 ]; then
  fail "AS heal too slow: ${ms}ms (max 8000)"
fi
echo "OK: AS heal ${ms}ms (<8s)"

test -f "${HOME}/.sina/worker-as-heal-receipt-v1.json" || fail "missing receipt"

echo "OK: validate-worker-anti-staleness-v1"
