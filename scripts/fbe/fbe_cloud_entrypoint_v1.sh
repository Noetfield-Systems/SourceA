#!/usr/bin/env bash
# FBE cloud worker entrypoint — canonical copy (Wave 1 · ROOT=/app when copied to /entrypoint.sh)
set -euo pipefail
ROOT="${FBE_HOME:-/app}"
cd "$ROOT"

MODE="${1:-}"
BAY="${2:-sample-bay}"
GRAPH="data/fbe_node_graph_v1.json"
BUNDLE="data/fbe_factory_builder_bundle_v1.json"

validate_skeleton() {
  [[ -f "$GRAPH" ]] || { echo "FAIL: missing $GRAPH"; exit 1; }
  [[ -f "$BUNDLE" ]] || { echo "FAIL: missing $BUNDLE"; exit 1; }
  python3 -c "
import json
from pathlib import Path
g = json.loads(Path('$GRAPH').read_text())
assert g.get('schema') == 'fbe-node-graph-v1'
assert g.get('line_node_count') == 76
print('OK: fbe graph 76 nodes')
"
  echo "OK: fbe-worker-entrypoint skeleton"
}

run_bay() {
  local bay="${1:-sample-bay}"
  validate_skeleton
  export CREED_ROOT="${CREED_ROOT:-$HOME/Desktop/YA5/PLUS ONE/CREED}"
  echo "FBE W2 headless refinery bay=$bay"
  python3 scripts/fbe_refinery_runner_v1.py --bay "$bay" --json
  python3 scripts/fbe_verify_refinery_v1.py --bay "$bay" --json
  echo "OK: fbe-worker --run-bay $bay"
}

run_assembly() {
  local bay="${1:-sample-bay}"
  validate_skeleton
  export CHURCH_ROOT="${CHURCH_ROOT:-$HOME/Desktop/YA5/PLUS ONE/CHURCH}"
  echo "FBE W3 headless assembly bay=$bay"
  python3 scripts/fbe_assembly_runner_v1.py --bay "$bay" --json
  python3 scripts/fbe_verify_assembly_v1.py --bay "$bay" --json
  echo "OK: fbe-worker --run-assembly $bay"
}

run_exchange() {
  local bay="${1:-trustfield-bay}"
  validate_skeleton
  export CREED_ROOT="${CREED_ROOT:-$HOME/Desktop/YA5/PLUS ONE/CREED}"
  export CHURCH_ROOT="${CHURCH_ROOT:-$HOME/Desktop/YA5/PLUS ONE/CHURCH}"
  echo "FBE W4 exchange bay=$bay"
  python3 scripts/fbe_exchange_runner_v1.py --bay "$bay" --json
  python3 scripts/fbe_verify_exchange_v1.py --bay "$bay" --json
  echo "OK: fbe-worker --run-exchange $bay"
}

run_forge() {
  local bay="${1:-forge-bay}"
  validate_skeleton
  echo "FBE W5 headless forge bay=$bay"
  python3 scripts/fbe_forge_runner_v1.py --bay "$bay" --json
  python3 scripts/fbe_verify_forge_v1.py --bay "$bay" --json
  echo "OK: fbe-worker --run-forge $bay"
}

run_fleet() {
  local bay="${1:-sample-bay}"
  validate_skeleton
  echo "FBE W6 headless fleet bay=$bay"
  python3 scripts/fbe_run_fleet_v1.py --bay "$bay" --json
  echo "OK: fbe-worker --run-fleet $bay"
}

run_full_job() {
  local bay="${1:-sample-bay}"
  validate_skeleton
  echo "FBE full job bay=$bay"
  python3 scripts/fbe_run_job_v1.py --bay "$bay" --json
  echo "OK: fbe-worker --run-full-job $bay"
}

if [[ "$MODE" == "--serve-http" ]]; then
  validate_skeleton
  echo "FBE W6 headless HTTP worker (port ${PORT:-8080})"
  exec python3 scripts/fbe_cloud_worker_http_v1.py --port "${PORT:-8080}"
fi

if [[ "$MODE" == "--validate-only" ]]; then
  validate_skeleton
  exit 0
fi

if [[ "$MODE" == "--run-bay" ]]; then
  run_bay "$BAY"
  exit 0
fi

if [[ "$MODE" == "--run-assembly" ]]; then
  run_assembly "$BAY"
  exit 0
fi

if [[ "$MODE" == "--run-exchange" ]]; then
  run_exchange "$BAY"
  exit 0
fi

if [[ "$MODE" == "--run-forge" ]]; then
  run_forge "$BAY"
  exit 0
fi

if [[ "$MODE" == "--run-fleet" ]]; then
  run_fleet "$BAY"
  exit 0
fi

if [[ "$MODE" == "--run-full-job" ]]; then
  run_full_job "$BAY"
  exit 0
fi

echo "FBE worker — use --validate-only | --run-bay | --run-assembly | --run-exchange | --run-forge | --run-fleet | --run-full-job <slug>"
validate_skeleton
python3 scripts/fbe_pipeline_runner_v1.py --dry-run --json >/dev/null
echo "OK: dry-run delegate ready"
