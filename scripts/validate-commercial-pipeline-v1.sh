#!/usr/bin/env bash
# validate-commercial-pipeline-v1.sh — AB1/NW1 pipeline SSOT + hub wire
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
SINA="${HOME}/.sina"
PIPE="${SINA}/commercial-pipeline-v1.jsonl"
GLANCE="${SINA}/commercial-pipeline-glance-v1.json"

fail() { echo "FAIL: validate-commercial-pipeline-v1 — $*" >&2; exit 1; }

[[ -f "$ROOT/scripts/commercial_pipeline_v1.py" ]] || fail "missing commercial_pipeline_v1.py"

python3 - <<'PY' || fail "import commercial_pipeline_v1"
import importlib.util
from pathlib import Path
spec = importlib.util.spec_from_file_location('cp', 'scripts/commercial_pipeline_v1.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert hasattr(mod, 'pipeline_glance_payload')
assert hasattr(mod, 'sync_from_receipts')
print('OK: commercial_pipeline_v1 imports')
PY

grep -q 'commercial_pipeline' "$ROOT/scripts/worker_hub_v1.py" || fail "worker_hub_v1 missing commercial_pipeline wire"
grep -q 'commercial_agents_wire_v1' "$ROOT/scripts/worker_hub_v1.py" || fail "worker_hub_v1 missing commercial_agents wire"
[[ -f "$ROOT/scripts/commercial_reply_qualification_agent_v1.py" ]] || fail "missing reply qualification agent"
[[ -f "$ROOT/scripts/mark_reply_followup_sent_v1.py" ]] || fail "missing mark_reply_followup_sent"
[[ -f "$ROOT/scripts/commercial_agents_wire_v1.py" ]] || fail "missing commercial_agents_wire_v1"
python3 - <<'PY' || fail "commercial_agents_wire import"
import importlib.util
spec = importlib.util.spec_from_file_location('caw', 'scripts/commercial_agents_wire_v1.py')
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
assert hasattr(mod, 'commercial_agent_payload')
assert hasattr(mod, 'run_commercial_action')
print('OK: commercial_agents_wire_v1 imports')
PY

OUT="$(python3 "$ROOT/scripts/commercial_pipeline_v1.py" --sync --json)"
echo "$OUT" | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('ok') is True
g = d.get('glance') or {}
assert g.get('schema') == 'commercial-pipeline-glance-v1'
assert 'counts' in g
assert 'AB1' in (g.get('lanes') or [])
print('OK: sync + glance', g.get('headline'))
"

[[ -f "$GLANCE" ]] || fail "glance cache not written"
[[ -f "$PIPE" ]] || fail "pipeline jsonl not created"

echo "PASS: validate-commercial-pipeline-v1"
