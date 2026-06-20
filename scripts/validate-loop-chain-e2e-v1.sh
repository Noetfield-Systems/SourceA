#!/usr/bin/env bash
# validate-loop-chain-e2e-v1.sh — full loop chain wire + routing panel + live surfaces
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-loop-chain-e2e-v1 — $*" >&2; exit 1; }

bash scripts/validate-investigator-judge-loop-v1.sh || fail "IJ10 base"

test -f scripts/founder_routing_panel_v1.py || fail "missing founder_routing_panel_v1.py"
grep -q 'founder_routing_panel' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire missing routing panel"
grep -q 'routing_panel' scripts/worker_hub_v1.py || fail "worker_hub missing routing_panel slice"
grep -q '/api/loop-chain/tick/v1' scripts/sina-command-server.py || fail "hub missing loop-chain route"
grep -q 'routing-panel-card' agent-control-panel/worker-hub/index.html || fail "H1 UI missing routing panel card"
grep -q 'disclosure-ladder-card' agent-control-panel/worker-hub/index.html || fail "H1 UI missing disclosure ladder card"
grep -q 'mcp-stack-card' agent-control-panel/worker-hub/index.html || fail "H1 UI missing mcp stack card"
grep -q 'loop-rooms-card' agent-control-panel/worker-hub/index.html || fail "H1 UI missing loop rooms card"

python3 scripts/founder_routing_panel_v1.py --json >/dev/null || fail "routing panel run"
test -f "${SINA}/founder-routing-panel-v1.json" || fail "missing founder-routing-panel receipt"

python3 - <<'PY' || fail "routing panel schema"
import json
from pathlib import Path

r = json.loads((Path.home() / ".sina/founder-routing-panel-v1.json").read_text())
if r.get("schema") != "founder-routing-panel-v1":
    raise SystemExit("bad schema")
if len(r.get("brand_routes") or []) < 6:
    raise SystemExit("missing brand routes")
if not r.get("founder_routing_panel_line"):
    raise SystemExit("missing line")
if not (r.get("loop_chain") or {}).get("investigator_line"):
    raise SystemExit("loop_chain missing investigator_line")
print("OK: routing panel", r.get("founder_routing_panel_line", "")[:72])
PY

python3 scripts/disk_live_wire_sync_v1.py --json >/dev/null 2>&1 || fail "disk_live_wire_sync"

python3 - <<'PY' || fail "live surfaces E2E lines"
import json
from pathlib import Path

s = json.loads((Path.home() / ".sina/agent-live-surfaces-v1.json").read_text())
need = (
    "loop_specialist_line",
    "investigator_line",
    "judge_loop_line",
    "founder_routing_panel_line",
    "disclosure_line",
    "mcp_stack_line",
    "tool_pick_line",
    "plans_unified_line",
    "anti_theater_line",
    "world_model_line",
)
for k in need:
    if not s.get(k):
        raise SystemExit(f"missing agent-live-surfaces {k}")
print("OK: live surfaces E2E lines wired")
PY

grep -q 'disclosure_ladder_v1' data/commercial/stack-map-routing-v1.json || fail "stack-map missing disclosure_ladder_v1"
grep -q 'mcp_stack_free_tier_v1' data/commercial/stack-map-routing-v1.json || fail "stack-map missing mcp_stack_free_tier_v1"
grep -q 'world_model_plan_check_v1' data/commercial/stack-map-routing-v1.json || fail "stack-map missing world_model_plan_check_v1"
grep -q 'anti_theater_validator_loop_v1' data/commercial/stack-map-routing-v1.json || fail "stack-map missing anti_theater_validator_loop_v1"
grep -q 'plans_unified_upgrade_v1' data/commercial/stack-map-routing-v1.json || fail "stack-map missing plans_unified_upgrade_v1"
grep -q 'tool_pick_two_phase_v1' data/commercial/stack-map-routing-v1.json || fail "stack-map missing tool_pick_two_phase_v1"

python3 - <<'PY' || fail "stack-map loop_chain_e2e"
import json
from pathlib import Path

r = json.loads(Path("data/commercial/stack-map-routing-v1.json").read_text())
if not r.get("loop_chain_e2e"):
    raise SystemExit("missing loop_chain_e2e in stack-map-routing")
print("OK: stack-map loop_chain_e2e")
PY

echo "PASS: validate-loop-chain-e2e-v1"
