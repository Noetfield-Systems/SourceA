#!/usr/bin/env bash
# validate-video-ad-factory-runtime-v1.sh — runtime SSOT + golden batch (offline)
set -euo pipefail
cd "$(dirname "$0")/.."

test -f data/agent-runtime-factory-registry-v1.json || { echo "FAIL missing factory registry"; exit 1; }
test -f data/video-ad-factory-runtime-v1.json || { echo "FAIL missing runtime SSOT"; exit 1; }
test -f data/video-ad-factory-golden-v1.json || { echo "FAIL missing golden SSOT"; exit 1; }
test -f scripts/video_ad_factory_orchestrate_v1.py || { echo "FAIL missing orchestration"; exit 1; }

python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from agent_runtime_config_v1 import load_factory_runtime_config, factory_registry_entry

entry = factory_registry_entry("video-ad-factory-v1")
assert entry.get("ssot") == "data/video-ad-factory-runtime-v1.json"

cfg = load_factory_runtime_config("video-ad-factory-v1")
assert cfg.get("config_version"), cfg
assert cfg.get("variation_key") == "default", cfg
assert cfg.get("mock_llm") is True, cfg

prod = json.loads(Path("data/video-ad-factory-runtime-v1.json").read_text())
assert str(prod.get("active_variation_key")) == "default", prod
assert int((prod.get("rollout") or {}).get("percent") or 100) == 100, prod
print("OK: video-ad runtime config default variation")
PY

python3 scripts/video_ad_factory_eval_batch_v1.py --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('pass_rate', 0) >= 0.875, r
assert r.get('evaluated', 0) >= 3, r
print('OK: video-ad golden default', r.get('pass_rate'))
"

python3 scripts/video_ad_factory_eval_batch_v1.py --variation-key strong --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('pass_rate', 0) >= 0.875, r
print('OK: video-ad golden strong', r.get('pass_rate'))
"

python3 scripts/video_ad_factory_orchestrate_v1.py --seed-demo --no-write --json >/dev/null
python3 scripts/video_ad_factory_orchestrate_v1.py --no-write --campaign-id demo-campaign-v1 --json | python3 -c "
import json,sys
r=json.load(sys.stdin)
assert r.get('ok'), r
assert r.get('config_version'), r
assert r.get('variation_key'), r
print('OK: orchestration emits runtime config fields')
"

echo "PASS: validate-video-ad-factory-runtime-v1"
