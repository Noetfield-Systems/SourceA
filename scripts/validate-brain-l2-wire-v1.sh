#!/usr/bin/env bash
# L2 Brain wire — all second-layer agents bound to governance-brain-wire-v1.json
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
errors=0

fail() { echo "FAIL: $*"; errors=$((errors + 1)); }

WIRE="${SINA}/governance-brain-wire-v1.json"
ALIAS="${SINA}/brain-wire-v1.json"
CTX="${SINA}/governance-chat-context-v1.json"

[[ -f "$WIRE" ]] || fail "missing $WIRE — run brain_governance_wire_v1.py"
[[ -f "$ALIAS" ]] || fail "missing alias $ALIAS"

python3 - <<'PY' "$WIRE" || exit 1
import json, sys
wire = json.load(open(sys.argv[1]))
schema = wire.get("schema") or wire.get("schema_legacy")
if schema not in ("brain-wire-v1", "governance-brain-wire-v1"):
    raise SystemExit(f"bad schema: {schema}")
l2 = wire.get("l2_wired") or {}
agents = l2.get("agents") or []
if len(agents) < 4:
    raise SystemExit(f"l2_wired.agents count {len(agents)} < 4")
roles = {a.get("role") for a in agents}
need = {"worker", "researcher_l2", "maintainer_2", "maintainer_3"}
if not need.issubset(roles):
    raise SystemExit(f"missing L2 roles: {need - roles}")
qh = wire.get("queue_head") or {}
if not qh.get("sa_id") and not qh.get("queue_exhausted"):
    raise SystemExit("queue_head.sa_id missing (and queue not exhausted)")
print(f"OK: brain wire L2 agents={len(agents)} queue={qh.get('sa_id') or 'exhausted'}")
PY

[[ -f "${ROOT}/.cursor/rules/brain-wire-l2-mandatory.mdc" ]] || fail "missing brain-wire-l2-mandatory.mdc"
grep -q "agentic_layer_pipeline_v2.py" "${ROOT}/scripts/agent_session_gate_run_v1.py" || grep -q "brain_governance_wire_v1.py" "${ROOT}/scripts/agent_session_gate_run_v1.py" || fail "session gate missing pipeline/brain wire step"
grep -q "brain_l2_wire" "${ROOT}/scripts/worker_anti_staleness_heal_v1.py" || fail "worker AS-heal missing brain wire"
grep -q "l1_wired_to_brain" "${ROOT}/scripts/brain_governance_wire_v1.py" || fail "brain wire missing l1_wired_to_brain"
grep -q "brain_wire" "${ROOT}/scripts/agent_truth_bundle_v1.py" || fail "truth bundle missing brain_wire"
grep -q "Brain wire (mandatory" "${ROOT}/SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md" || fail "layer stack law missing L2 wire"

if [[ -f "$CTX" ]]; then
  python3 - <<'PY' "$CTX" || exit 1
import json, sys
ctx = json.load(open(sys.argv[1]))
sync = [t for t in ctx.get("threads") or [] if t.get("layer") == 2 and t.get("sync_before_reply")]
if len(sync) < 4:
    raise SystemExit(f"L2 threads with sync_before_reply: {len(sync)} < 4")
print(f"OK: chat context L2 sync threads={len(sync)}")
PY
fi

if [[ $errors -gt 0 ]]; then
  echo "FAIL: validate-brain-l2-wire-v1 ($errors)"
  exit 1
fi
echo "OK: validate-brain-l2-wire-v1"
