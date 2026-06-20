#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PLAN="$ROOT/data/brain-cloud-reasoning-1000-upgrade-plan-v1.json"
fail() { echo "FAIL: $*" >&2; exit 1; }
[[ -f "$PLAN" ]] || fail "missing $PLAN"
python3 - <<'PY' "$PLAN" || fail "schema"
import json, sys
p = json.load(open(sys.argv[1]))
assert p.get("schema") == "brain-cloud-reasoning-1000-upgrade-plan-v1"
u = p.get("upgrades") or []
assert len(u) == 1000
assert u[0]["id"] == "B0001" and u[-1]["id"] == "B1000"
assert p.get("strategic_pivot", {}).get("real_blocker")
assert all(x.get("owner_role") == "brain" for x in u)
print("OK: brain-cloud 1000 plans", len(u), "P0", p["tier_counts"]["P0"])
PY
python3 scripts/brain_cloud_reasoning_plan_pulse_v1.py --json >/dev/null || fail "pulse"
echo "PASS: validate-brain-cloud-reasoning-1000-plan-v1"
