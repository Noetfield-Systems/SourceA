#!/usr/bin/env bash
# validate-deferred-excludes-scheduled-v1.sh — sa-0808 deferred vs scheduled_cadence pending_total
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

fail() { echo "FAIL: validate-deferred-excludes-scheduled-v1 — $*" >&2; exit 1; }

python3 - <<'PY' || fail "deferred vs scheduled"
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
from h2_pending_count_lib_v1 import count_h2_pending

reg_path = Path.home() / ".sina/h2-pending-registry-v1.json"
if not reg_path.is_file():
    raise SystemExit("missing h2-pending-registry-v1.json")

reg = json.loads(reg_path.read_text(encoding="utf-8"))
counts = count_h2_pending(reg)
deferred = list(reg.get("deferred") or [])
scheduled = list(reg.get("scheduled_cadence") or [])
deferred_ids = {r.get("id") for r in deferred if isinstance(r, dict)}
scheduled_ids = {r.get("id") for r in scheduled if isinstance(r, dict)}
overlap = deferred_ids & scheduled_ids
if overlap:
    raise SystemExit(f"deferred∩scheduled_cadence must be empty: {overlap}")
up_in_deferred = [r.get("id") for r in deferred if str(r.get("id", "")).startswith("UP-")]
if up_in_deferred:
    raise SystemExit(f"UP-* rows must not be in deferred: {up_in_deferred}")
# scheduled rows must not inflate pending_total (counted separately)
for rid in scheduled_ids:
    if rid in deferred_ids:
        raise SystemExit(f"scheduled id {rid} duplicated in deferred")

print(
    f"OK: validate-deferred-excludes-scheduled-v1 · pending={counts['pending_total']} "
    f"deferred={counts['deferred']} scheduled={counts['scheduled_total']} · no overlap"
)
PY

bash "$ROOT/scripts/validate-h2-pending-honest-count-v1.sh" >/dev/null || fail "h2 honest count"

echo "OK: validate-deferred-excludes-scheduled-v1 · sa-0808"
