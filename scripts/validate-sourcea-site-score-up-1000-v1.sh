#!/usr/bin/env bash
# Validate SourceA site score-up 1000 plan pack.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PACK="$ROOT/brain-os/plan-registry/sourcea-site-score-up-1000"
REG="$PACK/REGISTRY.json"
MASTER="$ROOT/brain-os/plan-registry/SOURCEA_SITE_SCORE_UP_1000_MASTER_v1.json"
LAW="$ROOT/docs/SOURCEA_SITE_SCORE_UP_1000_PLANS_LOCKED_v1.md"

echo "=== validate-sourcea-site-score-up-1000-v1 ==="
test -f "$LAW" || { echo "FAIL: missing law doc"; exit 1; }
test -f "$REG" || { echo "FAIL: missing REGISTRY — run generator"; exit 1; }
test -f "$MASTER" || { echo "FAIL: missing master"; exit 1; }

python3 - <<'PY'
import json, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1] if False else Path(".")
pack = Path("brain-os/plan-registry/sourcea-site-score-up-1000")
reg = json.loads((pack / "REGISTRY.json").read_text())
plans = reg.get("plans", [])
if reg.get("count") != 1000 or len(plans) != 1000:
    print(f"FAIL: count {reg.get('count')} plans {len(plans)}")
    sys.exit(1)
ids = [p["id"] for p in plans]
if len(ids) != len(set(ids)):
    print("FAIL: duplicate ids")
    sys.exit(1)
for p in plans[:3]:
    if not (pack / p["path"]).is_file():
        print(f"FAIL: missing {p['path']}")
        sys.exit(1)
now = sum(1 for p in plans if p.get("phase") == "NOW")
print(f"OK: 1000 plans · NOW={now} · baseline={reg.get('baseline_score')} target={reg.get('target_score')}")
PY

echo "validate-sourcea-site-score-up-1000-v1.sh: PASS"
