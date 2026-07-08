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
w2 = reg.get("w2_execution") or {}
ups = w2.get("upgrade_plans") or []
assert len(ups) == 10, f"w2 plans expected 10 got {len(ups)}"
for up in ups:
    steps = up.get("steps") or []
    assert len(steps) == 10, f"{up.get('id')} steps={len(steps)}"
    for i, st in enumerate(steps, start=1):
        ti = int(up["id"].split("-")[-1]) - 1
        wi = i - 1
        expected_seq = ti * 100 + wi * 10 + 1
        expected_id = f"sa-score-{expected_seq:04d}"
        assert st.get("sa_score_id") == expected_id, (up.get("id"), st.get("sa_score_id"), expected_id)
print(f"OK: 1000 plans · W2 {len(ups)}×10 · NOW={now} · baseline={reg.get('baseline_score')} target={reg.get('target_score')}")
PY

cd "$ROOT" && python3 scripts/sourcea_site_score_w2_pulse_v1.py --json >/dev/null 2>&1 || true

echo "validate-sourcea-site-score-up-1000-v1.sh: PASS"
