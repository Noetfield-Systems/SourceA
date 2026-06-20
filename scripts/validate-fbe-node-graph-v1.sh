#!/usr/bin/env bash
# validate-fbe-node-graph-v1.sh — FBE graph SSOT + 76 line nodes + dry-run
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

GRAPH="data/fbe_node_graph_v1.json"
[[ -f "$GRAPH" ]] || { echo "FAIL: missing $GRAPH — run fbe_compile_node_graph_v1.py --write"; exit 1; }

python3 - <<'PY' || fail=1
import json
from pathlib import Path
g = json.loads(Path("data/fbe_node_graph_v1.json").read_text())
assert g.get("schema") == "fbe-node-graph-v1", "bad schema"
assert g.get("line_node_count") == 76, f"line_node_count {g.get('line_node_count')}"
assert g.get("graph_total_nodes") == 80, f"graph_total_nodes {g.get('graph_total_nodes')}"
counts = g.get("counts") or {}
assert counts.get("refinery") == 36, f"refinery {counts.get('refinery')}"
assert counts.get("assembly") == 22, f"assembly {counts.get('assembly')}"
assert counts.get("motor") == 18, f"motor {counts.get('motor')}"
assert counts.get("meta") == 4, f"meta {counts.get('meta')}"
ids = set()
line_nodes = 0
meta_nodes = 0
for tier in g.get("tiers") or []:
    for node in tier.get("nodes") or []:
        nid = node.get("id")
        assert nid, "node missing id"
        assert nid not in ids, f"duplicate {nid}"
        ids.add(nid)
        if node.get("line") == "meta":
            meta_nodes += 1
        else:
            line_nodes += 1
        if node.get("required", True) and node.get("line") != "meta":
            assert node.get("cmd"), f"node {nid} missing cmd"
assert line_nodes == 76, f"tier line nodes {line_nodes}"
assert meta_nodes == 4, f"tier meta nodes {meta_nodes}"
edges = g.get("edges") or []
assert len(edges) >= 17, f"too few edges {len(edges)}"
pg = g.get("parallel_groups") or []
assert len(pg) >= 6, f"parallel_groups {len(pg)}"
print(f"OK: fbe graph line_nodes={line_nodes} total={len(ids)} edges={len(edges)}")
PY

echo "=== FBE dry-run runner ==="
python3 scripts/fbe_pipeline_runner_v1.py --dry-run --json >/dev/null || fail=1
echo "OK: fbe_pipeline_runner dry-run"

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-fbe-node-graph-v1"
  exit 0
fi
echo "FAIL: validate-fbe-node-graph-v1"
exit 1
