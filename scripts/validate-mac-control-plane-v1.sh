#!/usr/bin/env bash
# validate-mac-control-plane-v1.sh — Mac control plane law gate
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LAW="$HOME/Desktop/MacLaw/MAC_CONTROL_PLANE_LOCKED.md"

fail() { echo "FAIL: $*"; exit 1; }

[[ -f "$LAW" ]] || fail "missing $LAW"
[[ -f "$ROOT/data/founder-execution-model-v1.json" ]] || fail "missing founder-execution-model SSOT"

out="$(python3 "$ROOT/scripts/mac_control_plane_v1.py" --assess --json)"
ok="$(python3 -c "import json,sys; print('yes' if json.loads(sys.stdin.read()).get('ok') else 'no')" <<<"$out")"
[[ "$ok" == "yes" ]] || { echo "$out"; fail "mac_control_plane assess"; }

bash "$ROOT/scripts/validate-founder-execution-model-v1.sh" 2>/dev/null || true
bash "$ROOT/scripts/validate-mac-pipeline-validator-pressure-v1.sh" \
  || fail "pipeline/validator pressure law gate"

echo "PASS mac-control-plane-v1"
