#!/usr/bin/env bash
# Unified authority convergence gate — P0 + P1 + boundary + LOCKED doc.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

LOCKED="$ROOT/brain-os/system/AUTHORITY_RUNTIME_VERIFICATION_LOCKED_v1.md"
test -f "$LOCKED"

bash "$ROOT/scripts/validate-authority-p1-v1.sh"
bash "$ROOT/scripts/run-rail-a-boundary-test-v1.sh" >/dev/null
bash "$ROOT/scripts/validate-master-operating-tracker-v1.sh"

python3 <<PY
import sys
from pathlib import Path

root = Path("${ROOT}")
sys.path.insert(0, str(root / "scripts"))
from authority_enforce_p1_lib import DEFAULT_GOVERNANCE_TRACES, _load_reconciled

row = _load_reconciled()
cited = row.get("trace_ids_cited") or []
for tid in DEFAULT_GOVERNANCE_TRACES:
    assert tid in cited, (tid, cited)
assert str(row.get("next_sa") or "").startswith("sa-"), row

events = Path.home() / ".sina/events"
day_files = sorted(events.glob("*.jsonl")) if events.is_dir() else []
assert day_files, "no event log yet — run boundary test or AUTO-RUN"

print("OK: validate-authority-convergence-v1")
PY

echo "LOCKED: brain-os/system/AUTHORITY_RUNTIME_VERIFICATION_LOCKED_v1.md"
