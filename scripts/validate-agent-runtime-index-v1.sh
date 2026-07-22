#!/usr/bin/env bash
# validate-agent-runtime-index-v1.sh — assert validator index scripts exist on disk
set -euo pipefail
cd "$(dirname "$0")/.."

python3 <<'PY'
import json
from pathlib import Path

ROOT = Path(".")
index = json.loads((ROOT / "data/agent-runtime-validator-index-v1.json").read_text())
missing = []
for name in (index.get("validators") or {}):
    path = ROOT / "scripts" / name
    if not path.is_file():
        missing.append(str(path))
for tier in (index.get("tiers") or {}).values():
    script = tier.get("script")
    if script and not (ROOT / script).is_file():
        missing.append(str(ROOT / script))
    for item in tier.get("includes") or tier.get("validators") or []:
        p = ROOT / item
        if not p.is_file():
            missing.append(str(p))
if missing:
    raise SystemExit("FAIL missing validator paths:\n  " + "\n  ".join(missing))
print("OK: validator index", len(index.get("validators") or {}), "entries on disk")
PY

echo "PASS: validate-agent-runtime-index-v1"
