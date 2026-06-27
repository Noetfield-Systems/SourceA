#!/usr/bin/env bash
# Validate portfolio next 6000 — counts only (Mac-safe)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 - "$ROOT" <<'PY'
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
master = json.loads((root / "brain-os/plan-registry/PORTFOLIO_NEXT_6000_MASTER_v1.json").read_text())
if master.get("plan_count") != 6000:
    raise SystemExit(f"FAIL: plan_count {master.get('plan_count')}")
pack = root / "brain-os/plan-registry/portfolio-next-6000"
total = 0
for repo in ["sourcea", "witnessbc", "noetfield", "trustfield", "virlux", "mono"]:
    reg = json.loads((pack / repo / "REGISTRY.json").read_text())
    n = reg.get("count", 0)
    if n != 1000:
        raise SystemExit(f"FAIL: {repo} count {n}")
    total += n
if total != 6000:
    raise SystemExit(f"FAIL: total {total}")
print(f"OK: portfolio-next-6000 · 6 repos · {total} plans")
PY
echo "validate-portfolio-next-6000-v1.sh: ALL PASS"
