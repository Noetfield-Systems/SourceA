#!/usr/bin/env bash
# Validate SourceA site score-up batch-2 pack + zero overlap with batch-1 titles.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
B2="$ROOT/brain-os/plan-registry/sourcea-site-score-up-1000-batch2"
B1="$ROOT/brain-os/plan-registry/sourcea-site-score-up-1000"
LAW="$ROOT/docs/SOURCEA_SITE_SCORE_UP_1000_BATCH2_LOCKED_v1.md"

echo "=== validate-sourcea-site-score-up-1000-batch2-v1 ==="
test -f "$LAW" || { echo "FAIL: missing batch-2 law"; exit 1; }
test -f "$B2/REGISTRY.json" || { echo "FAIL: run batch-2 generator"; exit 1; }

python3 - <<'PY'
import json, sys
from pathlib import Path

b2p = Path("brain-os/plan-registry/sourcea-site-score-up-1000-batch2/REGISTRY.json")
b1p = Path("brain-os/plan-registry/sourcea-site-score-up-1000/REGISTRY.json")
b2 = json.loads(b2p.read_text())
plans = b2.get("plans", [])
if b2.get("count") != 1000 or len(plans) != 1000:
    print(f"FAIL: batch-2 count {b2.get('count')} plans {len(plans)}")
    sys.exit(1)
ids = [p["id"] for p in plans]
if len(ids) != len(set(ids)):
    print("FAIL: duplicate batch-2 ids")
    sys.exit(1)
if not all(p["id"].startswith("sa-score2-") for p in plans):
    print("FAIL: id prefix must be sa-score2-")
    sys.exit(1)
b1_titles = set()
if b1p.is_file():
    b1 = json.loads(b1p.read_text())
    b1_titles = {p["title"].lower().strip() for p in b1.get("plans", [])}
overlap = [p["title"] for p in plans if p["title"].lower().strip() in b1_titles]
if overlap:
    print(f"FAIL: {len(overlap)} titles overlap batch-1 e.g. {overlap[0]}")
    sys.exit(1)
for p in plans[:3]:
    if not (b2p.parent / p["path"]).is_file():
        print(f"FAIL: missing {p['path']}")
        sys.exit(1)
now = sum(1 for p in plans if p.get("phase") == "NOW")
print(f"OK: batch-2 1000 plans · NOW={now} · baseline={b2.get('baseline_score')} target={b2.get('target_score')} · batch-1 overlap=0")
PY

echo "validate-sourcea-site-score-up-1000-batch2-v1.sh: PASS"
