#!/usr/bin/env bash
# validate-newmatch-factory-v1.sh — NewMatch factory SSOT + graph + 999-plan + scripts gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
FAIL=0
fail() { echo "FAIL: newmatch-factory — $*" >&2; FAIL=1; }

[[ -f data/newmatch-factory-v1.json ]] || fail "missing SSOT"
[[ -f data/newmatch-graph-schema-v1.json ]] || fail "missing graph schema"
[[ -f data/NEWMATCH_FACTORY_PROPOSAL_LOCKED_v1.md ]] || fail "missing LOCKED proposal mirror"
[[ -f scripts/gen_newmatch_factory_999_plan_v1.py ]] || fail "missing generator"
[[ -f scripts/newmatch_situation_router_t0_v1.py ]] || fail "missing T0 router"
[[ -f scripts/newmatch_free_tier_check_v1.py ]] || fail "missing free-tier check"

python3 - <<'PY' || fail "SSOT fields"
import json
from pathlib import Path
ssot = json.loads(Path("data/newmatch-factory-v1.json").read_text())
assert ssot.get("status") == "LOCKED"
assert ssot.get("factory_id") == "newmatch_router_cloud"
assert ssot.get("graph_schema") == "data/newmatch-graph-schema-v1.json"
assert ssot.get("plan_999") == "data/newmatch-factory-999-plan-v1.json"
ft = ssot.get("free_tier_policy") or {}
assert ft.get("phase_0_cost_ceiling_usd") == 0, "phase_0 must be $0"
assert ssot.get("situation_engine", {}).get("t0_script")
assert ssot.get("api_contract", {}).get("endpoints")
print("OK: SSOT v1.2 locked + situation engine")
PY

[[ -f data/newmatch-factory-999-plan-v1.json ]] || fail "missing 999-plan — run gen_newmatch_factory_999_plan_v1.py"

python3 - <<'PY' || fail "999-plan shape"
import json
from pathlib import Path
doc = json.loads(Path("data/newmatch-factory-999-plan-v1.json").read_text())
plans = doc.get("plans") or []
assert len(plans) == 999, f"expected 999 plans got {len(plans)}"
assert doc.get("unique_titles") == 999, f"duplicate titles {doc.get('unique_titles')}"
assert doc.get("graph_schema") == "data/newmatch-graph-schema-v1.json"
ids = [p["id"] for p in plans]
assert ids[0] == "NM-001" and ids[-1] == "NM-999"
assert len(set(ids)) == 999
for p in plans:
    assert p.get("cloud_only") is True
    assert p.get("local_worker_allowed") is False
    assert p.get("free_tier_first") is True
    assert p.get("mvp_wave")
    assert p.get("signal_hint")
    assert p.get("route_hint")
free_n = doc.get("free_plan_count") or sum(1 for p in plans if p.get("marginal_cost_usd", 0) == 0)
assert free_n >= 700, f"expected >=700 free plans got {free_n}"
print(f"OK: 999 plans v1.2 free={free_n} P0={doc['tier_counts']['P0']}")
PY

python3 scripts/newmatch_situation_router_t0_v1.py --demo --json >/dev/null || fail "T0 router demo"
python3 scripts/newmatch_free_tier_check_v1.py --json >/dev/null || fail "free-tier check"
[[ -f apps/newmatch/data/graph-v1.json ]] || fail "missing apps/newmatch scaffold — run WORK NM-001"
bash scripts/validate-newmatch-scaffold-v1.sh >/dev/null || fail "scaffold validator"

grep -q 'Saved:.*T[0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z' data/NEWMATCH_FACTORY_PROPOSAL_LOCKED_v1.md || fail "LOCKED md missing exact UTC Saved"

echo "PASS: validate-newmatch-factory-v1"
exit "$FAIL"
