#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

for f in \
  brain-os/law/enforcement/GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md \
  brain-os/law/BRAIN_UNIFIED_RULES_LOCKED_v1.md \
  .cursor/rules/000-brain-unified.mdc \
  scripts/goal1_auto_run_deliver_v1.py \
  scripts/worker_inject_lib.py \
  scripts/start_goal1_worker_turn_v1.py; do
  test -f "$f" || { echo "FAIL: missing $f"; exit 1; }
done

grep -q "INJECT" brain-os/law/enforcement/GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md
grep -q "VALIDATE" brain-os/law/enforcement/GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md
grep -q "ACTIVATE" brain-os/law/enforcement/GOAL1_LOOP_ACTIVATION_CHAIN_LOCKED_v1.md
grep -q "GOAL1_LOOP_ACTIVATION_CHAIN" brain-os/contract/MANDATORY_BRAIN_CHAT_LOCKED_v1.md
grep -q "LOOP ACTIVATION CHAIN" brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md

python3 <<'PY'
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path("scripts").resolve()))
state_path = Path.home() / ".sina" / "healthy-queue-state-v1.json"
try:
    from healthy_queue_ssot_lib import first_open_queue_pos

    pos = first_open_queue_pos()
except Exception:
    pos = 1
state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.is_file() else {}
state["next_pos"] = pos if pos <= 30 else 1
state_path.parent.mkdir(parents=True, exist_ok=True)
state_path.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
PY

python3 scripts/goal1_auto_run_deliver_v1.py --prepare-only --turns 1 --json | python3 -c "
import json, sys
d = json.load(sys.stdin)
assert d.get('ok'), d
assert d.get('inbox_pending') or d.get('step') == 'prepared', d
print('PASS: inject prepare path')
"

bash scripts/validate-goal1-brain-validation-v1.sh
bash scripts/validate-brain-run-loop-v1.sh

echo "OK: validate-goal1-auto-run-activation-chain-v1"
