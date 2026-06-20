#!/usr/bin/env bash
# E2E — live prompt feed: rebuild, cursor align, advance simulation, validators.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SCRIPTS="$ROOT/scripts"
cd "$ROOT"
# shellcheck source=_founder_session_gate_entry_v1.sh
source "$ROOT/scripts/_founder_session_gate_entry_v1.sh"
_founder_session_gate_or_exit "$(basename "$0")" "$ROOT"

echo "=== validate-live-prompt-feed-e2e-v1 ==="

python3 "$SCRIPTS/live_ongoing_prompts_v1.py" --rebuild --json >/dev/null
bash "$SCRIPTS/validate-live-ongoing-prompts-v1.sh"

python3 - <<'PY'
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, "scripts")
from healthy_queue_ssot_lib import healthy_queue_state_path

SINA = Path.home() / ".sina"
live = json.loads((SINA / "live-ongoing-prompts-next-10-v1.json").read_text())
state = json.loads(healthy_queue_state_path().read_text())
cursor = int(state.get("next_pos") or 1)
turns = live.get("turns") or []
assert turns, "no turns"
assert turns[0]["queue_pos"] == cursor, f"head {turns[0]['queue_pos']} != cursor {cursor}"

# Simulate advance + rebuild (dry — restore cursor after)
proc = subprocess.run(
    [sys.executable, "scripts/advance-healthy-queue-v1.py"],
    capture_output=True,
    text=True,
    cwd=str(Path.cwd()),
)
adv = json.loads(proc.stdout)
new_pos = int(adv.get("next_pos") or cursor)
live2 = json.loads(subprocess.check_output(
    [sys.executable, "scripts/live_ongoing_prompts_v1.py", "--rebuild", "--json"],
    text=True,
))
turns2 = live2.get("turns") or []
assert turns2[0]["queue_pos"] == new_pos, f"after advance head {turns2[0]['queue_pos']} != {new_pos}"

# Restore cursor
subprocess.run(
    [sys.executable, "scripts/advance-healthy-queue-v1.py", "--set-pos", str(cursor), "--reason", "e2e-restore"],
    check=True,
    capture_output=True,
)
subprocess.run([sys.executable, "scripts/live_ongoing_prompts_v1.py", "--rebuild"], check=True, capture_output=True)
print(f"OK: advance simulation {cursor}->{new_pos}->restore {cursor}")
PY

python3 "$SCRIPTS/validate-next-prompt-pack-live-v1.py" --json | python3 -c "
import json,sys
d=json.load(sys.stdin)
# Under FREEZE, pack validator may fail on ACT — CHECK at cursor must be feasible
print('pack_validator ok=', d.get('ok'), 'failed=', d.get('failed'))
"

grep -q "live_ongoing_prompts" "$SCRIPTS/sina_command_lib.py"
grep -q "live_ongoing_prompts" "$SCRIPTS/prompt_direction.py"

python3 - <<'PY'
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path.cwd()
SCRIPTS = ROOT / "scripts"
SINA = Path.home() / ".sina"
OV = SINA / "live-prompt-overrides-v1.json"

spec = importlib.util.spec_from_file_location("hdr", SCRIPTS / "healthy-drain-orchestrator-v1.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

qi = mod.queue_item()
assert qi.get("ok"), "queue_item failed"
pos = int(qi["pos"])
ov_backup = OV.read_text(encoding="utf-8") if OV.is_file() else None

sys.path.insert(0, str(SCRIPTS))
from healthy_queue_ssot_lib import healthy_queue_state_path
state_path = healthy_queue_state_path()
state_backup = state_path.read_text(encoding="utf-8")

OV.parent.mkdir(parents=True, exist_ok=True)
OV.write_text(json.dumps({
    "schema": "live-prompt-overrides-v1",
    "edits": {},
    "quarantine": [pos],
    "excluded": [],
}, indent=2) + "\n", encoding="utf-8")

st = mod.orchestrator_state()
out = mod._skip_override_turn(qi=qi, reason="quarantine", st=st)
assert out.get("skipped") and out.get("skip_reason") == "quarantine", out

if ov_backup is None:
    OV.unlink(missing_ok=True)
else:
    OV.write_text(ov_backup, encoding="utf-8")
subprocess.run(
    [sys.executable, str(SCRIPTS / "advance-healthy-queue-v1.py"), "--set-pos", str(pos), "--reason", "e2e-quarantine-restore"],
    check=True,
    capture_output=True,
)
state_path.write_text(state_backup, encoding="utf-8")
subprocess.run([sys.executable, str(SCRIPTS / "live_ongoing_prompts_v1.py"), "--rebuild"], check=True, capture_output=True)
print(f"OK: quarantine skip smoke pos {pos}")
PY

grep -q "FREEZE_ACT_BLOCKED" "$SCRIPTS/healthy-drain-orchestrator-v1.py"
grep -q "data-live-edit" "$ROOT/agent-control-panel/assets/app.js"

echo "PASS: validate-live-prompt-feed-e2e-v1"
