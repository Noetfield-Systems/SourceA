#!/usr/bin/env bash
# NM-001 — apps/newmatch scaffold gate (graph local JSON + schema mirror)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail() { echo "FAIL: validate-newmatch-scaffold-v1 — $*" >&2; exit 1; }

[[ -f apps/newmatch/README.md ]] || fail "missing apps/newmatch/README.md"
[[ -f apps/newmatch/package.json ]] || fail "missing package.json"
[[ -f apps/newmatch/data/graph-v1.json ]] || fail "missing data/graph-v1.json"
[[ -f apps/newmatch/schema/graph-v1.json ]] || fail "missing schema/graph-v1.json"

python3 - <<'PY'
import json
from pathlib import Path

graph = json.loads(Path("apps/newmatch/data/graph-v1.json").read_text())
assert graph.get("schema") == "newmatch-graph-local-v1"
assert graph.get("phase_0_cost_usd") == 0
assert graph.get("plan_step") == "NM-001"
for key in ("persons", "edges", "signals", "situations", "follow_ups"):
    assert key in graph, key
assert len(graph["persons"]) >= 1
assert graph["persons"][0].get("disclosure_tier") == "T4_internal"

mirror = json.loads(Path("apps/newmatch/schema/graph-v1.json").read_text())
canon = json.loads(Path("data/newmatch-graph-schema-v1.json").read_text())
assert mirror.get("schema") == canon.get("schema")
routes = mirror.get("entities", {}).get("situation", {}).get("routes", [])
assert "personal_nurture" in routes and "block" in routes
print("OK: graph local + schema mirror aligned")
PY

python3 scripts/newmatch_free_tier_check_v1.py --json >/dev/null || fail "free-tier check"
python3 scripts/newmatch_situation_router_t0_v1.py --demo --json >/dev/null || fail "T0 router demo"

echo "PASS: validate-newmatch-scaffold-v1 · apps/newmatch · NM-001"
