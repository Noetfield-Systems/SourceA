#!/usr/bin/env bash
# Master Operating Tracker — structural + pointer consistency (fail closed).
# Law: brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

TRACKER="$ROOT/brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md"
test -f "$TRACKER"

# Section 1 must not contain unfilled Brain placeholders
if grep -q '\[Brain fills\]' "$TRACKER"; then
  echo "FAIL: tracker has unfilled [Brain fills] placeholders" >&2
  python3 -c "
import sys; sys.path.insert(0,'$ROOT/scripts')
from authority_enforce_p1_lib import mark_tracker_status
mark_tracker_status(status='STALE', reason='unfilled_section_placeholders')
"
  exit 1
fi

python3 <<PY
import json
import re
import sys
from pathlib import Path

root = Path("${ROOT}")
sys.path.insert(0, str(root / "scripts"))
from authority_enforce_p1_lib import load_pointer, mark_tracker_status

tracker = (root / "brain-os/system/SOURCEA_MASTER_OPERATING_TRACKER_LOCKED_v1.md").read_text(encoding="utf-8")
assert "Golden Rule" in tracker, "missing Golden Rule"
assert "SOURCEA MASTER OPERATING TRACKER" in tracker

pointer = load_pointer()
next_sa = str(pointer.get("next_sa") or "")
if next_sa.startswith("sa-"):
    assert next_sa in tracker, f"pointer {next_sa} not referenced in tracker executive snapshot"

mark_tracker_status(status="OK", reason="validate-master-operating-tracker-v1 PASS")
print("OK: validate-master-operating-tracker-v1")
print(f"pointer_ref: {next_sa}")
PY
