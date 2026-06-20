#!/usr/bin/env bash
# Mechanical Worker drain paste — from disk only (Goal 1 execution bridge).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

PROGRESS="$(python3 "$ROOT/scripts/goal-progress-v1.py" --json 2>/dev/null)"
PICK_ID="$(echo "$PROGRESS" | python3 -c "import sys,json; print(json.load(sys.stdin)['live_pick']['id'] or '—')")"
PICK_PATH="$(echo "$PROGRESS" | python3 -c "import sys,json; print(json.load(sys.stdin)['live_pick']['path'] or '')")"
PICK_STATUS="$(echo "$PROGRESS" | python3 -c "import sys,json; print(json.load(sys.stdin)['live_pick'].get('status') or 'backlog')")"
GOAL_PCT="$(echo "$PROGRESS" | python3 -c "import sys,json; g=json.load(sys.stdin)['goal_1']; print(f\"{g['done']}/{g['total']} ({g['pct']}%)\")")"
TURN_WARN=""
if python3 "$ROOT/scripts/worker_turn_lib.py" --check 2>/dev/null | python3 -c "import sys,json; d=json.load(sys.stdin); import sys as s; s.exit(0 if d.get('turn_blocked') or (d.get('turn') or {}).get('status')=='open' else 1)" 2>/dev/null; then
  TURN_WARN="WARN: worker turn OPEN — close prior turn before new gate session"
fi
STALE_WARN=""
if [[ "$PICK_STATUS" == "done" ]]; then
  STALE_WARN="WARN: pick 1 id ${PICK_ID} already done on REGISTRY — re-run goal-progress; do NOT re-implement"
fi

cat <<EOF
MANDATORY: os/chat-handoffs/MANDATORY_SOURCEA_WORKER_CHAT_LOCKED_v1.md
MANDATORY: os/chat-handoffs/REGISTRY_DRAIN_RAIL_LOCKED_v1.md §PICK ORDER
MANDATORY: os/chat-handoffs/GOAL_EXECUTION_ACTIVE_LOCKED_v1.md

DRAIN ROUND — ONE sa per turn · Goal 1 progress: ${GOAL_PCT}
REGISTRY TRUTH: trust bash scripts/plan-no-asf-run.sh pick 1 only (never cite stale sa-0076/sa-0078)
DRAIN_CHECK: OFF · NO batch closeout · FORBIDDEN: UNATTENDED BATCH / pick 30
${TURN_WARN}
${STALE_WARN}

1. VALIDATE FIRST
   bash scripts/worker_turn_entry_v1.sh
   bash scripts/plan-no-asf-run.sh pick 1  → must match ${PICK_ID}

2. ACT — ONLY ${PICK_PATH:-prompts/.../${PICK_ID}.md}

3. VERIFY
   cd scripts && bash worker_verify_ultra_v1.sh

4. CLOSEOUT — one id only: ${PICK_ID}
   REGISTRY done · SOURCEA-PRIORITY row · pack validate · session-close

5. WORKER_ROUND_REPORT YAML → STOP (do not pick again this turn)

Mechanical gate: closeout writes ~/.sina/worker_round_report_v1.json — next session blocked until closed.

FOUNDER LAW: Hub → Actions → Copy Worker drain — no Terminal (SINA_COMMAND_NO_TERMINAL_FOUNDER_LOCKED_v1.md)
EOF
