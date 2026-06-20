#!/usr/bin/env bash
# validate-better-loop-v1.sh — Better Loop v2 machine wiring
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-better-loop-v1 — $*" >&2; exit 1; }

test -f scripts/better_loop_pulse_v1.py || fail "missing better_loop_pulse_v1.py"
test -f docs/SOURCEA_STACK_MAP_AND_BETTER_LOOP_LOCKED_v1.md || fail "missing stack map LOCKED doc"

grep -q 'better_loop' scripts/worker_hub_v1.py || fail "worker_hub must expose better_loop slice"
grep -q 'better_loop' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire_sync must set better_loop_line"
grep -q 'better_loop_pulse' scripts/agent_session_gate_run_v1.py || fail "session gate must call better_loop_pulse"

grep -q 'system_red_count' scripts/better_loop_pulse_v1.py || fail "pulse must emit system_red_count"
grep -q 'commercial_red_count' scripts/better_loop_pulse_v1.py || fail "pulse must emit commercial_red_count"

python3 scripts/better_loop_pulse_v1.py --init-cart >/dev/null || fail "init check cart"
test -f "${SINA}/better-loop-checkcart-v1.json" || fail "missing better-loop-checkcart-v1.json"

python3 scripts/better_loop_pulse_v1.py --json >/dev/null || fail "pulse run"
test -f "${SINA}/better-loop-pulse-receipt-v1.json" || fail "missing pulse receipt"

python3 - <<'PY' || fail "receipt freshness / schema"
import json
from datetime import datetime, timezone
from pathlib import Path

p = Path.home() / ".sina/better-loop-pulse-receipt-v1.json"
r = json.loads(p.read_text())
if r.get("schema") != "better-loop-pulse-receipt-v1":
    raise SystemExit("bad schema")
at = r.get("at") or ""
if not at.endswith("Z"):
    raise SystemExit("missing at")
ts = datetime.strptime(at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
age_h = (datetime.now(timezone.utc) - ts).total_seconds() / 3600
if age_h > 24:
    raise SystemExit(f"receipt stale {age_h:.1f}h")
if not r.get("better_loop_line"):
    raise SystemExit("missing better_loop_line")
print(f"OK: receipt fresh {age_h:.2f}h red={r.get('red_count')}")
if "system_red_count" not in r or "commercial_red_count" not in r:
    raise SystemExit("missing red taxonomy fields")
print(f"OK: taxonomy sys={r.get('system_red_count')} comm={r.get('commercial_red_count')}")
PY

test -f "${SINA}/agent-live-surfaces-v1.json" || fail "run disk_live_wire_sync first"
python3 - <<'PY' || fail "agent-live-surfaces missing better_loop_line"
import json
from pathlib import Path
s = json.loads((Path.home() / ".sina/agent-live-surfaces-v1.json").read_text())
if not s.get("better_loop_line"):
    raise SystemExit("better_loop_line missing — run disk_live_wire_sync")
print("OK: better_loop_line on live surfaces")
PY

test -f scripts/best_loop_oqg_score_v1.py || fail "missing best_loop_oqg_score_v1.py"
test -f docs/SOURCEA_BEST_LOOP_OUTPUT_QUALITY_GATE_LOCKED_v1.md || fail "missing OQG LOCKED doc"
grep -q 'best_loop_oqg' scripts/worker_hub_v1.py || fail "worker_hub must expose best_loop_oqg slice"
grep -q 'best_loop_oqg_line' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire_sync must set best_loop_oqg_line"
grep -q 'output_quality' scripts/better_loop_pulse_v1.py || fail "pulse must embed output_quality"
grep -q 'nerve_system' scripts/agent_session_gate_run_v1.py || fail "session gate must call nerve_system step"

python3 scripts/best_loop_oqg_score_v1.py --json >/dev/null || fail "oqg score run"
test -f "${SINA}/best-loop-oqg-receipt-v1.json" || fail "missing best-loop-oqg-receipt-v1.json"

python3 - <<'PY' || fail "oqg receipt schema"
import json
from pathlib import Path
r = json.loads((Path.home() / ".sina/best-loop-oqg-receipt-v1.json").read_text())
if r.get("schema") != "best-loop-oqg-receipt-v1":
    raise SystemExit("bad oqg schema")
if r.get("metric") != "output_clean_pct":
    raise SystemExit("wrong metric")
if not r.get("best_loop_oqg_line"):
    raise SystemExit("missing best_loop_oqg_line")
w3 = next((l for l in r.get("lanes") or [] if l.get("lane") == "w3_commercial"), None)
if not w3:
    raise SystemExit("missing w3_commercial lane")
print(f"OK: oqg fleet={r.get('fleet_output_clean_pct')}% w3={w3.get('output_clean_pct')}%")
PY

echo "PASS: validate-better-loop-v1"
bash scripts/validate-forge-vocabulary-disambiguation-v1.sh || fail "forge vocabulary drift"
bash scripts/validate-nerve-system-cart-v1.sh || fail "nerve cart validator"
