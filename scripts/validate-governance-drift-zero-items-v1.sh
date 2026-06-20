#!/usr/bin/env bash
# sa-0034 / sa-0084 — governance drift items must be 0 (DRIFT.json + aggregate pass)
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

bash validate-governance-drift-v1.sh

python3 - <<'PY'
import json
import re
from pathlib import Path

report_path = Path.home() / ".sina" / "governance_drift_report_v1.json"
assert report_path.is_file(), "missing governance_drift_report_v1.json"

report = json.loads(report_path.read_text(encoding="utf-8"))
aggregate = int(report.get("aggregate_score") or 0)
assert aggregate >= 85, f"aggregate_score below threshold: {aggregate}"

sensors = report.get("sensors") or []
bowl = next((s for s in sensors if s.get("id") == "GD-BOWL"), None)
assert bowl is not None, "missing GD-BOWL sensor"
assert bowl.get("ok") is True, bowl

detail = str(bowl.get("detail") or "")
m = re.search(r"(\d+)\s+drift item", detail)
drift_n = int(m.group(1)) if m else None
assert drift_n == 0, f"DRIFT.json drift items must be 0, got {detail!r}"

assert all(s.get("ok") for s in sensors[:4]), f"audit sensors not ok: {sensors[:4]}"
print(
    f"OK: validate-governance-drift-zero-items-v1 · score={aggregate} · "
    f"drift_items=0 · sensors={len(sensors)}"
)
PY
