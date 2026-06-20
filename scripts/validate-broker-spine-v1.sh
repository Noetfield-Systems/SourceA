#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-broker-spine-v1 — $*" >&2; exit 1; }

grep -q "def append_spine_worker_round" "$ROOT/scripts/goal1_lane_broker.py" \
  || fail "append_spine_worker_round missing"
grep -q "SPINE_WORKER_ROUND_FAIL" "$ROOT/scripts/goal1_lane_broker.py" \
  || fail "spine failure must be logged (no silent pass)"
python3 -c "
import re
from pathlib import Path
text = Path('$ROOT/scripts/goal1_lane_broker.py').read_text(encoding='utf-8')
assert 'append_spine_worker_round' in text, 'missing helper'
start = text.find('def append_spine_worker_round')
end = text.find('\ndef broker_state', start)
helper = text[start:end]
rest = text[:start] + text[end:]
assert 'spine_append(' in helper, 'helper must call spine_append'
assert 'spine_append(' not in rest, 'spine_append only allowed in append_spine_worker_round'
assert 'SPINE_WORKER_ROUND_FAIL' in helper, 'helper must log spine failures'
assert not re.search(
    r'append_spine_worker_round[\s\S]{0,600}except Exception:\s*\n\s*pass',
    helper,
), 'append_spine_worker_round must not silent-fail'
" || fail "broker spine wiring audit"

python3 <<PY
import importlib.util
import json
import sys
from pathlib import Path

root = Path("$ROOT")
spec = importlib.util.spec_from_file_location("broker", root / "scripts" / "goal1_lane_broker.py")
mod = importlib.util.module_from_spec(spec)
sys.modules["broker"] = mod
spec.loader.exec_module(mod)

sa = "sa-BROKER-SPINE-PROBE"
res = mod.append_spine_worker_round(
    sa=sa,
    round_type="check",
    orch_ok=True,
    deliver_ok=True,
    source="validate-broker-spine-v1",
)
assert res.get("ok"), res
ev = res.get("event") or {}
assert ev.get("event_type") == "WORKER_ROUND", ev
assert ev.get("skill_id") == "goal1-lane-broker", ev
assert ev.get("law_id") == "GOV_EVENT_SPINE", ev
assert sa in (ev.get("affected_objects") or []), ev
assert ev.get("replay_pointer", "").startswith("WORKER_ROUND:"), ev

ledger = Path.home() / ".sina" / "governance-event-spine-v1.jsonl"
found = False
if ledger.is_file():
    for line in ledger.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        if row.get("event_type") == "WORKER_ROUND" and row.get("object_id") == sa:
            found = True
            break
assert found, f"no WORKER_ROUND row for {sa} in spine ledger"

print("PASS: broker WORKER_ROUND spine append")
PY

echo "OK: validate-broker-spine-v1"
