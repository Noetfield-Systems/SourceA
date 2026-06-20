#!/usr/bin/env bash
# validate-investigator-judge-loop-v1.sh — IJ10 investigator + judge loop room
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-investigator-judge-loop-v1 — $*" >&2; exit 1; }

test -f scripts/investigator_circle_run_v1.py || fail "missing investigator_circle_run_v1.py"
test -f scripts/judge_loop_room_v1.py || fail "missing judge_loop_room_v1.py"
test -f data/investigator-specialist-routing-v1.json || fail "missing routing json"
test -f data/investigator-self-heal-catalog-v1.json || fail "missing heal catalog"
test -f data/investigator-judge-cloud-contract-v1.json || fail "missing cloud contract"
grep -q 'investigator_circle' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire must call investigator"
grep -q 'judge_loop_room' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire must call judge loop"
grep -q 'investigator_room' scripts/worker_hub_v1.py || fail "worker_hub must expose investigator_room"
grep -q 'judge_room' scripts/worker_hub_v1.py || fail "worker_hub must expose judge_room"
grep -q '/api/investigator-circle/tick/v1' scripts/sina-command-server.py || fail "hub missing investigator route"
grep -q '/api/judge-loop/tick/v1' scripts/sina-command-server.py || fail "hub missing judge-loop route"

python3 scripts/investigator_circle_run_v1.py --json >/dev/null || fail "investigator run"
python3 scripts/judge_loop_room_v1.py --json >/dev/null || fail "judge loop run"

test -f "${SINA}/loop-health-investigation-receipt-v1.json" || fail "missing investigation receipt"
test -f "${SINA}/judge-loop/latest-verdict-v1.json" || fail "missing judge-loop verdict"

python3 - <<'PY' || fail "receipt schemas"
import json
from pathlib import Path

inv = json.loads((Path.home() / ".sina/loop-health-investigation-receipt-v1.json").read_text())
if inv.get("schema") != "loop-health-investigation-receipt-v1":
    raise SystemExit("bad investigation schema")
if inv.get("investigation_verdict") not in ("GREEN", "YELLOW", "RED"):
    raise SystemExit("bad investigation_verdict")
if inv.get("execution_authority") is not False:
    raise SystemExit("investigator must not have execution_authority")
if not inv.get("investigator_line"):
    raise SystemExit("missing investigator_line")

jv = json.loads((Path.home() / ".sina/judge-loop/latest-verdict-v1.json").read_text())
if jv.get("schema") != "judge-loop-verdict-v1":
    raise SystemExit("bad judge-loop schema")
if jv.get("loop_verdict") not in ("LOOP_HEALTHY", "LOOP_DEGRADED", "DISPATCH_BLOCKED", "PROMPT_STALE"):
    raise SystemExit("bad loop_verdict")
if jv.get("execution_authority") is not False:
    raise SystemExit("judge loop must not have execution_authority")
if not jv.get("judge_loop_line"):
    raise SystemExit("missing judge_loop_line")
print(f"OK: inv={inv.get('investigation_verdict')} judge={jv.get('loop_verdict')}")
PY

bash scripts/validate-loop-observatory-v1.sh || fail "observatory cross-refs"

python3 - <<'PY' || fail "observatory investigator+judge cross-refs"
import json
from pathlib import Path

r = json.loads((Path.home() / ".sina/loop-observatory-report-v1.json").read_text())
for k in ("investigator", "judge_room"):
    if k not in r:
        raise SystemExit(f"observatory missing {k}")
print("OK: observatory investigator + judge_room slices")
PY

echo "PASS: validate-investigator-judge-loop-v1"
