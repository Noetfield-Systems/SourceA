#!/usr/bin/env bash
# sa-overnight-zero-spam — CHECK→API, duplicate guard, forward-only reconcile.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"

test -f "$ROOT/scripts/overnight_turn_guard_v1.py"
test -f "$ROOT/scripts/autorun_dispatcher_v1.py"
test -f "$ROOT/scripts/reconcile-queue-from-registry-v1.py"
test -f "$ROOT/scripts/healthy-drain-orchestrator-v1.py"

grep -q "role_engine" "$ROOT/scripts/autorun_dispatcher_v1.py"
grep -q "check_duplicate_turn" "$ROOT/scripts/autorun_dispatcher_v1.py"
grep -q "acquire_dispatch_lock" "$ROOT/scripts/autorun_dispatcher_v1.py"
grep -q "forward_only" "$ROOT/scripts/reconcile-queue-from-registry-v1.py"
grep -q "complete_overnight_turn" "$ROOT/scripts/healthy-drain-orchestrator-v1.py"
grep -q "cli_act_only" "$ROOT/scripts/claude_code_agent_v1.py"
test -f "$ROOT/scripts/healthy_prompt_turn_v1.py"
grep -q "healthy_prompt_turn_v1" "$ROOT/scripts/claude_code_agent_v1.py"
grep -q "healthy_prompt_turn_v1" "$ROOT/scripts/claude_api_agent_v1.py"
! grep -q "FREE_SLICE_SKIP" "$ROOT/scripts/autorun_dispatcher_v1.py"

python3 - <<'PY'
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path("scripts").resolve().parent
sys.path.insert(0, str(ROOT / "scripts"))
from overnight_turn_guard_v1 import GUARD_STATE, check_duplicate_turn, role_engine, record_turn

spec = importlib.util.spec_from_file_location(
    "reconcile_mod", ROOT / "scripts/reconcile-queue-from-registry-v1.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

assert role_engine("check") == "API", role_engine("check")
assert role_engine("verify") == "API", role_engine("verify")
assert role_engine("act") == "CLI", role_engine("act")
from overnight_turn_guard_v1 import is_cli_act_role
assert is_cli_act_role("act") is True
assert is_cli_act_role("check") is False
assert is_cli_act_role("verify") is False

guard_backup = GUARD_STATE.read_text() if GUARD_STATE.is_file() else None
record_turn(sa_id="sa-test", role="check", pos=1, engine="API", ok=True, cost_usd=0.01, status="PASS")
dup = check_duplicate_turn(sa_id="sa-test", role="check", pos=1)
assert dup.get("skip") is True, dup
if guard_backup:
    GUARD_STATE.write_text(guard_backup)
else:
    GUARD_STATE.unlink(missing_ok=True)

state = Path.home() / ".sina/healthy-queue-state-v1.json"
backup = state.read_text() if state.is_file() else None
state.parent.mkdir(parents=True, exist_ok=True)
state.write_text(json.dumps({"next_pos": 5}) + "\n")
row = mod.reconcile(apply=False, forward_only=True)
assert row.get("current_pos") == 5, row
if row.get("first_open_pos", 99) < 5:
    assert row.get("rewind_blocked") is True, row
if backup:
    state.write_text(backup)
else:
    state.unlink(missing_ok=True)

print("OK: validate-overnight-zero-spam-v1")
PY
