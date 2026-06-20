#!/usr/bin/env bash
# validate-anti-staleness-auto-wire-v1.sh — L0.5→L1→L2 always wired
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-anti-staleness-auto-wire-v1 — $*" >&2; exit 1; }

test -f SOURCEA_ANTI_STALENESS_AUTO_WIRE_LAYER_SYNC_LOCKED_v1.md || fail "missing law doc"
test -f scripts/anti_staleness_auto_wire_v1.py || fail "missing orchestrator"

grep -q 'anti_staleness_auto_wire_v1.py' scripts/agent_session_gate_run_v1.py || fail "session gate not wired"
grep -q 'anti_staleness_auto_wire_v1.py' scripts/brain-session-start.sh || fail "brain-session-start not wired"
grep -q 'anti_staleness_auto_wire_v1.py' scripts/worker_turn_entry_v1.sh || fail "worker_turn_entry not wired"

python3 scripts/anti_staleness_auto_wire_v1.py --role any --tier session --json >/dev/null || fail "orchestrator run"

test -f "${SINA}/anti-staleness-auto-wire-v1.json" || fail "missing receipt"
test -f "${SINA}/agent-live-surfaces-v1.json" || fail "missing L0.5 surfaces"
test -f "${SINA}/agentic-layer-pipeline-v2.json" || fail "missing L1+L2 pipeline"
test -f "${SINA}/governance-brain-wire-v1.json" || fail "missing L2 brain wire"

python3 - <<'PY' || fail "receipt layer check"
import json
from pathlib import Path
r = json.loads((Path.home()/".sina/anti-staleness-auto-wire-v1.json").read_text())
assert r.get("ok"), r
layers = r.get("layers") or {}
assert layers.get("L0_5", {}).get("disk_live_wire"), layers
assert (layers.get("L1") or {}).get("l1_to_brain", 0) >= 3, layers
assert (layers.get("L2") or {}).get("l2_wired", 0) >= 4, layers
print("OK: receipt layers L0.5+L1+L2")
PY

bash scripts/validate-disk-live-wire-v1.sh >/dev/null || fail "disk live wire sub-validator"

bash scripts/validate-better-loop-v1.sh >/dev/null || fail "better loop v2 sub-validator"
bash scripts/validate-agent-nerve-system-v1.sh >/dev/null || fail "nerve system sub-validator"

echo "OK: validate-anti-staleness-auto-wire-v1 · L0.5→L1→L2 wired"
