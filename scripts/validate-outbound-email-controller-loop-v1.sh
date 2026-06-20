#!/usr/bin/env bash
# validate-outbound-email-controller-loop-v1.sh — OEGCC generator + controller
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"
FIX="scripts/fixtures/outbound-email-linter"

fail() { echo "FAIL: validate-outbound-email-controller-loop-v1 — $*" >&2; exit 1; }

test -f data/outbound-email-oegcc-v1.json || fail "missing SSOT"
test -f scripts/outbound_email_linter_v1.py || fail "missing linter"
test -f scripts/outbound_email_generator_v1.py || fail "missing generator"
test -f scripts/outbound_email_controller_v1.py || fail "missing controller"
bash scripts/validate-outbound-email-linter-v1.sh >/dev/null || fail "linter validator"

python3 - <<'PY' || fail "controller simulation"
import json
import sys
from pathlib import Path

ROOT = Path(".")
sys.path.insert(0, str(ROOT / "scripts"))
from outbound_email_controller_v1 import run_controller_loop, detect_oscillation
from outbound_email_generator_v1 import build_repair_user_prompt, GENERATOR_SYSTEM

FIX = ROOT / "scripts/fixtures/outbound-email-linter"
fail_opener = (FIX / "fail_opener.txt").read_text(encoding="utf-8")
pass_body = (FIX / "pass.txt").read_text(encoding="utf-8")
fail_long = (FIX / "fail_141words.txt").read_text(encoding="utf-8")

# Simulation: opener fail → pass on repair
def sim_fix(attempt, prior):
    return fail_opener if attempt == 1 else pass_body

result = run_controller_loop(sim_fix, case_id="validate-sim-fix", write_log=False)
if not result["receipt"].get("ok"):
    raise SystemExit(f"sim should pass: {result['receipt']}")
if result["receipt"].get("outcome") != "linter_pass_human_queue":
    raise SystemExit(f"wrong outcome: {result['receipt'].get('outcome')}")

# Oscillation detect unit
assert detect_oscillation([{"word_count"}, {"banned_opener"}, {"word_count"}])

# Repair prompt must quote failure and say keep rest
from outbound_email_linter_v1 import lint_email
lint_row = lint_email(fail_opener)
repair = build_repair_user_prompt(draft=fail_opener, lint_row=lint_row)
if "do not rewrite from scratch" not in repair.lower():
    raise SystemExit("repair missing patch instruction")
if "I noticed" not in repair:
    raise SystemExit("repair missing offending substring")
if "GENERATOR" not in GENERATOR_SYSTEM or "100 words" in GENERATOR_SYSTEM:
    pass
else:
    raise SystemExit("generator system missing word limit")

print("OK: controller sim · oscillation · repair prompt")
PY

python3 scripts/outbound_email_controller_v1.py --simulate --json >/dev/null || fail "CLI simulate"
test -f "${SINA}/outbound-email-controller-receipt-v1.json" || fail "missing controller receipt"

python3 - <<'PY' || fail "receipt never_auto_send"
import json
from pathlib import Path
r = json.loads((Path.home() / ".sina/outbound-email-controller-receipt-v1.json").read_text())
if not r.get("never_auto_send"):
    raise SystemExit("never_auto_send must be true")
if r.get("exit") != "human_queue":
    raise SystemExit("exit must be human_queue")
print("OK: receipt policy")
PY

python3 - <<'PY' || fail "commercial red map"
import json
from pathlib import Path
import sys
sys.path.insert(0, "scripts")
from oegcc_commercial_red_map_v1 import map_commercial_reds, probe_oegcc_linter_fail_ids
ids = probe_oegcc_linter_fail_ids()
if not ids or "banned_opener" not in ids:
    raise SystemExit(f"expected banned_opener in fail fixture ids: {ids}")
checks = [
    {"id": "w3_sina_read", "class": "commercial", "ok": False, "detail": "pending"},
    {"id": "oegcc_linter", "class": "commercial", "ok": True},
]
row = map_commercial_reds(checks)
if "ship_gate:w3_sina_read" not in row.get("rule_ids", []):
    raise SystemExit(row)
print("OK: commercial red map")
PY

python3 scripts/outbound_email_judge_v1.py \
  --body-file scripts/fixtures/outbound-email-linter/pass.txt \
  --json >/dev/null || fail "judge advisory"

echo "PASS: validate-outbound-email-controller-loop-v1"
