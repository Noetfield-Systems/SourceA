#!/usr/bin/env bash
# sa-0622 — honest_score built list includes Execution Spine
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

python3 - <<'PY'
from system_roadmap import _build_world_target_map

m = _build_world_target_map()
here = m.get("honest_score", {}).get("here") or []
built = m.get("reality_alignment", {}).get("built") or []

assert any("Execution Spine" in str(x) for x in here), here
assert "Execution Spine" in built, built

print("OK: validate-honest-score-execution-spine-v1 · honest_score.here + reality_alignment.built")
PY
