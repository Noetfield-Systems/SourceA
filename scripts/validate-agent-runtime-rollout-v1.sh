#!/usr/bin/env bash
# validate-agent-runtime-rollout-v1.sh — load_bay_config + rollout fixture + prod lock
set -euo pipefail
cd "$(dirname "$0")/.."

test -f data/cloud-comprehension-bay-rollout-test-v1.json || { echo "FAIL missing rollout test fixture"; exit 1; }

export AGENT_RUNTIME_BAY_SSOT="data/cloud-comprehension-bay-rollout-test-v1.json"

python3 <<'PY'
import json
import os
import sys
from pathlib import Path

ROOT = Path(".")
sys.path.insert(0, str(ROOT / "scripts"))
from agent_runtime_config_v1 import load_bay_config  # noqa: WPS433

doc = json.loads((ROOT / os.environ["AGENT_RUNTIME_BAY_SSOT"]).read_text())
for fx in doc.get("fixtures") or []:
    cid = str(fx.get("context_id") or "")
    expect = str(fx.get("expect_variation_key") or "")
    cfg = load_bay_config("comprehension-loop-bay", context_id=cid)
    key = str(cfg.get("variation_key") or "")
    assert key == expect, (cid, key, expect)
    print(f"OK: rollout fixture {cid} -> {key}")

prod = json.loads((ROOT / "data/cloud-comprehension-bay-v1.json").read_text())
assert str(prod.get("active_variation_key") or "") == "default", prod
assert int((prod.get("rollout") or {}).get("percent") or 100) == 100, prod
print("OK: production active_variation_key=default rollout.percent=100")
PY

python3 scripts/test_agent_runtime_rollout_edges_v1.py

echo "PASS: validate-agent-runtime-rollout-v1"
