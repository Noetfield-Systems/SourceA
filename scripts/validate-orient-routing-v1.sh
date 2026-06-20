#!/usr/bin/env bash
# validate-orient-routing-v1.sh — orient chain · cascade SSOT · agent orient smoke
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

[[ -f data/sourcea_orient_routing_v1.json ]] || { echo "FAIL: missing orient routing SSOT"; exit 1; }
[[ -f docs/SOURCEA_ORIENTATION_AND_ROUTING_LOCKED_v1.md ]] || { echo "FAIL: missing orient routing doc"; exit 1; }

python3 - <<'PY' || fail=1
import json
from pathlib import Path
import sys
sys.path.insert(0, "scripts")
from orient_routing_v1 import validate_orient_routing, validate_orient_chain

r = validate_orient_routing()
if not r["ok"]:
    raise SystemExit("FAIL orient routing: " + "; ".join(r["errors"]))
c = validate_orient_chain()
print(f"OK: orient chain {c['count']} steps · validator_mappings={r['validator_mappings']}")
PY

echo "=== agent orient smoke ==="
python3 scripts/agent_orient_v1.py --role worker --json >/dev/null || fail=1
[[ -f ~/.sina/orient-routing-report-v1.json ]] || fail=1
python3 - <<'PY' || fail=1
import json
from pathlib import Path
r = json.loads(Path.home().joinpath(".sina/orient-routing-report-v1.json").read_text())
assert r.get("schema") == "orient-routing-report-v1"
assert "receipt_cascade" in r
assert "role_routing" in r
assert "node_mesh_brief" in r
assert "pipeline_nodes_brief" in r
assert len((r.get("pipeline_nodes_brief") or {}).get("pipelines") or []) >= 4
print(f"OK: orient report cascade_line={r.get('cascade_line')!r}")
PY

python3 - <<'PY' || fail=1
import json
from pathlib import Path
g = json.loads(Path("data/sourcea_pipeline_node_graph_v1.json").read_text())
lat = [t for t in g.get("tiers") or [] if t.get("id") == "T_lat_orient"]
if not lat or not (lat[0].get("nodes") or []):
    raise SystemExit("FAIL: graph missing T_lat_orient tier")
if lat[0]["nodes"][0].get("id") != "orient_routing_v1":
    raise SystemExit("FAIL: T_lat_orient first node must be orient_routing_v1")
print("OK: graph T_lat_orient wired")
PY

echo "=== unified bundle ==="
bash scripts/validate-agentic-unified-bundle-v1.sh || fail=1

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-orient-routing-v1"
  exit 0
fi
echo "FAIL: validate-orient-routing-v1"
exit 1
