#!/usr/bin/env bash
# validate-loop-specialist-v1.sh — CL10 Auto Runtime specialist + advisory circle
set -euo pipefail
cd "$(dirname "$0")/.."
SINA="${HOME}/.sina"

fail() { echo "FAIL: validate-loop-specialist-v1 — $*" >&2; exit 1; }

test -f scripts/loop_specialist_tick_v1.py || fail "missing loop_specialist_tick_v1.py"
test -f scripts/future_loop_prompt_advisory_circle_v1.py || fail "missing advisory circle"
test -f data/loop-specialist-cloud-contract-v1.json || fail "missing cloud contract"
grep -q 'loop_specialist_tick' scripts/disk_live_wire_sync_v1.py || fail "disk_live_wire must call Auto Runtime specialist"
grep -q 'loop_specialist' scripts/worker_hub_v1.py || fail "worker_hub must expose loop_specialist slice"

python3 scripts/future_loop_prompt_advisory_circle_v1.py --json >/dev/null || fail "advisory run"

python3 - <<'PY' || fail "advisory schema + stable hash"
import json
from pathlib import Path

p = Path.home() / ".sina/future-loop-prompt-advisory-v1.json"
r1 = json.loads(p.read_text())
if r1.get("schema") != "future-loop-prompt-advisory-v1":
    raise SystemExit("bad advisory schema")
if not r1.get("deterministic_hash"):
    raise SystemExit("missing deterministic_hash")
plan = json.loads(Path("data/outbound-factory-100-upgrade-plan-v1.json").read_text())
pending = [u for u in (plan.get("upgrades") or []) if u.get("status") != "done"]
if pending and not r1.get("ranked_prompts"):
    raise SystemExit("missing ranked_prompts while plan has pending upgrades")
import subprocess
subprocess.check_call(["python3", "scripts/future_loop_prompt_advisory_circle_v1.py", "--json"], stdout=subprocess.DEVNULL)
r2 = json.loads(p.read_text())
if r1.get("deterministic_hash") != r2.get("deterministic_hash"):
    raise SystemExit("deterministic_hash unstable on re-run")
print(f"OK: advisory hash={r1.get('deterministic_hash')}")
PY

python3 scripts/loop_specialist_tick_v1.py --json >/dev/null || fail "specialist tick run"

test -f "${SINA}/loop-specialist-tick-receipt-v1.json" || fail "missing tick receipt"
test -f "${SINA}/future-loop-prompt-advisory-v1.json" || fail "missing advisory receipt"
test -f "${SINA}/loop-specialist-config-v1.json" || fail "missing config"

python3 - <<'PY' || fail "tick receipt schema"
import json
from pathlib import Path

r = json.loads((Path.home() / ".sina/loop-specialist-tick-receipt-v1.json").read_text())
if r.get("schema") != "loop-specialist-tick-receipt-v1":
    raise SystemExit("bad tick schema")
dec = r.get("tick_decision")
allowed = {"observe_only", "compose_blocked", "dispatch_ready", "dispatch_done", "execute_pending", "idle", "auto_commercial"}
if dec not in allowed:
    raise SystemExit(f"bad tick_decision {dec}")
if not r.get("loop_specialist_line"):
    raise SystemExit("missing loop_specialist_line")
if r.get("execution_authority") is not False:
    raise SystemExit("specialist must not have execution_authority")
print(f"OK: tick_decision={dec}")
PY

python3 - <<'PY' || fail "auto_dispatch policy"
import json
from pathlib import Path

c = json.loads((Path.home() / ".sina/loop-specialist-config-v1.json").read_text())
enabled = c.get("loop_auto_dispatch_enabled")
if enabled is True:
    grad = Path.home() / ".sina/loop-auto-graduation-receipt-v1.json"
    if not grad.is_file():
        raise SystemExit("auto_dispatch true without graduation receipt")
    g = json.loads(grad.read_text())
    if not g.get("ok"):
        raise SystemExit("graduation receipt not ok")
    print("OK: auto_dispatch enabled via graduation")
elif enabled is not False:
    raise SystemExit("loop_auto_dispatch_enabled must be boolean false by default")
else:
    print("OK: auto_dispatch default false")
PY

python3 - <<'PY' || fail "advisory queue_head_pin"
import json
from pathlib import Path

adv = json.loads((Path.home() / ".sina/future-loop-prompt-advisory-v1.json").read_text())
hq_path = Path.home() / ".sina/healthy-queue-30-active.json"
if not hq_path.is_file():
    print("SKIP: no healthy queue")
    raise SystemExit(0)
hq = json.loads(hq_path.read_text())
queue = hq.get("queue") or []
if not queue:
    print("SKIP: empty queue")
    raise SystemExit(0)
head_uid = (queue[0] or {}).get("upgrade_id") or (queue[0] or {}).get("hp_id")
top = (adv.get("ranked_prompts") or [{}])[0]
top_uid = top.get("upgrade_id") or top.get("hp_id")
if head_uid and top_uid and head_uid != top_uid:
    raise SystemExit(f"queue head {head_uid} != advisory top {top_uid}")
if head_uid and not top.get("queue_head_pin"):
    raise SystemExit("top advisory missing queue_head_pin")
print(f"OK: queue_head_pin={head_uid}")
PY

bash scripts/validate-loop-observatory-v1.sh || fail "observatory cross-ref"

python3 - <<'PY' || fail "execute_pending when auto+outbound+inbox"
import json
from pathlib import Path

cfg = json.loads((Path.home() / ".sina/loop-specialist-config-v1.json").read_text())
if not cfg.get("loop_auto_dispatch_enabled"):
    print("SKIP: auto off")
    raise SystemExit(0)
inbox = json.loads((Path.home() / ".sina/worker-prompt-inbox-v1.json").read_text())
if not inbox.get("pending"):
    print("SKIP: inbox not pending")
    raise SystemExit(0)
hq = json.loads((Path.home() / ".sina/healthy-queue-30-active.json").read_text())
outbound = str(hq.get("thread") or "") == "OUTBOUND-FACTORY"
if not outbound:
    print("SKIP: not outbound drain")
    raise SystemExit(0)
tick = json.loads((Path.home() / ".sina/loop-specialist-tick-receipt-v1.json").read_text())
if tick.get("tick_decision") != "execute_pending":
    raise SystemExit(f"expected execute_pending got {tick.get('tick_decision')} blocks={tick.get('block_reasons')}")
print("OK: execute_pending under outbound auto loop")
PY

echo "PASS: validate-loop-specialist-v1"
