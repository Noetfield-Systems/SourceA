#!/usr/bin/env bash
# sa-0651 — audit_hub_source_alignment Phase D regression guard wired
set -euo pipefail
cd "$(dirname "$0")"

python3 - <<'PY'
from pathlib import Path

src = Path("audit_hub_source_alignment.py").read_text(encoding="utf-8")
assert "_check_system_roadmap_phase_d_regression" in src, "Phase D regression helper missing"
assert "sa-0651" in src, "sa-0651 marker missing"
assert "future_phase" in src, "future_phase guard missing"
assert "!= 16" in src, "step_count 16 guard missing"
print("OK: validate-audit-hub-phase-d-regression-v1 · helper wired in audit_hub_source_alignment")
PY
