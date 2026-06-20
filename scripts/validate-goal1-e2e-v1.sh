#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"
SCRIPTS="$ROOT/scripts"

_goal1_e2e_release() {
  python3 "$SCRIPTS/factory_validation_lock_v1.py" release --holder goal1_e2e --pid "$$" --json >/dev/null 2>&1 || true
}
trap _goal1_e2e_release EXIT

if ! python3 "$SCRIPTS/factory_validation_lock_v1.py" assert-clear --for goal1_e2e --json | python3 -c "import json,sys; assert json.load(sys.stdin)['ok']"; then
  echo "FAIL: goal1 E2E blocked — full E2E or goal1 auto-run in progress"
  python3 "$SCRIPTS/factory_validation_lock_v1.py" status --json 2>/dev/null || true
  exit 1
fi
if ! python3 "$SCRIPTS/factory_validation_lock_v1.py" acquire --holder goal1_e2e --pid "$$" --json | python3 -c "import json,sys; assert json.load(sys.stdin)['ok']"; then
  echo "FAIL: factory lock acquire goal1_e2e"
  exit 1
fi
echo "OK: factory lock acquired (goal1_e2e)"

python3 "$SCRIPTS/factory_control_v1.py" resume --max-turns 2 --trigger "validate-goal1-e2e-v1" --json >/dev/null \
  || { echo "FAIL: resume token for e2e deliver"; exit 1; }

bash scripts/validate-goal1-lane-broker-v1.sh
bash scripts/validate-healthy-drain-orchestrator-v1.sh
bash scripts/validate-worker-inbox-delivery-v1.sh
python3 -c "
import sys
sys.path.insert(0, 'scripts')
from healthy_pack_bind_lib_v1 import heal_bind_mismatch
heal_bind_mismatch(force_deliver=False)
"
bash scripts/validate-goal1-loop-activation-chain-v1.sh

python3 <<'PY'
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(".")
fail = 0


def run(cmd, **kw):
    return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, **kw)


def ok(name, cond, detail=""):
    global fail
    if cond:
        print(f"PASS: {name}" + (f" — {detail}" if detail else ""))
    else:
        print(f"FAIL: {name}" + (f" — {detail}" if detail else ""))
        fail = 1


for f in ("start_goal1_worker_turn_v1.py", "brain_execute_turn_v1.py"):
    ok(f"exists {f}", (ROOT / "scripts" / f).is_file())

feas = json.loads(run([sys.executable, "scripts/prompt_feasibility_gate.py", "--role", "worker", "--json"]).stdout)
ok("feasibility not STOP_INJECT", feas.get("action") != "STOP_INJECT", feas.get("action"))

sys.path.insert(0, str(ROOT / "scripts"))
from duplicate_inject_guard_v1 import clear_inject_lock  # noqa: E402
from worker_inject_lib import clear_inbox  # noqa: E402

run([sys.executable, "scripts/healthy-drain-orchestrator-v1.py", "reset"])
clear_inbox(reason="validate_goal1_e2e")
clear_inject_lock()
from healthy_pack_bind_lib_v1 import heal_bind_mismatch  # noqa: E402

heal = heal_bind_mismatch(force_deliver=False)
ok("bind heal", heal.get("ok"), str(heal.get("status") or heal.get("error")))
# E2E must not fail when pack cursor exhausted (next_pos > queue_total).
state_path = Path.home() / ".sina" / "healthy-queue-state-v1.json"
try:
    from healthy_queue_ssot_lib import first_open_queue_pos  # noqa: E402

    pos = first_open_queue_pos()
except Exception:
    pos = 1
state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
state["next_pos"] = pos if pos <= 30 else 1
state_path.parent.mkdir(parents=True, exist_ok=True)
state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
deliver = json.loads(run([sys.executable, "scripts/healthy-drain-orchestrator-v1.py", "deliver", "--force"]).stdout)
ok("deliver", deliver.get("ok"), deliver.get("queue", {}).get("item", {}).get("sa_id"))

from active_now_v1 import sync_active_now_from_queue_head  # noqa: E402

sync = sync_active_now_from_queue_head()
ok("active_now sync", sync.get("ok"), str(sync.get("error") or sync.get("active_now", {}).get("queue_pos")))

inbox = json.loads(run([sys.executable, "scripts/worker_inject_lib.py", "--status"]).stdout)
ok("inbox pending", inbox.get("pending"))

dry = json.loads(run([sys.executable, "scripts/start_goal1_worker_turn_v1.py", "--dry-run"]).stdout)
ok("agent dry-run", dry.get("ok"), dry.get("sa_id"))

poll = json.loads(run([sys.executable, "scripts/goal1_lane_broker.py", "brain-poll", "--json"]).stdout)
ok("broker poll", poll.get("status") == "BRAIN_BROKER_POLL", poll.get("action"))

sys.exit(fail)
PY

python3 <<'PY'
import sys
sys.path.insert(0, "scripts")
from duplicate_inject_guard_v1 import clear_inject_lock  # noqa: E402
from healthy_pack_bind_lib_v1 import clear_stale_turn_bind  # noqa: E402
from worker_inject_lib import clear_inbox  # noqa: E402

clear_inbox(reason="validate_goal1_e2e_done")
clear_inject_lock()
clear_stale_turn_bind()
PY

echo "OK: validate-goal1-e2e-v1 — dry-run path only; live agent -p -f NOT proven here"
