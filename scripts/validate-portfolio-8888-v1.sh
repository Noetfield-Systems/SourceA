#!/usr/bin/env bash
# Validate portfolio 8888 master — 6000 next + 2888 fast-sell
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MASTER="$ROOT/data/portfolio-8888-master-manifest-v1.json"
test -f "$MASTER" || { echo "FAIL: missing $MASTER"; exit 1; }

python3 <<'PY'
import json
from pathlib import Path
root = Path(".")
master = json.loads((root / "data/portfolio-8888-master-manifest-v1.json").read_text())
assert master.get("plan_count") == 8888, master.get("plan_count")
next_base = root / "brain-os/plan-registry/portfolio-next-6000"
fs_base = root / "brain-os/plan-registry/portfolio-fast-sell-2888"
for repo in ["sourcea", "witnessbc", "noetfield", "trustfield", "virlux", "mono"]:
    reg = next_base / repo / "REGISTRY.json"
    doc = json.loads(reg.read_text())
    assert doc["count"] == 1000, (repo, doc["count"])
for lane in ["sourcea", "witnessbc", "noetfield", "trustfield", "virlux", "mono", "agency-b", "gtm-sku"]:
    reg = fs_base / lane / "REGISTRY.json"
    doc = json.loads(reg.read_text())
    assert doc["count"] == 361, (lane, doc["count"])
print("PASS: portfolio 8888 — 6000 next + 2888 fast-sell")
PY
