#!/usr/bin/env bash
# L1 → Brain pipeline — all first-layer subordinates wired TO Brain through machine Python
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
errors=0

fail() { echo "FAIL: $*"; errors=$((errors + 1)); }

PIPE="${SINA}/l1-agent-pipeline-wire-v1.json"
ALIAS="${SINA}/l1-brain-pipeline-wire-v1.json"
WIRE="${SINA}/governance-brain-wire-v1.json"
CTX="${SINA}/governance-chat-context-v1.json"

[[ -f "$PIPE" ]] || fail "missing $PIPE — run l1_agent_pipeline_wire_v1.py"
[[ -f "$ALIAS" ]] || fail "missing alias $ALIAS"
[[ -f "${ROOT}/scripts/l1_agent_pipeline_wire_v1.py" ]] || fail "missing l1_agent_pipeline_wire_v1.py"

python3 - <<'PY' "$PIPE" || exit 1
import json, sys
pipe = json.load(open(sys.argv[1]))
if pipe.get("schema") != "l1-agent-pipeline-wire-v1":
    raise SystemExit(f"bad schema: {pipe.get('schema')}")
if not pipe.get("brain_hub"):
    raise SystemExit("missing brain_hub")
l1b = pipe.get("l1_to_brain") or {}
subs = l1b.get("subordinates") or []
if len(subs) < 3:
    raise SystemExit(f"l1_to_brain.subordinates count {len(subs)} < 3")
for s in subs:
    if not s.get("wired_to_brain"):
        raise SystemExit(f"{s.get('role')} not wired_to_brain")
l1 = pipe.get("l1_wired") or {}
agents = l1.get("agents") or []
if len(agents) < 4:
    raise SystemExit(f"l1_wired.agents count {len(agents)} < 4")
shared = l1.get("shared") or {}
if not shared.get("brain_authority"):
    raise SystemExit("shared.brain_authority missing")
qh = shared.get("queue_head") or {}
if not qh.get("sa_id") and not qh.get("queue_exhausted"):
    raise SystemExit("shared.queue_head.sa_id missing (and queue not exhausted)")
print(f"OK: L1→Brain pipeline subs={len(subs)} queue={qh.get('sa_id') or 'exhausted'}")
PY

grep -qE "l1_agent_pipeline_wire_v1\.py|agentic_layer_pipeline_v2\.py" "${ROOT}/scripts/governance_center_run_v1.py" || fail "governance center missing L1 pipeline"
grep -q "l1_pipeline" "${ROOT}/scripts/agent_truth_bundle_v1.py" || fail "truth bundle missing l1_pipeline"
grep -q "l1_to_brain" "${ROOT}/scripts/l1_agent_pipeline_wire_v1.py" || fail "L1 pipeline missing l1_to_brain"
grep -q "brain_hub" "${ROOT}/scripts/l1_agent_pipeline_wire_v1.py" || fail "L1 pipeline missing brain_hub"
grep -q "wired TO Brain" "${ROOT}/SOURCEA_AGENTIC_LAYER_STACK_LOCKED_v2.md" || fail "layer stack missing L1→Brain law"
[[ -f "${ROOT}/.cursor/rules/l1-agent-pipeline-mandatory.mdc" ]] || fail "missing l1-agent-pipeline-mandatory.mdc"

if [[ -f "$WIRE" ]]; then
  python3 - <<'PY' "$WIRE" || exit 1
import json, sys
wire = json.load(open(sys.argv[1]))
if not wire.get("l1_pipeline"):
    raise SystemExit("brain wire missing l1_pipeline cross-ref")
print("OK: brain wire l1_pipeline cross-ref")
PY
fi

if [[ -f "$CTX" ]]; then
  python3 - <<'PY' "$CTX" || exit 1
import json, sys
ctx = json.load(open(sys.argv[1]))
sync = [t for t in ctx.get("threads") or [] if t.get("layer") == 1 and t.get("sync_before_reply")]
if len(sync) < 4:
    raise SystemExit(f"L1 threads with sync_before_reply: {len(sync)} < 4")
print(f"OK: chat context L1 sync threads={len(sync)}")
PY
fi

if [[ $errors -gt 0 ]]; then
  echo "FAIL: validate-l1-agent-pipeline-v1 ($errors)"
  exit 1
fi
echo "OK: validate-l1-agent-pipeline-v1"
