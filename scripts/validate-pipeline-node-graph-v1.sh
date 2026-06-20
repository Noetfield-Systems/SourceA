#!/usr/bin/env bash
# validate-pipeline-node-graph-v1.sh — graph SSOT + dry-run + receipt schema
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

GRAPH="data/sourcea_pipeline_node_graph_v1.json"
[[ -f "$GRAPH" ]] || { echo "FAIL: missing $GRAPH"; exit 1; }

python3 - <<'PY' || fail=1
import json
from pathlib import Path
g = json.loads(Path("data/sourcea_pipeline_node_graph_v1.json").read_text())
assert g.get("schema") == "sourcea-pipeline-node-graph-v1"
assert g.get("tiers"), "no tiers"
ids = set()
for tier in g["tiers"]:
    assert tier.get("id"), "tier missing id"
    for node in tier.get("nodes") or []:
        assert node.get("id"), "node missing id"
        assert node.get("cmd"), f"node {node.get('id')} missing cmd"
        assert node["id"] not in ids, f"duplicate node id {node['id']}"
        ids.add(node["id"])
print(f"OK: graph schema v1 tiers={len(g['tiers'])} nodes={len(ids)}")
# v1.2+ edges
ver = str(g.get("version") or "1.0")
if ver >= "1.2":
    pg = g.get("parallel_groups") or []
    edges = g.get("edges") or []
    if not pg:
        raise SystemExit("FAIL: v1.2 graph missing parallel_groups")
    if len(edges) < 10:
        raise SystemExit(f"FAIL: v1.2 graph too few edges ({len(edges)})")
    for node in ids:
        pass  # ids validated above
    print(f"OK: graph v1.2 parallel_groups={len(pg)} edges={len(edges)}")
PY

python3 - <<'PY' || fail=1
import json
from pathlib import Path
cpath = Path("data/sourcea_node_mesh_catalog_v1.json")
if not cpath.is_file():
    raise SystemExit("FAIL: missing mesh catalog")
c = json.loads(cpath.read_text())
assert c.get("schema") == "sourcea-node-mesh-catalog-v1"
g = json.loads(Path("data/sourcea_pipeline_node_graph_v1.json").read_text())
active = {n["id"] for n in c.get("active_nodes") or []}
graph_ids = {n["id"] for t in g["tiers"] for n in t.get("nodes") or []}
if active != graph_ids:
    raise SystemExit(f"FAIL: catalog active_nodes mismatch graph: cat-only={active-graph_ids} graph-only={graph_ids-active}")
print(f"OK: mesh catalog v1 active={len(active)} planned={len(c.get('planned_nodes') or [])}")
PY

python3 - <<'PY' || fail=1
import json
from pathlib import Path
g = json.loads(Path("data/sourcea_pipeline_node_graph_v1.json").read_text())
graph_ids = {n["id"] for t in g["tiers"] for n in t.get("nodes") or []}
mpath = Path("data/sourcea_directory_node_map_v1.json")
if not mpath.is_file():
    raise SystemExit("FAIL: missing data/sourcea_directory_node_map_v1.json")
m = json.loads(mpath.read_text())
assert m.get("schema") == "sourcea-directory-node-map-v1"
listed = set(m.get("graph_node_ids") or [])
missing = graph_ids - listed
if missing:
    raise SystemExit(f"FAIL: graph nodes not in directory map: {sorted(missing)}")
logical = {n["id"] for n in m.get("logical_nodes") or []}
all_nodes = listed | logical
for tier in g["tiers"]:
    for node in tier.get("nodes") or []:
        nid = node["id"]
        if nid not in all_nodes:
            raise SystemExit(f"FAIL: runner node {nid} not catalogued in directory map")
print(f"OK: directory map v1 planes={len(m.get('planes') or {})} logical={len(logical)} runtime={len(m.get('runtime_plane',{}).get('entries') or [])}")
PY

echo "=== Dry-run runner ==="
python3 scripts/pipeline_node_graph_runner_v1.py --dry-run --json >/dev/null || fail=1
echo "OK: pipeline_node_graph_runner dry-run"

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-pipeline-node-graph-v1"
  exit 0
fi
echo "FAIL: validate-pipeline-node-graph-v1"
exit 1
