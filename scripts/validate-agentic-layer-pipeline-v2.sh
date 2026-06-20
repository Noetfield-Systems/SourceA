#!/usr/bin/env bash
# Pipeline v2 validator — upgraded L0–L3 stack · health · cross-ref
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SINA="${HOME}/.sina"
errors=0

fail() { echo "FAIL: $*"; errors=$((errors + 1)); }

V2="${SINA}/agentic-layer-pipeline-v2.json"

[[ -f "${ROOT}/scripts/agentic_layer_pipeline_v2.py" ]] || fail "missing agentic_layer_pipeline_v2.py"
[[ -f "${ROOT}/scripts/agentic_pipeline_lib_v1.py" ]] || fail "missing agentic_pipeline_lib_v1.py"

python3 "${ROOT}/scripts/agentic_layer_pipeline_v2.py" --json --tier fast >/dev/null || fail "pipeline v2 run"

[[ -f "$V2" ]] || fail "missing $V2"

python3 - <<'PY' "$V2"
import json, sys
v2 = json.load(open(sys.argv[1]))
if v2.get("schema") != "agentic-layer-pipeline-v2":
    raise SystemExit(f"bad schema: {v2.get('schema')}")
if v2.get("version") != 2:
    raise SystemExit(f"bad version: {v2.get('version')}")
if not v2.get("ok"):
    raise SystemExit("pipeline v2 structural ok=false")
health = v2.get("health") or {}
if health.get("L1", {}).get("wired_to_brain", 0) < 3:
    raise SystemExit("L1 wired_to_brain < 3")
if health.get("L2", {}).get("agents", 0) < 4:
    raise SystemExit("L2 agents < 4")
if not v2.get("stack", {}).get("L1"):
    raise SystemExit("missing stack.L1")
print(f"OK: pipeline v2 health={health.get('status')} queue={(v2.get('brain_summary') or {}).get('queue_head')}")
PY

grep -q "agentic_layer_pipeline_v2" "${ROOT}/scripts/governance_center_run_v1.py" || fail "governance center missing v2"
grep -q "agentic_pipeline_v2" "${ROOT}/scripts/agent_truth_bundle_v1.py" || fail "truth bundle missing v2"

if [[ $errors -gt 0 ]]; then
  echo "FAIL: validate-agentic-layer-pipeline-v2 ($errors)"
  exit 1
fi
echo "OK: validate-agentic-layer-pipeline-v2"
