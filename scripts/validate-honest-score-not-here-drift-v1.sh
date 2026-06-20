#!/usr/bin/env bash
# sa-0076 / sa-0018 — honest_score not_here drift guard (eval + L8 structural_only)
set -euo pipefail
cd "$(dirname "$0")"
export PYTHONPATH="${PYTHONPATH:-}:$(pwd)"

bash validate-honest-score-not-here-v1.sh

python3 - <<'PY'
import audit_hub_source_alignment as audit
from system_roadmap import _build_world_target_map

assert hasattr(audit, "_check_honest_score_not_here_regression"), (
    "audit missing _check_honest_score_not_here_regression (sa-0076)"
)

errors: list[str] = []
audit._check_honest_score_not_here_regression(
    errors, {"world_target_map": _build_world_target_map()}
)
assert not errors, f"honest_score not_here drift: {errors}"

print("OK: validate-honest-score-not-here-drift-v1 · sa-0076 · audit regression · no L8/eval stale drift")
PY
