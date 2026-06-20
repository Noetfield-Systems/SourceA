#!/usr/bin/env bash
# validate-witnessbc-competitor-1000-v1.sh — WitnessBC pack smoke
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REG="$ROOT/witnessbc-site/os/plan-library/witnessbc-competitor-1000/REGISTRY.json"
test -f "$REG" || { echo "FAIL missing REGISTRY"; exit 1; }
python3 -c "import json; d=json.load(open('$REG')); assert d['count']==1000; assert d.get('schema_version')==2"
echo "PASS witnessbc-competitor-1000 smoke"
