#!/usr/bin/env bash
# Healthy REGISTRY drain paste — one queue item, mandatory laws, check/act/verify rhythm.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

QUEUE_REPO="$ROOT/os/plan-library/sourcea-1000/prompts/healthy-queue-30-active.json"
QUEUE_HOME="$HOME/.sina/healthy-queue-30-active.json"
if [[ -f "$QUEUE_HOME" ]]; then
  QUEUE="$QUEUE_HOME"
else
  QUEUE="$QUEUE_REPO"
fi
STATE="$HOME/.sina/healthy-queue-state-v1.json"

python3 "$ROOT/scripts/generate-healthy-prompt-pack-v1.py" >/dev/null 2>&1 || true

python3 <<PY
import json
from pathlib import Path

root = Path("$ROOT")
queue_path = Path("$QUEUE")
state_path = Path("$STATE")

queue = json.loads(queue_path.read_text(encoding="utf-8"))
items = queue.get("queue") or []
if not items:
    raise SystemExit("FAIL: empty healthy queue")

pos = 1
if state_path.is_file():
    try:
        pos = int(json.loads(state_path.read_text()).get("next_pos") or 1)
    except (json.JSONDecodeError, ValueError, TypeError):
        pos = 1
if pos < 1 or pos > len(items):
    pos = 1

item = items[pos - 1]
progress = __import__("subprocess").run(
    ["python3", str(root / "scripts/goal-progress-v1.py"), "--json"],
    capture_output=True, text=True, cwd=str(root),
)
goal = json.loads(progress.stdout) if progress.returncode == 0 else {}

out = {
    "queue_pos": pos,
    "queue_total": len(items),
    "item": item,
    "goal_1": goal.get("goal_1"),
    "live_pick": goal.get("live_pick"),
}
print(json.dumps(out, indent=2))
PY

ITEM_JSON="$(python3 -c "
import json
from pathlib import Path
q=json.loads(Path('$QUEUE').read_text())
s=Path('$STATE')
pos=1
if s.is_file():
    try: pos=int(json.loads(s.read_text()).get('next_pos') or 1)
    except: pos=1
if pos<1 or pos>len(q['queue']): pos=1
print(json.dumps(q['queue'][pos-1]))
")"

POS="$(echo "$ITEM_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['queue_pos'])")"
TOTAL="$(python3 -c "import json; print(len(json.load(open('$QUEUE'))['queue']))")"
ROLE="$(echo "$ITEM_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['queue_role'])")"
SA="$(echo "$ITEM_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['sa_id'])")"
PATH_SA="$(echo "$ITEM_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin).get('sa_path') or '')")"
INSTR="$(echo "$ITEM_JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['instruction'])")"
VERIFY="$(echo "$ITEM_JSON" | python3 -c "
import sys,json
sys.path.insert(0,'$ROOT/scripts')
from worker_verify_normalize_v1 import normalize_worker_verify
raw=json.load(sys.stdin)['verify']
print(normalize_worker_verify(raw, role='verify'))
")"
CLOSEOUT="$(echo "$ITEM_JSON" | python3 -c "import sys,json; print('yes' if json.load(sys.stdin).get('closeout') else 'no')")"
GOAL_PCT="$(python3 "$ROOT/scripts/goal-progress-v1.py" --json 2>/dev/null | python3 -c "import sys,json; g=json.load(sys.stdin)['goal_1']; print(f\"{g['done']}/{g['total']} ({g['pct']}%)\")")"

cat <<EOF
LEGACY PASTE SCRIPT — SSOT for live turns: scripts/healthy_prompt_turn_v1.py (orchestrator INBOX)
MANDATORY: brain-os/law/enforcement/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md
MANDATORY: brain-os/law/enforcement/REGISTRY_DRAIN_RAIL_LOCKED_v1.md §PICK ORDER
MANDATORY: brain-os/system/GOAL_EXECUTION_ACTIVE_LOCKED_v1.md
MANDATORY: brain-os/plan-registry/sourcea-1000/HEALTHY_PROMPT_SEQUENCE_LOCKED_v1.md
MANDATORY: brain-os/plan-registry/sourcea-1000/REGISTRY_DRAIN_PROCESS_LOCKED_v1.md

HEALTHY DRAIN — queue ${POS}/${TOTAL} · role=${ROLE} · Goal 1: ${GOAL_PCT}
REGISTRY bind: ${SA} (trust pick 1 must match on VERIFY turns)
FORBIDDEN: UNATTENDED BATCH · pick 30 · multi-sa closeout

1. VALIDATE FIRST
   bash scripts/worker_turn_entry_v1.sh
   bash scripts/plan-no-asf-run.sh pick 1

2. THIS TURN — $(echo "$ROLE" | tr '[:lower:]' '[:upper:]') ONLY
   ${INSTR}
   Path: ${PATH_SA:-prompts/.../${SA}.md}

3. VERIFY
   ${VERIFY}

4. CLOSEOUT
   $(if [[ "$CLOSEOUT" == "yes" ]]; then echo "FULL closeout ${SA} · REGISTRY · PRIORITY · pack · WORKER_ROUND_REPORT → STOP"; else echo "NO closeout this turn (${ROLE} phase) · WORKER_ROUND_REPORT → STOP"; fi)

DELIVERY: Hub/autoloop writes .sina-loop/INBOX.md (editor tab, background) — NOT clipboard paste into Brain chat
After STOP: Hub → Advance healthy queue (or autoloop watch) → Worker chat: say run inbox
FOUNDER LAW: no Terminal — Hub clicks only (SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md)
EOF
