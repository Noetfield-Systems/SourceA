#!/usr/bin/env bash
# n8n_investigator_judge_tick_hook_v1.sh — external cron glue (observe only)
set -euo pipefail
cd "$(dirname "$0")/.."
ROOT="$(pwd)"
HUB="${SINA_COMMAND_HUB_URL:-http://127.0.0.1:13020}"

if [[ "${1:-}" == "--local" ]]; then
  python3 "${ROOT}/scripts/investigator_circle_run_v1.py" --json
  python3 "${ROOT}/scripts/judge_loop_room_v1.py" --json
  exit 0
fi

curl -sf -X POST "${HUB}/api/investigator-circle/tick/v1" \
  -H "Content-Type: application/json" \
  -d '{}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('investigator_line') or r.get('investigation_verdict'))"

curl -sf -X POST "${HUB}/api/judge-loop/tick/v1" \
  -H "Content-Type: application/json" \
  -d '{}' \
  | python3 -c "import sys,json; r=json.load(sys.stdin); print(r.get('judge_loop_line') or r.get('loop_verdict'))"
