#!/usr/bin/env bash
# validate-loop-observatory-v1.sh — OL10 loop observatory receipt + freeze coherence
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-loop-observatory-v1 — $*" >&2; exit 1; }

test -f scripts/loop_observatory_report_v1.py || fail "missing loop_observatory_report_v1.py"
grep -q 'loop_observatory_report' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire_sync must call loop observatory"

python3 scripts/loop_observatory_report_v1.py --json >/dev/null || fail "observatory run"
test -f "${SINA}/loop-observatory-report-v1.json" || fail "missing loop-observatory-report-v1.json"

python3 - <<'PY' || fail "receipt schema / keys"
import json
from datetime import datetime, timezone
from pathlib import Path

p = Path.home() / ".sina/loop-observatory-report-v1.json"
r = json.loads(p.read_text())
need = ("schema", "at", "system", "product", "commercial", "founder_one_line", "freeze", "advisory", "loop_specialist")
for k in need:
    if k not in r:
        raise SystemExit(f"missing key {k}")
if r.get("schema") != "loop-observatory-report-v1":
    raise SystemExit("bad schema")
at = r.get("at") or ""
if not at.endswith("Z"):
    raise SystemExit("missing at")
ts = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
age_h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
if age_h > 24:
    raise SystemExit(f"receipt stale {age_h:.1f}h")
if not r.get("founder_one_line"):
    raise SystemExit("missing founder_one_line")
comm = r.get("commercial") or {}
if "compile_order" not in comm:
    raise SystemExit("missing commercial compile_order")
print(f"OK: observatory fresh {age_h:.2f}h line={r['founder_one_line'][:72]}")
PY

python3 - <<'PY' || fail "freeze coherence"
import json
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from worker_inject_lib import act_blocked_by_freeze  # noqa: E402

r = json.loads((Path.home() / ".sina/loop-observatory-report-v1.json").read_text())
freeze = r.get("freeze") or {}
act = act_blocked_by_freeze(queue_role="act")
expected_block = bool(act.get("prompt_blocked_by_freeze"))
if freeze.get("prompt_blocked_by_freeze") != expected_block:
    raise SystemExit(
        f"freeze incoherent blocked={freeze.get('prompt_blocked_by_freeze')} expected={expected_block}"
    )
if bool(freeze.get("outbound_queue_override")) != bool(act.get("outbound_queue_override")):
    raise SystemExit("outbound_queue_override mismatch observatory vs act_blocked")
print(f"OK: freeze coherence blocked={expected_block} outbound={bool(act.get('outbound_queue_override'))}")
PY

python3 - <<'PY' || fail "advisory + specialist cross-refs"
import json
from pathlib import Path

r = json.loads((Path.home() / ".sina/loop-observatory-report-v1.json").read_text())
adv = r.get("advisory") or {}
if not adv.get("compile_sequence"):
    raise SystemExit("observatory missing advisory.compile_sequence")
ls = r.get("loop_specialist") or {}
if "loop_auto_dispatch_enabled" not in ls:
    raise SystemExit("observatory missing loop_specialist.loop_auto_dispatch_enabled")
tick = Path.home() / ".sina/loop-specialist-tick-receipt-v1.json"
if not tick.is_file():
    raise SystemExit("missing loop-specialist-tick-receipt")
inv = r.get("investigator") or {}
if "investigation_verdict" not in inv:
    raise SystemExit("observatory missing investigator.investigation_verdict")
jr = r.get("judge_room") or {}
if "loop_verdict" not in jr:
    raise SystemExit("observatory missing judge_room.loop_verdict")
print("OK: observatory advisory + specialist + investigator + judge cross-refs")
PY

echo "PASS: validate-loop-observatory-v1"
