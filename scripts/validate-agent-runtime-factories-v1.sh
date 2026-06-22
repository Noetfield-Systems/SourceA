#!/usr/bin/env bash
# validate-agent-runtime-factories-v1.sh — registry + video-ad + noetfield copilot runtime gates
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY'
import json
from pathlib import Path

reg = json.loads(Path("data/agent-runtime-factory-registry-v1.json").read_text())
factories = reg.get("factories") or {}
for fid in (
    "comprehension-loop-factory-v1",
    "video-ad-factory-v1",
    "noetfield-copilot-factory-v1",
):
    row = factories.get(fid)
    assert row, f"missing {fid}"
    ssot = Path(row["ssot"])
    golden = Path(row["golden"])
    assert ssot.is_file(), ssot
    assert golden.is_file(), golden
    validator = Path(row["validator"])
    assert validator.is_file(), validator
print("OK: factory registry 3 factories SSOT+golden+validator")
PY

bash scripts/validate-video-ad-factory-runtime-v1.sh
bash scripts/validate-noetfield-copilot-runtime-v1.sh

echo "PASS: validate-agent-runtime-factories-v1"
