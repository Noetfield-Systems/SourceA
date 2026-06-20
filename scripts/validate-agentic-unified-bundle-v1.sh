#!/usr/bin/env bash
# validate-agentic-unified-bundle-v1.sh — version pins · SSOT paths · station map
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
fail=0

BUNDLE="data/sourcea_agentic_unified_bundle_v1.json"
[[ -f "$BUNDLE" ]] || { echo "FAIL: missing $BUNDLE"; exit 1; }

python3 - <<'PY' || fail=1
import json
from pathlib import Path

ROOT = Path(".")
bundle = json.loads((ROOT / "data/sourcea_agentic_unified_bundle_v1.json").read_text())
if bundle.get("schema") != "sourcea-agentic-unified-bundle-v1":
    raise SystemExit("FAIL: bad unified bundle schema")

errors = []
ssot = bundle.get("ssot") or {}

def check_pin(key: str, path_key: str = "machine", version_key: str = "version"):
    row = ssot.get(key) or {}
    rel = row.get(path_key) or row.get("human")
    if not rel:
        return
    p = ROOT / rel
    if not p.is_file():
        errors.append(f"missing {rel} ({key})")
        return
    if path_key == "machine" and version_key in row:
        doc = json.loads(p.read_text())
        got = str(doc.get("version") or "")
        want = str(row[version_key])
        if got and got != want:
            errors.append(f"{rel} version {got} != bundle pin {want}")

for k in ("orient_routing", "node_graph", "mesh_catalog", "directory_map"):
    check_pin(k)

orient = json.loads((ROOT / "data/sourcea_orient_routing_v1.json").read_text())
stations = bundle.get("orientation_stations") or {}
reads = stations.get("reads") or []
if len(reads) < 14:
    errors.append("orientation_stations.reads too short")
lib_reads = len(orient.get("orientation_station_nodes") or {}) + len(reads)
if len(orient.get("pipeline_nodes") or {}) != 4:
    errors.append("orient_routing pipeline_nodes != 4")

graph = json.loads((ROOT / "data/sourcea_pipeline_node_graph_v1.json").read_text())
runner = sum(len(t.get("nodes") or []) for t in graph.get("tiers") or [])
if runner != bundle.get("graph_summary", {}).get("runner_nodes"):
    errors.append(f"graph runner count {runner} != bundle summary")

iu = bundle.get("identity_unify") or {}
apex = iu.get("apex_commercial") or {}
apex_h = apex.get("human")
if apex_h and not (ROOT / apex_h).is_file():
    errors.append(f"missing identity apex {apex_h}")
for layer in ("engine_story", "runtime_dispatch", "human_machine_form", "asset_commercial"):
    row = iu.get(layer) or {}
    h = row.get("human")
    if h and not (ROOT / h).is_file():
        errors.append(f"missing identity_unify.{layer} {h}")

if errors:
    raise SystemExit("FAIL unified bundle: " + "; ".join(errors))
print(f"OK: unified bundle v{bundle.get('version')} · SSOT pins match · stations={len(reads)} reads")
PY

if [[ $fail -eq 0 ]]; then
  echo "OK: validate-agentic-unified-bundle-v1"
  exit 0
fi
echo "FAIL: validate-agentic-unified-bundle-v1"
exit 1
