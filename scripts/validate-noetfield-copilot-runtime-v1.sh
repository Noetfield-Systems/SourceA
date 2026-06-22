#!/usr/bin/env bash
# validate-noetfield-copilot-runtime-v1.sh — copilot policy runtime + golden batch (offline)
set -euo pipefail
cd "$(dirname "$0")/.."

test -f data/noetfield-copilot-runtime-v1.json || { echo "FAIL missing runtime SSOT"; exit 1; }
test -f data/noetfield-copilot-golden-v1.json || { echo "FAIL missing golden SSOT"; exit 1; }
test -f scripts/noetfield_copilot_runtime_v1.py || { echo "FAIL missing runtime script"; exit 1; }

python3 <<'PY'
import sys
sys.path.insert(0, "scripts")
from agent_runtime_config_v1 import load_factory_runtime_config, factory_registry_entry

entry = factory_registry_entry("noetfield-copilot-factory-v1")
assert entry.get("bay_slug") == "noetfield-copilot-bay"

cfg = load_factory_runtime_config("noetfield-copilot-factory-v1")
assert cfg.get("policy_strictness") == "strict", cfg
assert "read" in (cfg.get("allowed_actions") or []), cfg
print("OK: noetfield copilot strict default config")
PY

python3 scripts/noetfield_copilot_runtime_v1.py --no-write --action read --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('verdict')=='ALLOW', r
assert r.get('config_version'), r
print('OK: copilot read ALLOW')
"

python3 scripts/noetfield_copilot_runtime_v1.py --no-write --action export_pii --payload '{"contains_pii":true}' --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('verdict')=='BLOCKED', r
print('OK: copilot PII BLOCKED')
"

python3 scripts/noetfield_copilot_eval_batch_v1.py --require-escalation-case --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('pass_rate', 0) >= 0.875, r
assert r.get('escalation_ok', 0) >= 1, r
print('OK: noetfield copilot golden default', r.get('pass_rate'))
"

python3 scripts/noetfield_copilot_eval_batch_v1.py --variation-key strong --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('pass_rate', 0) >= 0.875, r
print('OK: noetfield copilot golden strong', r.get('pass_rate'))
"

echo "PASS: validate-noetfield-copilot-runtime-v1"
